---
name: idea-hatching
description: Idea incubator — safely captures every idea and advances one of them in a single bounded increment per call, hatching it into a trustworthy plan only when it is both feasible and credible. Keeps churn out of the deliverable so it never floods you with half-baked plans.
triggers: ["idea hatching", "孵化灵感", "孵化器", "推进灵感", "hatch idea", "灵感孵化", "incubate idea"]
argument-hint: "hatch \"<idea>\" | advance [<slug>] | list | show <slug> | incubate [--cron \"<spec>\"]"
---

# Idea Hatching

## Why this exists

You have many ideas, and the sheer volume is itself a burden: they fragment, get lost, and stall at "not-yet-explored," crowding out deep thinking. The goal here is **not to produce a quick plan**. It is to make sure every idea is **safely stored and advanced continuously but with restraint**, until it becomes a **trustworthy, maximum-effort plan** — and only then does it interrupt you.

Core tension: **keep advancing ↔ minimize cognitive load**. Every rule serves: nothing lost, always advancing, small change per step, deliverable short and clean, **churn sinks into a log instead of being dumped on the user**.

Metaphor: an idea is an egg 🥚 → `mind-model` is the developing embryo → once both "feasible" and "credible" pass, it **hatches** into a trustworthy plan.

## Storage

Global, **not tied to OMC, never under `.omc/`, no scripts**. Library root: `~/idea-hatching/`

```
~/idea-hatching/
  INDEX.md                 # catalog: slug · status · feasibility · credibility · last advanced
  <slug>/
    mind-model.md          # the only deliverable. frontmatter + 3 body sections. capped length, cites lib only
    buffer.md              # buffer module: candidate edits a haiku subagent writes after research; main agent drains it
    lib.md                 # evidence store L1,L2… each = source + content + use (only entries the main agent accepted)
    journal.md             # append-only iteration log (churn sinks here; never enters mind-model or reaches the user)
```

Before any operation: if `~/idea-hatching/` or `INDEX.md` is missing, create it (seed `INDEX.md` from the template). File templates live in `references/templates.md`.

## Language

Each idea's **body text follows the language it was captured in** (detected per idea), recorded in frontmatter `lang`. All later writes for that idea use that language. (This skill's own instructions are in English; the artifacts are not.)

---

## Commands

Invoked as `/idea-hatching <subcommand> ...`. With no argument, default to `list`.

### `hatch "<idea text>"` — capture (low-friction; this is the foundation of "nothing lost")
1. Detect the language from the text → `lang`; generate a short kebab-case `slug` (keyword/transliteration, unique; on collision append `-2`).
2. Create `~/idea-hatching/<slug>/` and write from templates:
   - `mind-model.md`: frontmatter (`status: incubating`, `feasibility: 0`, `credibility: 0`, `lang`, `created`, `last_advanced: 0000-00-00`) + the **3-section skeleton** (Motivation / Intuitive Essence / Path Spectrum), each holding one placeholder claim derived from the raw text, **marked unsupported** (no `[L#]` yet).
   - `buffer.md`: empty buffer (header only).
   - `lib.md`: empty store (header only).
   - `journal.md`: first entry `hatched-in`, recording the raw text.
3. Add one row to `INDEX.md`.
4. **Reply with a single confirmation line**, e.g. `🥚 hatched <slug> (incubating · F0 C0).` Expand no plan.

### `advance [<slug>]` — advance one round (the core engine, below)
Run **exactly one round**, then **stop**. With no slug, pick by the selection rule.

### `list` / `status` — overview
Read `INDEX.md`; show a table of all ideas: slug · status · F · C · last advanced. Add one suggestion line (e.g. "`<slug>` is least-recently advanced; consider advance").

### `show <slug>` — view
Print the idea's current `mind-model.md` in full. (One of the few places a work-in-progress may be shown, because the user **explicitly** asked.)

