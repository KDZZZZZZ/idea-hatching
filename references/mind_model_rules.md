# Mind Model Rules

## File contract

`mind-model.md` is the only user-facing deliverable for an idea.

Required sections:
- Motivation
- Intuitive Essence
- Path Spectrum

Frontmatter:
- `slug`
- `status`: `incubating | hatched | blocked`
- `feasibility`: `0..3`
- `credibility`: `0..3`
- `lang`
- `created`
- `last_advanced`

## Evidence rule

Every non-obvious judgment in `mind-model.md` must cite `lib.md` with `[L#]`. New material enters `lib.md` before it can enter `mind-model.md`.

## Scoring

| score | feasibility | credibility |
|---|---|---|
| 0 | not assessed | mostly assumption, unsupported |
| 1 | benefit unclear, or cost clearly too high | isolated grounding, big gaps |
| 2 | net-positive but major uncertainty | main judgments grounded, minor gaps |
| 3 | net-positive, uncertainty bounded, path necessary and sufficient | all three gates covered by referenceable evidence |

## Gates

Evaluate in this order and work on the first failing gate:
1. Is the motivation meaningful?
2. Would the implemented result achieve the motivation?
3. Are all costs and implementation path elements necessary?

## Change budget

Each `advance` may change:
- one motive only;
- one mind-model section only;
- at most 20 net lines;
- at most 2–3 accepted lib entries.

The mind-model body default cap is <3000 tokens. There is no total line-count cap.

## When near the token cap

Make room before adding content:
1. Cut hand-wavy filler.
2. Replace sprawling macro description with a sharper root principle or architecture statement.
3. Use `[L#]` citations for micro detail instead of inlining.
4. De-duplicate repeated meanings.
5. Fold new material into existing statements before creating standalone points.

Compression under these rules counts as a valid advance.

## Contradictions

For contradictions:
1. identify root cause first: bad data, changed premise, different scope, or different definition;
2. research or think further;
3. classify as resolvable, ignorable, or fatal.

Fatal contradiction sets `status: blocked`.
