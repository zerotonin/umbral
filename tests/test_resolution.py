# ╔══════════════════════════════════════════════════════════════════╗
# ║  Umbral — test_resolution                                        ║
# ║  « module »                                                      ║
# ╠══════════════════════════════════════════════════════════════════╣
# ╚══════════════════════════════════════════════════════════════════╝


from umbral import alignment
from umbral.grading import grade
from umbral.models import Lever, OutcomeBand, Programme
from umbral.resolution import resolve


def _prog(faction, target, lever):
    return Programme(round=1, faction=faction, target=target, lever=lever, intent="x")


def test_breakthrough_concession(make_rng):
    aff = alignment.load_affinity()
    graded = grade(_prog("Moderns", "Students", Lever.CONCESSION), 7, aff)
    res = resolve(graded, make_rng([3, 4]))
    assert res.total == 11
    assert res.band is OutcomeBand.BREAKTHROUGH
    assert res.deltas.grievance == -3
    assert res.deltas.contagion_seed is True


def test_backfired_repression_is_martyr(make_rng):
    aff = alignment.load_affinity()
    graded = grade(_prog("OldGuard", "Urban proletariat", Lever.REPRESSION), 6, aff)
    res = resolve(graded, make_rng([1, 3]))
    assert res.total == 3
    assert res.band is OutcomeBand.BACKFIRE
    assert res.deltas.martyr is True
    assert res.deltas.grievance == 3
