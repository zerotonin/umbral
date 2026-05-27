# Secondary system — Excel (planned)

Python is the **source of truth**. Excel is a faithful, no-code mirror for the
convenor (David) to run the engine without a Python install. It is built in a
dedicated **Excel transformation sprint** *after* each Python sprint closes, so
the two never drift far apart.

## Translation contract

Each `data/*.csv` becomes one worksheet (same column names). The resolution and
tipping logic become worksheet formulas + named ranges — **no VBA** unless a
step genuinely cannot be expressed as a formula.

| Python piece | Excel equivalent |
|---|---|
| `data/*.csv` | one sheet each (`People`, `Alignment`, `LeverEffects`, ...) |
| `grading.q_tier_for_score` | `VLOOKUP`/`XLOOKUP` against `GMDecision` sheet |
| `alignment.resonance_for` | `IFS` on the affinity cell vs band edges |
| `resolution.resolve` | `2d6` cells + `INDEX/MATCH` into `LeverEffects` |
| `tipping.tipping_check` | `IF(P>=T, ..., contested d6)` |
| `reports.gazette_barometer` | a formatted `Gazette` sheet, expressed support only |

## Sprint mapping

`E1..E6` mirror Python `S1..S6` (see ../DEV_PLAN.md). A workbook ships at the
end of each Excel sprint as `excel/umbral_v<sprint>.xlsx`.
