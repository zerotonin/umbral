# ╔══════════════════════════════════════════════════════════════════╗
# ║  Umbral — test_tipping                                           ║
# ║  « module »                                                      ║
# ╠══════════════════════════════════════════════════════════════════╣
# ╚══════════════════════════════════════════════════════════════════╝


from umbral import constants
from umbral.models import ConstituencyState
from umbral.tipping import disruption_index, run_tipping_phase, tipping_check


def _one(name):
    return [c for c in constants.load_people_table() if c.name == name][0]


def test_auto_tip(make_rng):
    up = _one("Urban proletariat")
    up.grievance = 9
    assert tipping_check(up, make_rng([1, 1]), threshold=3) is True


def test_de_escalation(make_rng):
    st = _one("Students")
    st.grievance = 2  # P = 0 < T = 2
    tipped = run_tipping_phase([st], make_rng([1]))
    assert st.state is ConstituencyState.QUIESCENT
    assert tipped == []


def test_disruption_index_at_open():
    assert disruption_index(constants.load_people_table()) == 1
