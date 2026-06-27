---
name: idea-hatching
description: Idea incubator — captures ideas, advances one idea at a time through a buffer→lib→mind-model workflow, and optionally runs Auto Hatch heartbeat while the computer is on.
triggers: ["idea hatching", "孵化灵感", "孵化器", "推进灵感", "hatch idea", "灵感孵化", "incubate idea", "auto hatch"]
argument-hint: "hatch \"<idea>\" | advance [<slug>] | list | show <slug> | incubate --auto --mode periodic|always --every <interval> | incubate --status | incubate --stop"
---

# Idea Hatching

Idea Hatching stores every idea globally, advances it in small trustworthy increments, and avoids flooding the user with half-baked plans. Install with `npx github:KDZZZZZZ/idea-hatching install`; installation does not enable Auto Mode. The durable workspace is `~/idea-hatching/`; it is global and independent of any project workspace.

## Core commands

- `hatch "<idea text>"` — capture an idea. Initialize the workspace if needed, create a slug directory, write `mind-model.md`, `buffer.md`, `lib.md`, `journal.md`, and update `INDEX.md`. Reply with one confirmation line only.
- `advance [<slug>]` — advance exactly one idea by one bounded round. If no slug is given, choose the least-recently advanced incubating idea.
- `list` / `status` — read `~/idea-hatching/INDEX.md` and show all ideas.
- `show <slug>` — show that idea's current `mind-model.md`.
- `incubate --cron "<spec>"` — optional Claude Code session-only cron; expires with the session / scheduled-task lifetime.
- `incubate --auto --mode periodic --every <interval>` — configure Auto Mode to wake on an interval and run one `advance`.
- `incubate --auto --mode always --every <interval>` — configure Auto Mode as a resident loop: `advance → cooldown → advance`.
- `incubate --status` — inspect heartbeat config, lock, log, and OS scheduler status.
- `incubate --stop` — stop Auto Hatch tasks and clear stale lock; never delete ideas.

## Read these references when needed

- `references/workflow.md` — full hatch/advance/list/show/incubate workflow.
- `references/mind_model_rules.md` — scoring, gates, token cap, 20-line delta rule, compression rules.
- `references/heartbeat_rules.md` — Auto Hatch modes, lock/log/silence contracts, scheduler behavior.

## Scripts

Use scripts through `${CLAUDE_SKILL_DIR}/scripts/...` when deterministic filesystem or scheduler work is needed.

- `scripts/init_workspace.py` initializes `~/idea-hatching/` and can hatch one idea without LLM reasoning.
- `scripts/heartbeat.py` implements Auto Hatch heartbeat: `--enable`, `--install-scheduler`, `--once`, `--loop`, `--status`, `--stop`, `--dry-run`.
- `scripts/install.ps1` installs/syncs the skill on Windows; Auto Mode is configured separately through `heartbeat.py`.
- `scripts/install.sh` installs/syncs the skill on macOS/Linux; Auto Mode is configured separately through `heartbeat.py`.
- `scripts/package.py` validates the skill structure and can sync files.

## Advance invariant summary

The evidence flow is one-way:

```text
haiku research → buffer.md candidates → main agent accepts → lib.md evidence → [L#] citations → mind-model.md
```

The haiku subagent may write only `buffer.md`. The main agent alone changes `lib.md` and `mind-model.md`.

Each `advance`:
1. evaluates feasibility and credibility;
2. finds the first failing gate;
3. fills or reuses the buffer;
4. accepts at most 2–3 lib entries;
5. changes at most one mind-model section by ≤20 net lines;
6. appends journal and refreshes INDEX;
7. stops.

Only proactively notify the user on: one-line hatch confirmation, one-line pre-hatch advance status, `hatched`, `blocked`, or Auto Hatch configuration errors.
