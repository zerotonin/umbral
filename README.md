# Umbral

[![tests](https://github.com/zerotonin/umbral/actions/workflows/tests.yml/badge.svg)](https://github.com/zerotonin/umbral/actions/workflows/tests.yml)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Mass-response engine for *The Fate of Abuc*** — the POLS399 revolution-and-
uprising RPG. Umbral answers the playbook's open question: *how does the GM,
with dice, calibrate how each popular constituency responds to the factions'
interventions?* It models that with hidden **Granovetter** thresholds,
**Epstein** active/quiescent dynamics, and **Kuran** preference falsification.

> Two systems, deliberately split. **Python is the source of truth** (this
> repo). **Excel** is a no-code mirror for the convenor, built in a separate
> transformation sprint. See `DEV_PLAN.md`.

## Install

```bash
pip install -e ".[dev]"      # or: conda env create -f environment.yml
```

No third-party runtime dependencies — the engine is pure standard library.

## Quickstart

```bash
umbral init --out state.json
umbral run-round \
  --state state.json \
  --programmes examples/session1_programmes.csv \
  --grades examples/session1_grades.csv \
  --outdir round_01 --seed 7
```

Outputs land in `round_01/`: `gm_report.md`, `gazette.md` (the in-fiction
*Barómetro del Pueblo*), `peasant_support.md` (GM-only true vs expressed),
`diary.jsonl`, and the next `state.json`.

## How a round resolves

1. Players submit **3-point programmes** through a form (`forms/`).
2. The GM grades each **0-10**; the engine looks up **resonance** from the
   constituency x faction affinity table.
3. `2d6 + modifiers` -> outcome band -> grievance/risk/support deltas.
4. The **tipping check** decides who mobilises; backfired repression makes a
   **martyr** that lowers everyone's threshold; cascades spread.

## Tuning

Everything numeric is a CSV in `data/`. Edit starting conditions, affinities,
lever effects, or disruption bands without touching code.

## Citation

See `CITATION.cff`.

## License

MIT — see `LICENSE`.
