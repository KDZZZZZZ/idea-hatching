#!/usr/bin/env python3
"""Validate/package the Idea Hatching skill."""
from __future__ import annotations

import argparse
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "SKILL.md",
    "references/workflow.md",
    "references/mind_model_rules.md",
    "references/heartbeat_rules.md",
    "scripts/init_workspace.py",
    "scripts/heartbeat.py",
    "scripts/install.ps1",
    "scripts/install.sh",
    "scripts/package.py",
    "templates/lib.md",
    "templates/mind_model.md",
    "templates/log.md",
    "templates/heartbeat.json",
    "README.md",
]


def check() -> int:
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    if missing:
        for p in missing:
            print(f"missing: {p}", file=sys.stderr)
        return 1
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    if not skill.startswith("---") or "name: idea-hatching" not in skill or "description:" not in skill:
        print("SKILL.md frontmatter is invalid", file=sys.stderr)
        return 1
    print("OK: structure valid")
    return 0


def sync() -> int:
    dest = Path.home() / ".claude" / "skills" / "idea-hatching"
    dest.mkdir(parents=True, exist_ok=True)
    for item in ROOT.iterdir():
        if item.name == ".git":
            continue
        target = dest / item.name
        if item.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)
    print(f"synced to {dest}")
    return 0


def zip_package(out: Path) -> int:
    if check() != 0:
        return 1
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in ROOT.rglob("*"):
            if ".git" in p.parts or p.is_dir():
                continue
            z.write(p, p.relative_to(ROOT).as_posix())
    print(f"wrote {out}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    p.add_argument("--sync", action="store_true")
    p.add_argument("--zip")
    args = p.parse_args()
    if args.sync:
        rc = sync()
        if rc:
            return rc
    if args.zip:
        return zip_package(Path(args.zip))
    return check()

if __name__ == "__main__":
    raise SystemExit(main())
