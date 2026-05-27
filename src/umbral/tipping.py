# ╔══════════════════════════════════════════════════════════════════╗
# ║  Umbral — tipping                                                ║
# ║  « when the crowd turns »                                        ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  Apply deltas, run the Granovetter tipping check (P >= T),       ║
# ║  reveal falsified support on a tip, and propagate the cascade.   ║
# ╚══════════════════════════════════════════════════════════════════╝


"""Apply deltas, run the tipping check, and propagate the cascade."""
from __future__ import annotations

import random

from umbral import constants
from umbral.models import Constituency, ConstituencyState, Resolution


def apply_resolution(
    constituency: Constituency, resolution: Resolution, acting_faction: str
) -> bool:
    """Apply a resolution's deltas to a constituency. Returns True on martyr."""
    d = resolution.deltas
    constituency.grievance += d.grievance
    constituency.risk += d.risk
    constituency.falsification_gap = max(
        0.0, constituency.falsification_gap + d.falsification_gap
    )
    if d.support_shift:
        _shift_support(constituency, acting_faction, d.support_shift)
    constituency.clamp()
    return d.martyr


def _shift_support(constituency: Constituency, faction: str, points: float) -> None:
    sup = constituency.true_support
    if not sup:
        return
    current = sup.get(faction, 0.0)
    new = max(0.0, current + points)
    delta = new - current
    sup[faction] = new
    others = [f for f in sup if f != faction]
    pool = sum(sup[f] for f in others)
    if pool > 0 and delta:
        for f in others:
            sup[f] = max(0.0, sup[f] - delta * (sup[f] / pool))
    _normalise(sup)


def _normalise(sup: dict[str, float]) -> None:
    total = sum(sup.values())
    if total > 0:
        for f in sup:
            sup[f] = sup[f] * 100.0 / total


def tipping_check(
    constituency: Constituency,
    rng: random.Random,
    active_adjacent: int = 0,
    threshold: float | None = None,
) -> bool:
    """Granovetter check: auto-tip at P>=T, contested d6 just below T."""
    T = constituency.threshold if threshold is None else threshold
    P = constituency.net_pressure
    if P >= T:
        return True
    if (T - constants.CONTESTED_BAND) <= P < T:
        return rng.randint(1, 6) + active_adjacent >= constants.CONTESTED_DIE_SUCCESS
    return False


def disruption_index(constituencies: list[Constituency]) -> int:
    """Sum of size-weights of currently Active constituencies (max 12)."""
    return sum(
        c.size_weight for c in constituencies if c.state is ConstituencyState.ACTIVE
    )


def run_tipping_phase(
    constituencies: list[Constituency],
    rng: random.Random,
    martyr: bool = False,
    contagion_links: dict[str, list[str]] | None = None,
) -> list[str]:
    """Run the per-round tipping check; return names that tipped Active.

    Active constituencies de-escalate when their net pressure falls back below
    their (unhelped) threshold. A martyr this round drops every quiescent
    constituency's effective threshold, making the cascade easier.
    """
    drop = constants.MARTYR_THRESHOLD_DROP if martyr else 0.0
    active_names = {
        c.name for c in constituencies if c.state is ConstituencyState.ACTIVE
    }
    tipped: list[str] = []
    for c in constituencies:
        if c.state is ConstituencyState.ACTIVE:
            if c.net_pressure < c.threshold:
                c.state = ConstituencyState.QUIESCENT
            continue
        adjacent = sum(
            1 for n in (contagion_links or {}).get(c.name, []) if n in active_names
        )
        if tipping_check(c, rng, active_adjacent=adjacent, threshold=c.threshold - drop):
            c.state = ConstituencyState.ACTIVE
            c.falsification_gap = 0.0
            tipped.append(c.name)
    return tipped


def propagate_contagion(
    constituencies: list[Constituency], contagion_links: dict[str, list[str]]
) -> None:
    """Relieve risk and bump grievance of quiescent masses next to an active one."""
    active_names = {
        c.name for c in constituencies if c.state is ConstituencyState.ACTIVE
    }
    by_name = {c.name: c for c in constituencies}
    for src in active_names:
        for dst in contagion_links.get(src, []):
            c = by_name.get(dst)
            if c and c.state is ConstituencyState.QUIESCENT:
                c.risk -= constants.CONTAGION_RISK_RELIEF
                c.grievance += constants.CONTAGION_GRIEVANCE_BUMP
                c.clamp()
