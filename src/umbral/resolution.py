# ╔══════════════════════════════════════════════════════════════════╗
# ║  Umbral — resolution                                             ║
# ║  « the dice moment »                                             ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  2d6 + static modifier -> outcome band -> grievance/risk/support ║
# ║  deltas, read from the lever-effects table.                      ║
# ╚══════════════════════════════════════════════════════════════════╝


"""Roll a graded programme and compute its grievance/risk/support deltas."""
from __future__ import annotations

import random

from umbral import constants
from umbral.models import Deltas, GradedProgramme, Resolution


def roll_2d6(rng: random.Random) -> int:
    return rng.randint(1, 6) + rng.randint(1, 6)


def resolve(graded: GradedProgramme, rng: random.Random) -> Resolution:
    """Resolve one graded programme into a Resolution record."""
    dice = roll_2d6(rng)
    total = dice + graded.static_modifier
    band = constants.outcome_band(total)
    effect = constants.LEVER_EFFECTS[(graded.programme.lever, band)]
    deltas = Deltas(
        grievance=effect["grievance"],
        risk=effect["risk"],
        support_shift=effect["support"],
        falsification_gap=effect["falsification"],
        martyr=effect["martyr"],
        contagion_seed=effect["contagion_seed"],
    )
    return Resolution(graded=graded, dice=dice, total=total, band=band, deltas=deltas)