### `incubate [--cron "<spec>"]` — optional: silent scheduled advancing
Off by default. When enabled, use the harness **CronCreate** to schedule `advance` (picking the least-recently-advanced idea), with prompt `/idea-hatching advance`.
**Silence contract**: scheduled runs notify (via PushNotification, one line) **only** when an idea becomes `hatched` or `blocked` (fatal contradiction); all other rounds stay silent (still write files, no notification). Remind the user that cron expires after 7 days.

---

## Advance Engine

`advance` runs exactly the round below, then **stops**. One idea, one spot, per call.

### Orchestration: main agent + haiku subagent
The cheap "research + drafting" is delegated to a **haiku subagent**; the expensive "judge + integrate + evaluate" stays with the main agent. Pipeline:
**research → buffer (candidates, written by haiku) → main agent selects → lib (accepted) → cited → mind-model (clean deliverable)**.
- Subagent: use the **Agent tool**, `model: haiku`, a file-writing type (e.g. `executor` or `general-purpose`). Its job is strictly to research and write candidate edits into `buffer.md`. It **must not touch `mind-model.md` / `lib.md`**.
- Main agent: read the buffer, **select into lib, edit mind-model from lib, evaluate one round, drain the buffer**. All judgment stays with the main agent.

### 1 · Select the idea
- Slug given → use it.
- Otherwise → among `status: incubating`, pick the one with the **earliest `last_advanced`** (fair rotation, so every idea is advanced and none is lost). If no incubating idea exists, report and stop.

### 2 · Evaluate two metrics (walk the gates to find the first one that fails)
Read `mind-model.md` + `lib.md`. Two yardsticks:

- **feasibility = cost vs. benefit**
- **credibility = coverage + referenceability of the evidence** (**not** whether the source is authoritative — but: are the key judgments covered by lib, and are those grounds specific enough to be reused/referenced)

Evaluate **in this gate order** and locate the **first** failing gate — it decides what this round does:
1. **Is the motivation meaningful?** (is it worth doing at all)
2. **Would the implemented result achieve the motivation?** (does building it actually solve the motivation)
3. **Are all costs and the implementation path genuinely necessary to obtain that result?** (any waste / over-engineering)

Score each 0–3, record in frontmatter:

| score | feasibility | credibility |
|---|---|---|
| 0 | not assessed | mostly assumption, unsupported |
| 1 | benefit unclear, or cost clearly too high | only isolated points grounded, big gaps |
| 2 | net-positive but major uncertainty | main judgments grounded, minor gaps |
| 3 | net-positive, uncertainty bounded, path necessary & sufficient | motivation / result-achieves-motivation / necessity all covered by referenceable lib; gaps immaterial |

### 3 · Hatch check
If **`feasibility ≥ 3` AND `credibility ≥ 3`** → set `status: hatched`, refresh INDEX, append journal, and **only now do you proactively present the complete trustworthy plan** to the user. Done.
Otherwise, proceed to edit.

### 4 · Fill the buffer (haiku subagent; skip if the buffer already suffices)
- Check `buffer.md` first: if it already holds **unused candidates that can close the current gap** → **skip the subagent, save cost**, go to step 5.
- Otherwise → dispatch a **haiku subagent** (Agent tool, `model: haiku`), handing it: the current `mind-model.md` + `lib.md` + **the failing gate from step 2**. Have it research/think (WebSearch / WebFetch / document-specialist, or pure reasoning) and write candidate edits into `buffer.md`, typed:
  - **corroborate**: supporting evidence found for a claim.
  - **refine**: facts needed to make a vague point concrete.
  - **supplement**: new content for a coverage gap (a missing piece of the motivation/path).
  - **branch**: an **alternative route / fork** on the path spectrum (a different way to reach the same result), so cost/path-necessity can be compared.
  - **contradiction**: evidence that conflicts with the mind-model (plus a first guess at the root cause).
  Each candidate carries **source + content + intended use + type** (template in references). The subagent **only writes the buffer**; it does not touch mind-model/lib.

