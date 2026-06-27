# Idea Hatching

Idea Hatching is a Claude Code skill for capturing many ideas without letting them crowd your attention. Each idea is slowly advanced through a trustworthy pipeline:

```text
haiku research → buffer.md → main-agent adjudication → lib.md → [L#] citations → mind-model.md
```

It supports manual advancement and optional **Auto Hatch** heartbeat while your computer is on.

## Install

Clone or copy this folder, then install globally:

### Windows

```powershell
.\scripts\install.ps1 -Mode periodic -Every 30m
```

### macOS/Linux

```bash
./scripts/install.sh --mode periodic --every 30m
```

To only validate/copy without scheduler changes:

```bash
python scripts/package.py --check --sync
```

## Commands

```text
/idea-hatching hatch "<idea>"
/idea-hatching advance [slug]
/idea-hatching list
/idea-hatching show <slug>
/idea-hatching incubate --auto --mode periodic --every 30m
/idea-hatching incubate --auto --mode always --every 10m
/idea-hatching incubate --status
/idea-hatching incubate --stop
```

## Workspace

Runtime files live in `~/idea-hatching/`:

```text
INDEX.md
heartbeat.json
heartbeat.log
heartbeat.lock
<slug>/mind-model.md
<slug>/buffer.md
<slug>/lib.md
<slug>/journal.md
```

No `.omc/` state is used.

## Auto Hatch

- `periodic`: run one advance per interval.
- `always`: loop while the machine/session is on, with cooldown between advances.
- Single-flight lock prevents overlapping runs.
- Routine advances stay silent.
- Notify only on hatched, blocked, or setup/config errors.

`heartbeat.py` is a scheduler wrapper. It does not reason or directly modify idea files; it invokes `/idea-hatching advance` through Claude Code.

## Development

Validate structure:

```bash
python scripts/package.py --check
```

Sync repo copy to local Claude skills:

```bash
python scripts/package.py --sync
```
