# Idea Hatching

Idea Hatching is a Claude Code skill for capturing many ideas without letting them crowd your attention. It stores ideas globally, advances them in small bounded steps, and only surfaces a complete plan when the idea is both feasible and credible.

The runtime workspace is:

```text
~/idea-hatching/
```

---

## Core logic

Each idea is stored as a folder:

```text
~/idea-hatching/<slug>/
  mind-model.md   # the clean deliverable
  buffer.md       # candidate edits from the haiku subagent
  lib.md          # accepted evidence and reasoning, cited as [L#]
  journal.md      # append-only iteration log
```

The evidence flow is one-way:

```text
haiku research → buffer.md → main-agent adjudication → lib.md → [L#] citations → mind-model.md
```

Rules:

- The haiku subagent may only write `buffer.md`.
- The main agent alone decides what enters `lib.md` and `mind-model.md`.
- `mind-model.md` may cite only `lib.md`.
- Every non-obvious judgment in `mind-model.md` should have an `[L#]` citation.
- Each `advance` changes at most one section of `mind-model.md` by at most 20 net lines.
- The default `mind-model.md` body cap is <3000 tokens.
- If the cap is reached, the next advance must compress before adding: cut filler, use sharper principles, cite details instead of inlining them, de-duplicate, and fold new content into existing statements.

The skill evaluates two metrics:

| Metric | Meaning |
|---|---|
| feasibility | cost vs benefit |
| credibility | evidence coverage + referenceability, not source prestige |

Evaluation follows three gates in order:

1. Is the motivation meaningful?
2. Would the implemented result achieve that motivation?
3. Are the cost and implementation path necessary to get that result?

An idea hatches only when:

```text
feasibility >= 3 and credibility >= 3
```

Before that, normal advances return only a one-line status.

---

## Installation

Installation copies the skill files into your global Claude Code skill directory and initializes `~/idea-hatching/` if needed. It does **not** turn on Auto Mode by itself.

### Windows

```powershell
cd path\to\idea-hatching
.\scripts\install.ps1 -DryRun
.\scripts\install.ps1
```

### macOS / Linux

```bash
cd path/to/idea-hatching
./scripts/install.sh --dry-run
./scripts/install.sh
```

### Manual sync for development

```bash
python scripts/package.py --check
python scripts/package.py --sync
```

Behavior:

- `--check` validates the expected file structure.
- `--sync` copies the repo version into `~/.claude/skills/idea-hatching/`.
- Install commands also create `~/idea-hatching/INDEX.md` and `~/idea-hatching/heartbeat.json` if missing.

---

## Manual usage

### Capture an idea

```text
/idea-hatching hatch "<idea>"
```

Behavior:

- Detects the idea language.
- Creates a unique slug.
- Creates `mind-model.md`, `buffer.md`, `lib.md`, and `journal.md`.
- Adds the idea to `INDEX.md`.
- Replies with one confirmation line only.

Example:

```text
/idea-hatching hatch "用 LLM 自动给会议纪要打结构化标签"
```

### Advance one idea one step

```text
/idea-hatching advance
```

or:

```text
/idea-hatching advance <slug>
```

Behavior:

- Without a slug, chooses the least-recently advanced incubating idea.
- Evaluates feasibility and credibility.
- Finds the first failing gate.
- Reuses `buffer.md` if it already contains suitable candidates.
- Otherwise sends a haiku subagent to write candidates into `buffer.md`.
- Main agent accepts useful candidates into `lib.md`.
- Main agent edits one section of `mind-model.md` using `[L#]` citations.
- Updates `journal.md` and `INDEX.md`.
- Stops after one round.
- If still incubating, returns one status line only.

### List ideas

```text
/idea-hatching list
```

or:

```text
/idea-hatching status
```

Behavior:

- Reads `~/idea-hatching/INDEX.md`.
- Shows each idea's slug, status, feasibility, credibility, last advanced date, and one-liner.
- Suggests the next idea to advance.

### Show one idea

```text
/idea-hatching show <slug>
```

Behavior:

- Prints that idea's current `mind-model.md`.
- This is allowed to reveal work-in-progress because the user explicitly requested it.

---

## Auto Mode

Auto Mode is optional. It is separate from installation.

Auto Mode runs while your machine and scheduler are available. It does not reason or edit idea files directly; it only invokes:

```text
/idea-hatching advance
```

Routine advances stay silent. Notifications are reserved for:

- an idea becoming `hatched`,
- an idea becoming `blocked`,
- configuration or runtime errors.

Auto Mode uses a lock file to prevent overlapping runs.

### Periodic mode

Periodic mode means: **wake up at a time interval, run exactly one `advance`, then exit**.

```text
/idea-hatching incubate --auto --mode periodic --every 30m
```

Script equivalent:

```bash
python scripts/heartbeat.py --enable --mode periodic --every 30m
python scripts/heartbeat.py --install-scheduler
```

Behavior:

- Creates/updates the heartbeat config.
- On Windows, `--install-scheduler` installs a Task Scheduler task named `IdeaHatchingPeriodic`.
- Each tick runs one `advance`.
- If another advance is already running, the tick exits quietly.
- It does not keep a resident loop alive between ticks.

### Always mode

Always mode means: **start one resident loop while the machine/session is on**.

```text
/idea-hatching incubate --auto --mode always --every 10m
```

Script equivalent:

```bash
python scripts/heartbeat.py --enable --mode always --every 10m
python scripts/heartbeat.py --install-scheduler
```

Behavior:

- On Windows, `--install-scheduler` starts the loop on login through Task Scheduler.
- Runs this loop:

```text
advance → cooldown → advance → cooldown → ...
```

- `--every` is the cooldown between two advances.
- Still runs only one bounded `advance` per cycle.
- Still uses the lock file to avoid overlap.

### Auto Mode status

```text
/idea-hatching incubate --status
```

Script equivalent:

```bash
python scripts/heartbeat.py --status
```

Behavior:

- Shows heartbeat config.
- Shows whether a lock exists.
- Shows the heartbeat log path.
- Prints the last few heartbeat log lines.

### Stop Auto Mode

```text
/idea-hatching incubate --stop
```

Script equivalent:

```bash
python scripts/heartbeat.py --stop
```

Behavior:

- Disables heartbeat config.
- Removes scheduler tasks where supported.
- Clears stale locks.
- Keeps all ideas, logs, and evidence files.

---

## Scripts

### `scripts/init_workspace.py`

```bash
python scripts/init_workspace.py
python scripts/init_workspace.py --hatch "<idea>"
```

Creates the workspace and, optionally, captures one idea without LLM reasoning.

### `scripts/heartbeat.py`

```bash
python scripts/heartbeat.py --once
python scripts/heartbeat.py --loop
python scripts/heartbeat.py --enable --mode periodic --every 30m
python scripts/heartbeat.py --install-scheduler
python scripts/heartbeat.py --status
python scripts/heartbeat.py --stop
python scripts/heartbeat.py --once --dry-run
```

Runs or inspects the Auto Mode heartbeat.

### `scripts/package.py`

```bash
python scripts/package.py --check
python scripts/package.py --sync
python scripts/package.py --zip idea-hatching.zip
```

Validates, syncs, or packages the skill.

---

## Development checks

```bash
python scripts/package.py --check
python scripts/heartbeat.py --once --dry-run
```