### 5 · Organize → store → single edit (main agent, targeting the gate from step 2)
1. Read `buffer.md` and **adjudicate each entry**: relevant and credible → accept; else drop and note one-line reason in journal.
2. **Accepted entries go into `lib.md` first** (assign `L#`, fill source/content/use) — hard rule: **mind-model may cite only `lib`**; any new claim must already have an `[L#]`.
3. From lib, **apply ONE edit** to mind-model; the motive is the one matching this round's gate (corroborate / refine / supplement / branch / contradiction — only one per round, touching only one section):
   - **branch** is written into "Path Spectrum" as an alternative between fastest-landing and ideal-form.
   - **contradiction** uses its dedicated flow: ① find the **root cause** first (bad data? changed premise? different scope/definition?) → ② research or think further → ③ classify and act: **resolvable** (adjust to self-consistency) / **ignorable** (state why the trunk is unaffected) / **fatal** (motivation or core path overturned → `status: blocked`, **proactively** give the user one explanatory line).
4. Any valid candidates not yet used **stay in the buffer** (reserved for the next round, not lost); remove accepted/dropped entries from the buffer.

### 6 · Evaluate one round, then stop
Re-score the two metrics → update `mind-model.md` frontmatter (metrics, `last_advanced`) → append one `journal.md` entry (did you dispatch haiku, what was accepted/dropped, what was retained) → trim `buffer.md` → refresh `INDEX.md` → **stop**.
When not hatched/blocked, **reply with a single status line**, e.g.
`🐣 <slug>: credibility 1→2 (supplemented coverage of "X") · logged, still incubating.`

---

## Noise & Cognitive Budget — applies to every write

- **One motive per round**, touching **one section** of the mind-model, net change **≤ 20 lines**, and at most **2–3 entries** accepted into `lib` per round. (`buffer.md` is a backstage staging area and may hold more candidates — it does not count toward the mind-model and is not shown to the user; the surplus waits for the next round.)
- **mind-model body default cap: < 3000 tokens** (configurable; frontmatter excluded; **no line-count limit on the total**). Near/at the cap, this round may only do "compression-integration" — see below.
- **Never show a half-baked plan to the user before it hatches**; all churn sinks into `journal.md`.
- Exception: user-initiated `show`/`list` — that's them asking, so it's fine.
- Slow is steady: prefer many small steps over one large untrustworthy plan in a single shot.

### When the cap is reached but new content must be added
Adding is not allowed to exceed the cap, but the idea must keep maturing. So when at/near the cap, make room **before** you add, in this order:
1. **Cut hand-wavy filler** — delete grand-but-empty phrasing that carries no decision-relevant content.
2. **Macro: raise the altitude.** Replace sprawling description with a more precise, more fundamental principle or architectural statement — one root principle that subsumes many specifics.
3. **Micro: lean on references.** For implementation detail, cite `[L#]` instead of inlining the explanation; the depth lives in lib, the body stays a pointer.
4. **De-duplicate.** Never let two sentences say the same thing in different words; keep the sharper one.
5. **Fold, don't fork.** When new content arrives, first try to merge it into an existing statement so the delta is minimal — avoid letting every point set up its own standalone item.

Compression done under these rules **is itself a legitimate advance** for the round.

## Invariants
1. Every non-obvious judgment in mind-model is traceable to a `lib` entry (`[L#]`).
2. Material flows one way: **buffer (candidate) → main agent accepts → lib → cited → mind-model**. Anything entering mind-model passed through lib first.
3. The haiku subagent **writes only `buffer.md`**; the authority to change `lib.md` / `mind-model.md` belongs **only to the main agent**.
4. Each `advance` = at most one mind-model edit (≤ 20 lines) + buffer trim + one journal entry + one INDEX refresh.
5. The user is interrupted **only** by: the one-line `hatch` confirmation, the one-line status of a pre-hatch advance, `hatched`, and `blocked`.
