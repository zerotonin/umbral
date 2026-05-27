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

## Two quantities, often confused: affinity vs support

A faction relates to a constituency through **two separate numbers**. They are
*not* the same thing, and the rules must not treat them as interchangeable.

| | **Affinity** | **Support %** |
|---|---|---|
| File | `data/alignment_matrix.csv` | `data/support_seed.csv` (+ moves in play) |
| Range | −1 … +1 | 0–100 % (a share of the constituency) |
| Nature | **static** disposition | **dynamic** allegiance |
| Question | *how receptive is this constituency to that faction's pitch?* | *how much of this constituency currently backs that faction?* |
| Used for | the **resonance** roll modifier (`+2 / 0 / −3`) | what a round's outcome **moves**, and what the reports show |

**How affinity becomes the `+2 / −3` you see in the rules.** The affinity cell
is bucketed into a resonance band, and the band is the roll modifier:

| Affinity | Resonance | Roll modifier |
|---|---|---|
| ≥ +0.34 | Aligned | **+2** |
| −0.33 … +0.33 | Neutral | **0** |
| ≤ −0.34 | Dissonant | **−3** |

(Edges are `AFFINITY_ALIGNED_MIN` / `AFFINITY_DISSONANT_MAX` in `constants.py`;
the modifiers are `RESONANCE_MOD`.)

**The relationship.** Affinity is the *gradient*; support % is the *position*.
A positive affinity makes it **easier** (a better roll) for a faction to grow
its support share with that constituency — but the two can diverge. Peasants
give the Old Guard 25 % support today (through Church ties), yet the Old Guard's
*affinity* with peasants is only −0.2: that support is held **against the
grain** and is fragile. Each round, **affinity sets the resonance modifier; the
dice then move support %.** Affinity does not change in play; support does.

### Why affinity and support are deliberately *not* connected

Resonance is read from affinity, **never** from current support %. This is a
fixed design decision, for four reasons a player should understand:

1. **It would create a runaway feedback loop.** If holding a constituency's
   support made your pitches land better (higher resonance), you would gain
   *more* support, which would raise resonance again — rich-get-richer. Whoever
   starts ahead snowballs and trailing factions can never break in. Decoupling
   keeps every round winnable.
2. **No double-counting.** Support % is the *output* the dice move. If it also
   fed back into the *input* (resonance), the same quantity would sit on both
   sides of the equation — circular, and it would amplify variance in ways the
   GM cannot reason about.
3. **It models real politics.** A faction can hold support *against* its natural
   disposition (the Old Guard's 25 % of peasants, bought with Church patronage,
   not won by resonance) — and such support is fragile. A faction can also be
   well-disposed yet hold little support (room to grow). That gap — sticky
   support where disposition agrees, precarious support where it does not — is
   the dramatically interesting part of the game. Collapsing the two erases it.
4. **It keeps grading tractable.** Affinity is a fixed lookup the GM applies
   once from a known table; players can predict the modifier. A resonance that
   moved with live support would have to be recomputed every round and could
   not be explained at the table.

So: **disposition (affinity) is a structural constant; allegiance (support %)
is the moving state.** Each round, affinity sets the resonance modifier and the
dice then move support. They are two axes on purpose, and the rule book treats
them as such.

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
