# ╔══════════════════════════════════════════════════════════════════╗
# ║  Umbral — intake                                                 ║
# ║  « collect the plans »                                           ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  Form-agnostic CSV loaders for 3-point programmes and GM grades. ║
# ║  Any tool that emits forms/programme_columns.csv will load.      ║
# ╚══════════════════════════════════════════════════════════════════╝


"""Collect 3-point programmes (form export) and GM grades from CSV.

The intake is form-agnostic: any tool (Google Forms, MS Forms, a hand-edited
CSV) that emits the column contract in ``forms/programme_columns.csv`` loads.
"""
from __future__ import annotations

import csv

from umbral.models import Lever, Programme


def load_programmes(path) -> list[Programme]:
    out: list[Programme] = []
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            out.append(
                Programme(
                    round=int(row["round"]),
                    faction=row["faction"].strip(),
                    target=row["target"].strip(),
                    lever=Lever(row["lever"].strip().lower()),
                    intent=row.get("intent", "").strip(),
                    leverage=row.get("leverage", "").strip(),
                    cost=row.get("cost", "").strip(),
                    risk_staked=row.get("risk_staked", "").strip(),
                    raw=dict(row),
                )
            )
    return out


def load_grades(path) -> dict[tuple[str, str], int]:
    out: dict[tuple[str, str], int] = {}
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            out[(row["faction"].strip(), row["target"].strip())] = int(row["q_score"])
    return out
