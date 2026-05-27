# ╔══════════════════════════════════════════════════════════════════╗
# ║  Umbral — constants                                              ║
# ║  « one source of truth »                                         ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  Loads starting conditions and lookup tables from data/.         ║
# ║  Disruption table, people table, GM decision table, lever effects. ║
# ║  Edit the CSVs, not this file, to retune the game.               ║
# ╚══════════════════════════════════════════════════════════════════╝


"""Starting conditions, lookup tables, and tuning knobs.

All numeric tables live in ``data/`` as CSV/JSON so the convenor can retune the
game without touching Python. This module loads them at import and exposes
typed lookups. The values reproduce the worked example in the lab note
*Mass-Response Engine*.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

from umbral.models import (
    Constituency,
    ConstituencyState,
    Lever,
    OutcomeBand,
    QTier,
    Resonance,
)

# ── paths ──────────────────────────────────────────────────────────────
PACKAGE_ROOT: Path = Path(__file__).resolve().parent
REPO_ROOT: Path = PACKAGE_ROOT.parent.parent
DATA_DIR: Path = REPO_ROOT / "data"

# ── static modifier lookups (Mass-Response Engine, section C) ────────────
Q_TIER_MOD: dict[QTier, int] = {
    QTier.WEAK: -2,
    QTier.SOUND: 0,
    QTier.STRONG: 2,
    QTier.DECISIVE: 4,
}
RESONANCE_MOD: dict[Resonance, int] = {
    Resonance.ALIGNED: 2,
    Resonance.NEUTRAL: 0,
    Resonance.DISSONANT: -3,
}

# affinity -> resonance band edges
AFFINITY_ALIGNED_MIN: float = 0.34
AFFINITY_DISSONANT_MAX: float = -0.34

# ── tipping / cascade tuning (Mass-Response Engine, section D) ────────────
CONTESTED_BAND: float = 2.0
CONTESTED_DIE_SUCCESS: int = 5
CONTAGION_RISK_RELIEF: float = 1.0
CONTAGION_GRIEVANCE_BUMP: float = 1.0
MARTYR_THRESHOLD_DROP: float = 1.0

# Abuc-specific poles for the falsification model
COERCIVE_FACTION: str = "OldGuard"
ILLEGAL_FACTION: str = "RPA"

# ── report change-colouring (Wong 2011, colourblind-safe) ────────────────
# Default: blue increase / vermilion decrease — the most robust diverging pair,
# legible under deutan, protan AND tritan deficiency. For a "growth/decline"
# feel, swap to teal/orange (strong for deutan/protan, weaker for rare tritan):
#     COLOR_INCREASE = "#009E73"  # Wong bluish-green (teal)
#     COLOR_DECREASE = "#E69F00"  # Wong orange
COLOR_INCREASE: str = "#0072B2"  # Wong blue
COLOR_DECREASE: str = "#D55E00"  # Wong vermilion


def _read_csv(path: Path) -> list[dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def q_tier_for_score(q: int) -> QTier:
    """Map a 0-10 GM quality score to its tier via the GM decision table."""
    for row in GM_DECISION_TABLE:
        if int(row["q_min"]) <= q <= int(row["q_max"]):
            return QTier(row["tier"])
    raise ValueError(f"quality score out of range: {q}")


def outcome_band(total: int) -> OutcomeBand:
    """Map a 2d6 + modifiers total to its outcome band."""
    for row in OUTCOME_BANDS:
        lo = int(row["total_min"]) if row["total_min"] else -999
        hi = int(row["total_max"]) if row["total_max"] else 999
        if lo <= total <= hi:
            return OutcomeBand(row["band"])
    raise ValueError(f"no outcome band for total {total}")


def disruption_band(index: int) -> dict[str, str]:
    """Return the disruption-table row whose [min, max] contains ``index``."""
    for row in DISRUPTION_TABLE:
        if int(row["min"]) <= index <= int(row["max"]):
            return row
    return DISRUPTION_TABLE[-1]


def load_support_seed(path: Path | None = None) -> dict[str, tuple[dict[str, float], float]]:
    """Return {constituency: ({faction: true_pct}, falsification_gap)}."""
    rows = _read_csv(path or DATA_DIR / "support_seed.csv")
    out: dict[str, tuple[dict[str, float], float]] = {}
    for r in rows:
        name = r["constituency"]
        if name not in out:
            out[name] = ({}, float(r["falsification_gap"]))
        out[name][0][r["faction"]] = float(r["true_pct"])
    return out


def load_people_table(path: Path | None = None) -> list[Constituency]:
    """Build fresh Constituency objects from the people table + support seed."""
    rows = _read_csv(path or DATA_DIR / "people_table.csv")
    support = load_support_seed()
    people: list[Constituency] = []
    for r in rows:
        true_support, gap = support.get(r["name"], ({}, 0.0))
        people.append(
            Constituency(
                name=r["name"],
                size_weight=int(r["size_weight"]),
                grievance=float(r["grievance"]),
                risk=float(r["risk"]),
                threshold=float(r["threshold"]),
                action_mode=r["action_mode"],
                state=ConstituencyState(r["state"]),
                falsification_gap=gap,
                true_support=dict(true_support),
            )
        )
    return people


def load_lever_effects(path: Path | None = None) -> dict[tuple[Lever, OutcomeBand], dict]:
    rows = _read_csv(path or DATA_DIR / "lever_effects.csv")
    out: dict[tuple[Lever, OutcomeBand], dict] = {}
    for r in rows:
        key = (Lever(r["lever"]), OutcomeBand(r["band"]))
        out[key] = {
            "grievance": float(r["grievance"]),
            "risk": float(r["risk"]),
            "support": float(r["support"]),
            "falsification": float(r["falsification"]),
            "martyr": bool(int(r["martyr"])),
            "contagion_seed": bool(int(r["contagion_seed"])),
        }
    return out


def load_factions(path: Path | None = None) -> list[dict[str, str]]:
    return _read_csv(path or DATA_DIR / "factions.csv")


def load_gazette_config(path: Path | None = None) -> dict:
    p = path or DATA_DIR / "gazette_config.json"
    return json.loads(p.read_text(encoding="utf-8"))


# ── tables loaded once at import ─────────────────────────────────────────
GM_DECISION_TABLE: list[dict[str, str]] = _read_csv(DATA_DIR / "gm_decision_table.csv")
OUTCOME_BANDS: list[dict[str, str]] = _read_csv(DATA_DIR / "outcome_bands.csv")
DISRUPTION_TABLE: list[dict[str, str]] = _read_csv(DATA_DIR / "disruption_table.csv")
LEVER_EFFECTS: dict[tuple[Lever, OutcomeBand], dict] = load_lever_effects()
