# Idea Hatching · File Templates

Follow these structures when `hatch`/`advance` write files. Write body text in the idea's `lang` (examples below are in English; an idea captured in Chinese uses Chinese). Use real `YYYY-MM-DD` dates from the current session — never leave placeholders.

---

## `~/idea-hatching/INDEX.md` (one per library root)

Seed (on first creation):

```markdown
# Idea Hatching · Index

> Catalog of incubating ideas, one row each. status: incubating / hatched / blocked (fatal contradiction).
> F = feasibility (0–3, cost vs benefit)   C = credibility (0–3, coverage + referenceability)

| slug | status | F | C | last advanced | one-liner |
|------|--------|---|---|---------------|-----------|
```

One row per idea, e.g.:
```markdown
| meeting-note-tagger | incubating | 0 | 1 | 2026-06-27 | LLM auto-tags meeting notes with structured labels |
```

---

## `<slug>/mind-model.md` (the only deliverable · capped length · cites lib only)

```markdown
---
slug: meeting-note-tagger
status: incubating          # incubating | hatched | blocked
feasibility: 0              # 0–3, cost vs benefit
credibility: 0              # 0–3, evidence coverage + referenceability
lang: en
created: 2026-06-27
last_advanced: 0000-00-00   # not yet advanced
---

## Motivation
<Why it is worth doing. Every non-obvious judgment carries [L#]. Mark unsupported placeholders (unsupported).>

## Intuitive Essence
<One sentence: the core mechanism / insight.>

## Path Spectrum
- **Fastest complete landing**: <smallest version that fully works end-to-end.>
- **… (1–2 intermediate steps or branches allowed)**
- **Ideal full form**: <the picture when cost is no object.>
```

Constraints: body default < 3000 tokens (no line-count limit); a new claim enters lib first, then is cited as `[L#]`; net change ≤ 20 lines per advance; near the cap, compress-integrate instead of growing (cut filler → raise altitude → cite instead of inline → de-dup → fold into existing statements).

---

## `<slug>/buffer.md` (buffer module · written by haiku subagent · drained by main agent)

Seed (at `hatch`):
```markdown
# Buffer · meeting-note-tagger

> The haiku subagent writes candidate edits here after research; the main agent accepts them into lib or drops them, then clears processed entries.
> type: corroborate / refine / supplement / branch / contradiction.
> status: pending (to adjudicate) / accepted (moved to lib) / dropped / deferred (kept for next round).
```

Each candidate (written by haiku, default status: pending):
```markdown
### B1 · [refine] one-line title   <!-- status: pending -->
- source: <URL / reference / "own reasoning">
- content: <the concrete fact found>
- intended use: <which mind-model section, and which judgment it corroborates/refines/supplements/branches/refutes>
- target gate: <① motivation meaningful / ② result achieves motivation / ③ cost necessity>
```
After adjudication the main agent flips `status:` to accepted/dropped/deferred, and removes accepted/dropped entries during the next round's wrap-up.

---

## `<slug>/lib.md` (evidence store · the only source mind-model may cite)

Seed:
```markdown
# Lib · meeting-note-tagger

> mind-model may cite only this file. Each entry = source + content + use. IDs L1, L2, … never reused.
```

Each evidence entry:
```markdown
### L1 · one-line title
- source: <URL / reference / "own reasoning">
- content: <the concrete fact found or reasoned>
- use: <which mind-model judgment it corroborates / refines / supplements / refutes>
```

---

## `<slug>/journal.md` (append-only · churn sink · never enters mind-model or reaches the user)

Seed (at `hatch`):
```markdown
# Journal · meeting-note-tagger

## 2026-06-27 · hatched-in
- raw: "<the raw idea text>"
- lang: en, starting F0 C0.
```

Append one entry per `advance`:
```markdown
## 2026-06-27 · advance
- eval: F0 C1. First failing gate: ① is the motivation meaningful — motivation still has no grounding.
- buffer: insufficient → dispatched haiku subagent; wrote candidates B2 (corroborate), B3 (corroborate), B4 (branch).
- adjudication: accepted B2, B3 → stored as L2, L3; B4 (branch) kept as deferred for next round.
- motive: corroborate (added [L2][L3] to the "Motivation" section).
- action: inserted two market-demand evidences into Motivation and cited them.
- result: C1→2. Next: evaluate "does the result achieve the motivation"; buffer holds B4.
```

Contradiction round example:
```markdown
## 2026-06-27 · advance (contradiction)
- conflict: L5 contradicts mind-model "Path Spectrum — fastest landing".
- root cause: different scope (L5 means real-time; mind-model means batch).
- research/think: <…>
- classification: ignorable — does not affect the batch trunk; applicability scope noted in lib.
```
