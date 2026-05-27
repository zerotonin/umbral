# ╔══════════════════════════════════════════════════════════════════╗
# ║  Umbral — grading                                                ║
# ║  « GM judgement to numbers »                                     ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  Turn a 0-10 quality score + looked-up resonance into the        ║
# ║  static modifier the 2d6 roll is measured against.               ║
# ╚══════════════════════════════════════════════════════════════════╝


"""Turn a GM quality score into the static modifiers the dice roll uses."""
from __future__ import annotations

from umbral import alignment, constants
from umbral.models import GradedProgramme, Programme, Resonance


def grade(
    programme: Programme,
    q_score: int,
    affinity: dict,
    resonance_override: Resonance | None = None,
) -> GradedProgramme:
    """Score a programme: GM quality tier + (looked-up) resonance."""
    tier = constants.q_tier_for_score(q_score)
    q_mod = constants.Q_TIER_MOD[tier]
    resonance = resonance_override or alignment.resonance_for(
        affinity, programme.faction, programme.target
    )
    return GradedProgramme(
        programme=programme,
        q_score=q_score,
        q_tier=tier,
        q_mod=q_mod,
        resonance=resonance,
        resonance_mod=constants.RESONANCE_MOD[resonance],
    )
