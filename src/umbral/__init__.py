# ╔══════════════════════════════════════════════════════════════════╗
# ║  Umbral — __init__                                               ║
# ║  « public API and version »                                      ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  Mass-response engine for The Fate of Abuc (POLS399).            ║
# ║  Granovetter thresholds + Epstein dynamics + Kuran falsification. ║
# ╚══════════════════════════════════════════════════════════════════╝


"""Umbral — mass-response engine for *The Fate of Abuc* (POLS399)."""
from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("umbral")
except PackageNotFoundError:  # pragma: no cover - source checkout without install
    __version__ = "0.0.0+unknown"

from umbral.models import (
    Constituency,
    ConstituencyState,
    Deltas,
    Faction,
    GradedProgramme,
    Lever,
    OutcomeBand,
    Programme,
    QTier,
    Resolution,
    Resonance,
)

__all__ = [
    "__version__",
    "Constituency",
    "ConstituencyState",
    "Deltas",
    "Faction",
    "GradedProgramme",
    "Lever",
    "OutcomeBand",
    "Programme",
    "QTier",
    "Resolution",
    "Resonance",
]
