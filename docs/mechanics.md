# Mechanics

The full design rationale lives in the lab note *Mass-Response Engine*. This
page summarises what the code does.

## Per-constituency state

| Variable | Meaning |
|---|---|
| Grievance `G` | motivation to act |
| Risk `R` | perceived danger of acting |
| Threshold `T` (hidden) | net pressure needed to mobilise |
| Net pressure `P = G - R` | mobilise when `P >= T` |

## One round

1. **Intake** — load 3-point programmes (`intake.load_programmes`).
2. **Grade** — GM scores quality 0-10; resonance is looked up from the
   affinity cross-table (`grading.grade`, `alignment`).
3. **Resolve** — `2d6 + Q mod + resonance mod` -> outcome band -> deltas
   (`resolution.resolve`, `data/lever_effects.csv`).
4. **Tip** — apply deltas, run the threshold check, reveal falsified support on
   a tip, propagate the cascade (`tipping`).
5. **Report** — GM report, GM-only support report, and the in-fiction gazette
   barometer (`reports`); everything is logged to the JSONL `diary`.

## Editing the game

Every table is a CSV in `data/`. Change starting conditions, affinities, lever
effects, or the disruption bands without touching Python.
