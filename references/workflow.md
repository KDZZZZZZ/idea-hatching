# Idea Hatching Workflow

## Workspace

Runtime workspace: `~/idea-hatching/`

```text
~/idea-hatching/
  INDEX.md
  heartbeat.json
  heartbeat.lock
  heartbeat.log
  <slug>/
    mind-model.md
    buffer.md
    lib.md
    journal.md
```

## Hatch

`hatch "<idea>"` must:
1. initialize the workspace if needed;
2. detect idea language;
3. generate a unique kebab-case slug;
4. create the idea directory;
5. write `mind-model.md`, `buffer.md`, `lib.md`, `journal.md` from templates;
6. update `INDEX.md`;
7. reply with one line only.

Use `scripts/init_workspace.py --hatch "<idea>"` for deterministic file creation when possible.

## Advance

`advance [<slug>]` runs exactly one round and stops.

### Selection
- Explicit slug: use it.
- No slug: choose `status: incubating` with the earliest `last_advanced`.

### Evaluation
Read `mind-model.md` and `lib.md`. Score:
- `feasibility`: cost vs benefit.
- `credibility`: evidence coverage + referenceability.

Find the first failing gate:
1. Is the motivation meaningful?
2. Would the implemented result achieve the motivation?
3. Are all costs and the implementation path genuinely necessary?

### Buffer fill
If `buffer.md` has usable deferred/pending candidates for the current gate, skip subagent work.
Otherwise dispatch a haiku subagent to write only `buffer.md`. Candidate types:
- `corroborate`
- `refine`
- `supplement`
- `branch`
- `contradiction`

### Main-agent integration
The main agent adjudicates buffer entries:
- accepted → `lib.md` as new `L#` entries;
- deferred → remains in `buffer.md`;
- dropped → removed with a one-line journal reason.

Then the main agent applies one mind-model edit only, from `lib.md` citations.

### Wrap-up
Update frontmatter metrics and `last_advanced`, append `journal.md`, refresh `INDEX.md`, and stop.

## Hatch check
If `feasibility >= 3` and `credibility >= 3`, set `status: hatched`, append journal, refresh INDEX, and present the complete plan.

## Block check
If a contradiction is fatal, set `status: blocked`, append journal, refresh INDEX, and proactively give one concise explanation.

## List/status
Read `INDEX.md` and display ideas. Add one suggestion for the least-recently advanced incubating idea.

## Show
Print `mind-model.md` for the requested slug. This is allowed to show work-in-progress because the user explicitly asked.

## Incubate
- `--cron`: use Claude Code scheduled task for session-scoped recurrence.
- `--auto`: use the heartbeat scripts and OS scheduler where available.
