# Idea Hatching / idea孵化器

> A low-noise Claude Code skill for people with too many ideas.

Most AI tools rush to generate plans. Idea Hatching does the opposite: it captures every idea, develops it slowly with evidence, and only surfaces a complete plan when it becomes feasible and credible.

It is for people who:

- have many side project, paper, product, or research ideas competing for attention;
- do not want every spark to immediately become a noisy pile of half-baked plans;
- want Claude to keep advancing ideas in small background steps instead of expanding everything at once;
- want each idea to grow into a credible mind model, evidence library, and landing path.

Idea Hatching is not an idea manager. It is an idea incubator.

It is not about generating plans faster. It is about developing ideas more slowly, quietly, and credibly.

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

Install with one command. This copies the skill into the default Claude Code global skill directory and initializes `~/idea-hatching/`. It does **not** enable Auto Mode.

```bash
npx github:KDZZZZZZ/idea-hatching install
```

Behavior:

- Installs the skill to `~/.claude/skills/idea-hatching/`.
- Creates `~/idea-hatching/INDEX.md` if missing.
- Creates `~/idea-hatching/heartbeat.json` if missing.
- Leaves Auto Mode off.

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

Auto Mode uses a lock file to prevent overlapping runs.

### Periodic mode

Periodic mode means: **wake up at a time interval, run exactly one `advance`, then exit**.

```text
/idea-hatching incubate --auto --mode periodic --every 30m
```

Behavior:

- Creates/updates the heartbeat config.
- On Windows, this sets up a Task Scheduler task named `IdeaHatchingPeriodic`.
- Each tick runs one `advance`.
- If another advance is already running, the tick exits quietly.
- It does not keep a resident loop alive between ticks.

### Always mode

Always mode means: **start one resident loop while the machine/session is on**.

```text
/idea-hatching incubate --auto --mode always --every 10m
```

Behavior:

- On Windows, this sets up a login-started Task Scheduler task for the loop.
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

Behavior:

- Shows heartbeat config.
- Shows whether a lock exists.
- Shows the heartbeat log path.
- Shows the resolved Claude Code CLI command when available.
- Prints the last few heartbeat log lines.

### Stop Auto Mode

```text
/idea-hatching incubate --stop
```

Behavior:

- Disables heartbeat config.
- Removes scheduler tasks where supported.
- Clears stale locks.
- Keeps all ideas, logs, and evidence files.

---

## Development

For maintainers only:

```bash
python scripts/heartbeat.py --check
```

Checks whether the local Claude Code CLI can be resolved and can complete a live `claude -p` probe.



```bash
python scripts/package.py --check
```
