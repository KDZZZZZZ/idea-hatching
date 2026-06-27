#!/usr/bin/env bash
set -euo pipefail
MODE="periodic"
EVERY="30m"
UNINSTALL=0
STATUS=0
DRY_RUN=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode) MODE="$2"; shift 2 ;;
    --every) EVERY="$2"; shift 2 ;;
    --uninstall|--stop) UNINSTALL=1; shift ;;
    --status) STATUS=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CLAUDE_SKILL_DIR="$HOME/.claude/skills/idea-hatching"
HEARTBEAT="$SKILL_DIR/scripts/heartbeat.py"
command -v python3 >/dev/null || { echo "python3 is required" >&2; exit 1; }
if [[ "$STATUS" == 1 ]]; then python3 "$HEARTBEAT" --status; exit 0; fi
if [[ "$UNINSTALL" == 1 ]]; then python3 "$HEARTBEAT" --stop; echo "Disable/remove cron/launchd/systemd task manually if installed."; exit 0; fi
python3 "$SKILL_DIR/scripts/package.py" --sync >/dev/null
python3 "$SKILL_DIR/scripts/init_workspace.py" >/dev/null
python3 "$HEARTBEAT" --mode "$MODE" --every "$EVERY" --status >/dev/null
if [[ "$DRY_RUN" == 1 ]]; then echo "DRY RUN: would install Auto Hatch mode=$MODE every=$EVERY"; exit 0; fi
cat <<EOF
Installed skill files and heartbeat config.
Automatic OS scheduling is platform-specific:
- periodic: run: python3 "$HEARTBEAT" --once
- always:   run: python3 "$HEARTBEAT" --loop
Use cron/systemd/launchd to schedule these commands.
EOF
