# ╔══════════════════════════════════════════════════════════════════╗
# ║  Umbral — alignment                                              ║
# ║  « the cross-table »                                             ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  Constituency x faction affinity drives resonance.               ║
# ║  Plus a clustering-style pairwise distance matrix over the rows. ║
# ╚══════════════════════════════════════════════════════════════════╝


"""Constituency x faction affinity table and clustering-style distances.

The affinity matrix (``data/alignment_matrix.csv``) is the cross-table that
drives *resonance*: how well a faction's intervention fits a constituency. We
also expose a pairwise constituency distance matrix computed from the affinity
rows, the analogue of a distance table in clustering, used to reason about
which masses are close enough to carry a cascade.
"""
from __future__ import annotations

import csv
from math import sqrt
from pathlib import Path

from umbral import constants
from umbral.models import Resonance


def load_affinity(path: Path | None = None) -> dict[str, dict[str, float]]:
    path = path or constants.DATA_DIR / "alignment_matrix.csv"
    out: dict[str, dict[str, float]] = {}
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        factions = [c for c in reader.fieldnames if c != "constituency"]
        for row in reader:
            out[row["constituency"]] = {f: float(row[f]) for f in factions}
    return out


def resonance_for(affinity: dict, faction: str, constituency: str) -> Resonance:
    """Bucket the affinity cell into ALIGNED / NEUTRAL / DISSONANT."""
    a = affinity[constituency][faction]
    if a >= constants.AFFINITY_ALIGNED_MIN:
        return Resonance.ALIGNED
    if a <= constants.AFFINITY_DISSONANT_MAX:
        return Resonance.DISSONANT
    return Resonance.NEUTRAL


def distance_matrix(affinity: dict) -> dict[str, dict[str, float]]:
    """Pairwise Euclidean distance between constituencies over faction affinities."""
    names = list(affinity)
    factions = list(next(iter(affinity.values())))
    out: dict[str, dict[str, float]] = {a: {} for a in names}
    for a in names:
        for b in names:
            out[a][b] = sqrt(sum((affinity[a][f] - affinity[b][f]) ** 2 for f in factions))
    return out


def nearest(affinity: dict, constituency: str, k: int = 2) -> list[str]:
    dm = distance_matrix(affinity)[constituency]
    others = [n for n in dm if n != constituency]
    return sorted(others, key=lambda n: dm[n])[:k]


def load_contagion_links(path: Path | None = None) -> dict[str, list[str]]:
    path = path or constants.DATA_DIR / "contagion_links.csv"
    out: dict[str, list[str]] = {}
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            out.setdefault(row["from"], []).append(row["to"])
    return out
