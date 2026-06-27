#!/usr/bin/env python3
"""Auto Hatch heartbeat for Idea Hatching.

This scheduler wrapper does not reason or edit idea files directly. It invokes an
advance command, enforces single-flight, and records a runtime log.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import shlex
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path.home() / "idea-hatching"
DEFAULT_CONFIG = ROOT / "heartbeat.json"


def expand(v: str) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(v)))


def parse_interval(value: str) -> int:
    s = value.strip().lower()
    if s.isdigit():
        return int(s)
    unit = s[-1]
    n = int(s[:-1])
    if unit == "s":
        return n
    if unit == "m":
        return n * 60
    if unit == "h":
        return n * 3600
    if unit == "d":
        return n * 86400
    raise ValueError(f"Unsupported interval: {value}")


def load_config(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {
        "enabled": False,
        "mode": "periodic",
        "every": "30m",
        "workspace": str(ROOT),
        "logFile": str(ROOT / "heartbeat.log"),
        "lockFile": str(ROOT / "heartbeat.lock"),
        "notify": {"hatched": True, "blocked": True, "configError": True, "routineAdvance": False},
        "singleFlight": True,
    }


def save_config(path: Path, cfg: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def log(cfg: dict, msg: str) -> None:
    log_file = expand(cfg.get("logFile", str(ROOT / "heartbeat.log")))
    log_file.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().isoformat(timespec="seconds")
    with log_file.open("a", encoding="utf-8") as f:
        f.write(f"[{stamp}] {msg}\n")


def pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        if platform.system().lower().startswith("win"):
            result = subprocess.run(["tasklist", "/FI", f"PID eq {pid}"], capture_output=True, text=True, timeout=10)
            return str(pid) in result.stdout
        os.kill(pid, 0)
        return True
    except Exception:
        return False


def acquire_lock(cfg: dict) -> bool:
    lock = expand(cfg.get("lockFile", str(ROOT / "heartbeat.lock")))
    lock.parent.mkdir(parents=True, exist_ok=True)
    if lock.exists():
        try:
            pid = int(lock.read_text(encoding="utf-8").strip().split()[0])
        except Exception:
            pid = -1
        if pid_alive(pid):
            log(cfg, f"skip: lock held by pid {pid}")
            return False
        lock.unlink(missing_ok=True)
        log(cfg, "cleared stale lock")
    lock.write_text(f"{os.getpid()} {datetime.now().isoformat()}\n", encoding="utf-8")
    return True


def release_lock(cfg: dict) -> None:
    lock = expand(cfg.get("lockFile", str(ROOT / "heartbeat.lock")))
    try:
        if lock.exists() and lock.read_text(encoding="utf-8").startswith(str(os.getpid())):
            lock.unlink()
    except Exception:
        pass


def default_advance_command() -> list[str]:
    env = os.environ.get("IDEA_HATCHING_ADVANCE_COMMAND")
    if env:
        return shlex.split(env)
    # Claude Code print mode. Users may override with IDEA_HATCHING_ADVANCE_COMMAND.
    return ["claude", "-p", "/idea-hatching advance"]


def run_once(cfg: dict, dry_run: bool = False) -> int:
    if cfg.get("singleFlight", True) and not acquire_lock(cfg):
        return 0
    try:
        cmd = default_advance_command()
        if dry_run:
            log(cfg, "dry-run: would execute " + " ".join(shlex.quote(x) for x in cmd))
            print("DRY_RUN " + " ".join(shlex.quote(x) for x in cmd))
            return 0
        log(cfg, "tick: executing advance")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=parse_interval(cfg.get("timeout", "30m")))
        out = (result.stdout or "") + (result.stderr or "")
        log(cfg, f"advance exit={result.returncode} output={out.strip()[:1000]}")
        if result.returncode != 0:
            print(out.strip())
        return result.returncode
    except Exception as e:
        log(cfg, f"config/runtime error: {e}")
        print(f"Auto Hatch error: {e}", file=sys.stderr)
        return 2
    finally:
        release_lock(cfg)


def status(cfg: dict) -> int:
    lock = expand(cfg.get("lockFile", str(ROOT / "heartbeat.lock")))
    log_file = expand(cfg.get("logFile", str(ROOT / "heartbeat.log")))
    print(json.dumps({
        "enabled": cfg.get("enabled"),
        "mode": cfg.get("mode"),
        "every": cfg.get("every"),
        "workspace": cfg.get("workspace"),
        "lockExists": lock.exists(),
        "logFile": str(log_file),
    }, ensure_ascii=False, indent=2))
    if log_file.exists():
        lines = log_file.read_text(encoding="utf-8", errors="replace").splitlines()[-5:]
        if lines:
            print("--- recent log ---")
            print("\n".join(lines))
    return 0


def stop(cfg: dict, config_path: Path) -> int:
    cfg["enabled"] = False
    save_config(config_path, cfg)
    lock = expand(cfg.get("lockFile", str(ROOT / "heartbeat.lock")))
    if lock.exists():
        try:
            pid = int(lock.read_text(encoding="utf-8").strip().split()[0])
        except Exception:
            pid = -1
        if not pid_alive(pid):
            lock.unlink(missing_ok=True)
            log(cfg, "stop: cleared stale lock")
    print("Auto Hatch disabled in heartbeat.json and scheduler tasks removed where supported.")
    return 0


def current_python() -> str:
    return sys.executable or "python"


def install_scheduler(cfg: dict, config_path: Path, dry_run: bool = False) -> int:
    """Install local OS scheduler tasks for Auto Mode where supported."""
    system = platform.system().lower()
    mode = cfg.get("mode", "periodic")
    every = cfg.get("every", "30m")
    script = Path(__file__).resolve()
    py = current_python()
    if dry_run:
        print(f"DRY_RUN install scheduler mode={mode} every={every}")
        return 0
    if system.startswith("win"):
        uninstall_scheduler(cfg, dry_run=False, quiet=True)
        if mode == "periodic":
            minutes = interval_to_minutes(every)
            cmd = [
                "schtasks", "/Create", "/TN", "IdeaHatchingPeriodic",
                "/SC", "MINUTE", "/MO", str(minutes),
                "/TR", f'"{py}" "{script}" --once', "/F",
            ]
            subprocess.run(cmd, check=True)
            print(f"Installed IdeaHatchingPeriodic every {every}.")
        elif mode == "always":
            cmd = [
                "schtasks", "/Create", "/TN", "IdeaHatchingAlways",
                "/SC", "ONLOGON", "/TR", f'"{py}" "{script}" --loop', "/F",
            ]
            subprocess.run(cmd, check=True)
            print(f"Installed IdeaHatchingAlways on logon with cooldown {every}.")
        else:
            raise ValueError(f"Unsupported mode: {mode}")
        return 0
    print("OS scheduler auto-install is not implemented for this platform. Use cron/systemd/launchd to run heartbeat.py --once or --loop.")
    return 0


def interval_to_minutes(value: str) -> int:
    seconds = parse_interval(value)
    if seconds < 60:
        raise ValueError("Windows Task Scheduler periodic mode requires at least 1 minute")
    return max(1, seconds // 60)


def uninstall_scheduler(cfg: dict, dry_run: bool = False, quiet: bool = False) -> int:
    system = platform.system().lower()
    if dry_run:
        print("DRY_RUN uninstall scheduler")
        return 0
    if system.startswith("win"):
        for name in ["IdeaHatchingPeriodic", "IdeaHatchingAlways"]:
            subprocess.run(["schtasks", "/Delete", "/TN", name, "/F"], capture_output=True, text=True)
        if not quiet:
            print("Removed Auto Hatch Windows scheduler tasks if present.")
        return 0
    if not quiet:
        print("Remove cron/systemd/launchd tasks manually if configured.")
    return 0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--config", default=str(DEFAULT_CONFIG))
    p.add_argument("--mode", choices=["periodic", "always"])
    p.add_argument("--every")
    p.add_argument("--once", action="store_true")
    p.add_argument("--loop", action="store_true")
    p.add_argument("--status", action="store_true")
    p.add_argument("--enable", action="store_true")
    p.add_argument("--install-scheduler", action="store_true")
    p.add_argument("--uninstall-scheduler", action="store_true")
    p.add_argument("--stop", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    config_path = expand(args.config)
    cfg = load_config(config_path)
    if args.mode:
        cfg["mode"] = args.mode
    if args.every:
        cfg["every"] = args.every
    if args.enable or args.install_scheduler:
        cfg["enabled"] = True
    if not args.dry_run:
        save_config(config_path, cfg)

    if args.status:
        return status(cfg)
    if args.install_scheduler:
        return install_scheduler(cfg, config_path, args.dry_run)
    if args.uninstall_scheduler:
        return uninstall_scheduler(cfg, args.dry_run)
    if args.stop:
        uninstall_scheduler(cfg, args.dry_run, quiet=True)
        return stop(cfg, config_path)
    if args.once:
        return run_once(cfg, args.dry_run)
    if args.loop:
        cfg["enabled"] = True
        save_config(config_path, cfg)
        log(cfg, f"loop start every={cfg.get('every')}")
        try:
            while load_config(config_path).get("enabled", False):
                run_once(load_config(config_path), args.dry_run)
                time.sleep(parse_interval(load_config(config_path).get("every", "30m")))
        except KeyboardInterrupt:
            log(cfg, "loop stopped by KeyboardInterrupt")
        return 0
    return status(cfg)

if __name__ == "__main__":
    raise SystemExit(main())
