# ╔══════════════════════════════════════════════════════════════════╗
# ║  Umbral — models                                                 ║
# ║  « the nouns of the game »                                       ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  Constituencies, factions, programmes, and the resolution record. ║
# ║  Plain dataclasses + enums; no I/O, no rules.                    ║
# ╚══════════════════════════════════════════════════════════════════╝


"""Dataclasses and enums describing constituencies, factions, and actions."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ConstituencyState(str, Enum):
    QUIESCENT = "quiescent"
    ACTIVE = "active"


class Lever(str, Enum):
    CONCESSION = "concession"
    REPRESSION = "repression"
    AGITATION = "agitation"


class QTier(str, Enum):
    WEAK = "weak"
    SOUND = "sound"
    STRONG = "strong"
    DECISIVE = "decisive"


class Resonance(str, Enum):
    ALIGNED = "aligned"
    NEUTRAL = "neutral"
    DISSONANT = "dissonant"


class OutcomeBand(str, Enum):
    BACKFIRE = "backfire"
    PARTIAL = "partial"
    SUCCESS = "success"
    BREAKTHROUGH = "breakthrough"


@dataclass
class Constituency:
    """A popular/mass element whose mobilisation the factions contest."""

    name: str
    size_weight: int
    grievance: float
    risk: float
    threshold: float
    action_mode: str
    state: ConstituencyState = ConstituencyState.QUIESCENT
    falsification_gap: float = 0.0
    true_support: dict[str, float] = field(default_factory=dict)

    @property
    def net_pressure(self) -> float:
        """Epstein net pressure P = grievance - risk."""
        return self.grievance - self.risk

    def clamp(self) -> None:
        """Keep grievance and risk inside the 0-10 scale."""
        self.grievance = max(0.0, min(10.0, self.grievance))
        self.risk = max(0.0, min(10.0, self.risk))


@dataclass
class Faction:
    name: str
    display_name: str
    is_player: bool = True


@dataclass
class Programme:
    """A faction's 3-point programme targeting one constituency."""

    round: int
    faction: str
    target: str
    lever: Lever
    intent: str
    leverage: str = ""
    cost: str = ""
    risk_staked: str = ""
    raw: dict[str, str] = field(default_factory=dict)


@dataclass
class GradedProgramme:
    """A programme after the GM has scored it and resonance is looked up."""

    programme: Programme
    q_score: int
    q_tier: QTier
    q_mod: int
    resonance: Resonance
    resonance_mod: int

    @property
    def static_modifier(self) -> int:
        return self.q_mod + self.resonance_mod


@dataclass
class Deltas:
    grievance: float = 0.0
    risk: float = 0.0
    falsification_gap: float = 0.0
    support_shift: float = 0.0
    martyr: bool = False
    contagion_seed: bool = False


@dataclass
class Resolution:
    graded: GradedProgramme
    dice: int
    total: int
    band: OutcomeBand
    deltas: Deltas
