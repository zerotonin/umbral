# ╔══════════════════════════════════════════════════════════════════╗
# ║  Umbral — engine                                                 ║
# ║  « the round, end to end »                                       ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  Orchestration: intake -> grade -> resolve -> tipping ->         ║
# ║  contagion -> reports -> diary -> next-round state.              ║
# ╚══════════════════════════════════════════════════════════════════╝


"""Round orchestration: intake -> grade -> resolve -> tipping -> reports."""
from __future__ import annotations

import random
from pathlib import Path

from umbral import alignment, constants, intake, reports, state
from umbral import diary as diary_mod
from umbral.grading import grade
from umbral.models import ConstituencyState
from umbral.resolution import resolve
from umbral.tipping import apply_resolution, propagate_contagion, run_tipping_phase


def init_state(out_path) -> None:
    """Write a fresh round-1 starting state from the data tables."""
    state.save_state(constituencies=constants.load_people_table(), round_number=1, path=out_path)


def run_round(state_path, programmes_path, grades_path, outdir, seed=None) -> dict:
    """Resolve one session and write all outputs. Returns a small summary."""
    rng = random.Random(seed)
    people, round_number = state.load_state(state_path)
    by_name = {c.name: c for c in people}
    affinity = alignment.load_affinity()
    links = alignment.load_contagion_links()
    gazette = constants.load_gazette_config()

    programmes = intake.load_programmes(programmes_path)
    grades = intake.load_grades(grades_path)

    outdir = Path(outdir)
    ledger = diary_mod.Diary(outdir / "diary.jsonl")

    resolutions = []
    any_martyr = False
    for p in programmes:
        if p.round != round_number:
            continue
        graded = grade(p, grades[(p.faction, p.target)], affinity)
        res = resolve(graded, rng)
        any_martyr = apply_resolution(by_name[p.target], res, p.faction) or any_martyr
        ledger.log_resolution(res, round_number)
        resolutions.append(res)

    tipped = run_tipping_phase(people, rng, martyr=any_martyr, contagion_links=links)
    propagate_contagion(people, links)
    idx = sum(c.size_weight for c in people if c.state is ConstituencyState.ACTIVE)
    ledger.log_tipping(round_number, tipped, idx)

    reports.save_text(
        reports.gm_round_report(round_number, resolutions, people, links),
        outdir / "gm_report.md",
    )
    reports.save_text(
        reports.gazette_barometer(round_number, people, gazette), outdir / "gazette.md"
    )
    peasant = by_name.get("Peasant farmers")
    if peasant:
        reports.save_text(reports.support_report(peasant), outdir / "peasant_support.md")

    state.save_state(people, round_number + 1, outdir / "state.json")
    return {"round": round_number, "tipped": tipped, "disruption_index": idx}
