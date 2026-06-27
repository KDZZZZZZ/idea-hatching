#!/usr/bin/env bash
set -euo pipefail
AUTO=0
MODE="periodic"
EVERY="30m"
UNINSTALL=0
STATUS=0
DRY_RUN=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --auto) AUTO=1; shift ;;
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
HEARTBEAT="$SKILL_DIR/scripts/heartbeat.py"
PYTHON_BIN=""
for candidate in python3 python; do
  if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c "import sys" >/dev/null 2>&1; then
    PYTHON_BIN="$candidate"
    break
  fi
done
if [[ -z "$PYTHON_BIN" ]]; then echo "python 3 is required" >&2; exit 1; fi
if [[ "$STATUS" == 1 ]]; then "$PYTHON_BIN" "$HEARTBEAT" --status; exit 0; fi
if [[ "$UNINSTALL" == 1 ]]; then "$PYTHON_BIN" "$HEARTBEAT" --stop; echo "Disable/remove cron/launchd/systemd task manually if installed."; exit 0; fi
if [[ "$DRY_RUN" == 1 ]]; then
  if [[ "$AUTO" == 1 ]]; then echo "DRY RUN: would enable Auto Hatch mode=$MODE every=$EVERY";
  else echo "DRY RUN: would install/sync the skill and initialize ~/idea-hatching only. Auto Mode would remain off."; fi
  exit 0
fi
"$PYTHON_BIN" "$SKILL_DIR/scripts/package.py" --sync >/dev/null
"$PYTHON_BIN" "$SKILL_DIR/scripts/init_workspace.py" >/dev/null
if [[ "$AUTO" == 0 ]]; then echo "Installed Idea Hatching skill and initialized workspace. Auto Mode is off."; exit 0; fi
"$PYTHON_BIN" "$HEARTBEAT" --mode "$MODE" --every "$EVERY" --status >/dev/null
cat <<EOF
Configured Auto Hatch mode=$MODE every=$EVERY.
Automatic OS scheduling is platform-specific:
- periodic: run: "$PYTHON_BIN" "$HEARTBEAT" --once
- always:   run: "$PYTHON_BIN" "$HEARTBEAT" --loop
Use cron/systemd/launchd to schedule these commands.
EOF
