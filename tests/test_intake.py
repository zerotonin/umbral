# ╔══════════════════════════════════════════════════════════════════╗
# ║  Umbral — test_intake                                            ║
# ║  « module »                                                      ║
# ╠══════════════════════════════════════════════════════════════════╣
# ╚══════════════════════════════════════════════════════════════════╝


from umbral.intake import load_grades, load_programmes
from umbral.models import Lever


def test_load_programmes(tmp_path):
    p = tmp_path / "plans.csv"
    p.write_text(
        "round,faction,target,lever,intent,leverage,cost,risk_staked\n"
        "2,Moderns,Students,concession,win students,budgets,spend,trust\n",
        encoding="utf-8",
    )
    progs = load_programmes(p)
    assert len(progs) == 1
    assert progs[0].lever is Lever.CONCESSION
    assert progs[0].faction == "Moderns"


def test_load_grades(tmp_path):
    p = tmp_path / "grades.csv"
    p.write_text("round,faction,target,q_score\n2,Moderns,Students,7\n", encoding="utf-8")
    assert load_grades(p)[("Moderns", "Students")] == 7
