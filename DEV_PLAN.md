# Umbral — development plan

**Primary system:** Python (this repo, fully documented + tested).
**Secondary system:** Excel, built in a transformation sprint *after* each
Python sprint closes (see `excel/README.md`). The two are split at the top
level so they never tangle.

## Architecture

```
src/umbral/      constants · models · intake · grading · alignment
                 resolution · tipping · diary · reports · state · engine · cli
data/            all tunable tables (CSV/JSON) — no code changes to retune
forms/           form column contract + Google Form build guide
examples/        a runnable opening session
excel/           secondary, no-code mirror (planned)
docs/            Sphinx (myst + furo)
tests/           engine math, tipping, intake, worked example
```

## Python sprints

| Sprint | Scope | State |
|---|---|---|
| **S0** | Scaffold: package, data tables, CI, docs, tests, worked example | done |
| **S1** | Harden intake: validation, friendly errors, multi-round CSVs | next |
| **S2** | Alignment tooling: distance-matrix report, affinity editor checks | |
| **S3** | Reports: SVG/PNG barometer figure + CSV companion (Wong palette) | |
| **S4** | Faction inventories (QoL, Money, Arms) wired to disruption bands | |
| **S5** | GM web intake (host the form + a thin review UI) | |
| **S6** | Full multi-session campaign runner + replay from diary | |

## Excel transformation sprints

Each `E#` mirrors the matching `S#` into `excel/umbral_v<sprint>.xlsx`:
sheet-per-table, `XLOOKUP`/`INDEX-MATCH` for the lookups, `IF` chains for
tipping, a formatted `Gazette` sheet. No VBA unless unavoidable.

## Conventions

- No third-party runtime deps (stdlib only) — keeps the Excel mirror faithful.
- Tables are data, not code. Decision logic stays out of the pipeline.
- Run from a source checkout (or `pip install -e .`); `constants.DATA_DIR`
  resolves to the repo's `data/`.
