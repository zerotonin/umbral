# 3-Point Programme intake form

The engine is **form-agnostic**: any tool that exports the column contract in
`programme_columns.csv` will load. The easy host is a Google Form backed by a
Google Sheet, exported as CSV.

## Google Form fields (map 1:1 to columns)

| Form question | Column | Type | Notes |
|---|---|---|---|
| Which session is this for? | `round` | short answer (number) | |
| Your faction | `faction` | multiple choice | use the keys in `data/factions.csv` |
| Target constituency | `target` | multiple choice | exact names from `data/people_table.csv` |
| Lever | `lever` | multiple choice | `concession` / `repression` / `agitation` |
| Intent — what do you want to achieve? | `intent` | paragraph | |
| Leverage — why can you pull it off? | `leverage` | paragraph | cite history |
| Cost — what will it cost you? | `cost` | paragraph | optional |
| Risk — what do you put at risk? | `risk_staked` | paragraph | optional |

## Export

File → Download → CSV from the linked Sheet, then run:

```
umbral run-round --state state.json --programmes plans.csv --grades grades.csv --outdir round_02
```

The GM grades each programme 0-10 in a second sheet matching `grades_columns.csv`.
