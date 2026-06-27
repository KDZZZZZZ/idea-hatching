# Auto Hatch Heartbeat Rules

Auto Hatch is the machine-on automation layer for Idea Hatching. It does not reason by itself; it schedules `/idea-hatching advance`.

## Modes

### periodic
Wakes up at a time interval, runs one advance, then exits.

Example:
```text
/idea-hatching incubate --auto --mode periodic --every 30m
```

### always
Runs a resident loop while the machine/session is on:

```text
advance → cooldown → advance → cooldown → ...
```

Example:
```text
/idea-hatching incubate --auto --mode always --every 10m
```

## Single-flight
Only one heartbeat advance may run at a time. Use `heartbeat.lock`. If a lock exists and the process is alive, skip the tick. If stale, clear it.

## Silence contract
Notify only on:
- `hatched`
- `blocked`
- configuration/setup errors

Routine advances remain silent and are recorded in logs/journals only.

## Scheduler hosts

Preferred local hosts (installed via `scripts/heartbeat.py --install-scheduler` where supported):
- Windows: Task Scheduler via `scripts/install.ps1`
- macOS: launchd via `scripts/install.sh` (planned/basic)
- Linux: systemd user timer or cron via `scripts/install.sh` (planned/basic)

Claude Code `CronCreate` remains available for session-scoped `--cron`, but it is not durable across machine/session boundaries.

## Stop/status
`incubate --status` inspects config, lock, log, and OS scheduler state.
`incubate --stop` disables/removes Auto Hatch scheduler tasks and clears stale locks. It never deletes idea data.

## Heartbeat config
Runtime config lives at `~/idea-hatching/heartbeat.json`, seeded from `templates/heartbeat.json`.
