#!/usr/bin/env bash
set -euo pipefail
STATUS=0
DRY_RUN=0
while [[ $# -gt 0 ]]; do
  case "$1" in
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
if [[ "$DRY_RUN" == 1 ]]; then echo "DRY RUN: would install/sync the skill and initialize ~/idea-hatching. Auto Mode would remain unchanged."; exit 0; fi
"$PYTHON_BIN" "$SKILL_DIR/scripts/package.py" --sync >/dev/null
"$PYTHON_BIN" "$SKILL_DIR/scripts/init_workspace.py" >/dev/null
echo "Installed Idea Hatching skill and initialized workspace. Auto Mode is unchanged."
