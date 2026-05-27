# ╔══════════════════════════════════════════════════════════════════╗
# ║  Umbral — test_worked_example                                    ║
# ║  « module »                                                      ║
# ╠══════════════════════════════════════════════════════════════════╣
# ╚══════════════════════════════════════════════════════════════════╝


"""The Session-2 worked example from the Mass-Response Engine note."""
from umbral import alignment, constants
from umbral.grading import grade
from umbral.models import ConstituencyState, Lever, Programme
from umbral.resolution import resolve
from umbral.tipping import apply_resolution, disruption_index, run_tipping_phase


def test_session_open_cascade(make_rng):
    people = constants.load_people_table()
    by = {c.name: c for c in people}
    aff = alignment.load_affinity()
    links = alignment.load_contagion_links()
    # A dice = 3+4 = 7; B dice = 1+3 = 4; one contested d6 = 1 (no tip)
    rng = make_rng([3, 4, 1, 3, 1])

    g_a = grade(
        Programme(round=1, faction="Moderns", target="Students", lever=Lever.CONCESSION, intent=""),
        7, aff,
    )
    apply_resolution(by["Students"], resolve(g_a, rng), "Moderns")

    g_b = grade(
        Programme(round=1, faction="OldGuard", target="Urban proletariat", lever=Lever.REPRESSION, intent=""),
        6, aff,
    )
    martyr = apply_resolution(by["Urban proletariat"], resolve(g_b, rng), "OldGuard")

    tipped = run_tipping_phase(people, rng, martyr=martyr, contagion_links=links)

    assert by["Students"].state is ConstituencyState.QUIESCENT
    assert by["Urban proletariat"].state is ConstituencyState.ACTIVE
    assert "Urban proletariat" in tipped
    assert disruption_index(people) == 3
