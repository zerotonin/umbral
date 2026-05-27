# ╔══════════════════════════════════════════════════════════════════╗
# ║  Umbral — reports                                                ║
# ║  « what the GM and the street see »                              ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  The GM round report (full state), the GM-only support report    ║
# ║  (true vs expressed), and the in-fiction gazette barometer.      ║
# ╚══════════════════════════════════════════════════════════════════╝


"""Round outputs: the GM report, the support report, and the gazette."""
from __future__ import annotations

from pathlib import Path

from umbral import constants
from umbral.models import Constituency, ConstituencyState


def expressed_support(constituency: Constituency) -> dict[str, float]:
    """Public-facing support after preference falsification (Kuran).

    Fear shifts ``falsification_gap`` points from the illegal pole (RPA) to the
    coercive pole (Old Guard). On a tip the gap is zeroed, so expressed == true.
    """
    exp = dict(constituency.true_support)
    gap = constituency.falsification_gap
    illegal = constants.ILLEGAL_FACTION
    coercive = constants.COERCIVE_FACTION
    if gap > 0 and illegal in exp:
        move = min(gap, exp[illegal])
        exp[illegal] -= move
        exp[coercive] = exp.get(coercive, 0.0) + move
    return exp


def _fmt_support(support: dict[str, float]) -> str:
    items = sorted(support.items(), key=lambda kv: -kv[1])
    return ", ".join(f"{f} {round(v)}%" for f, v in items if round(v) > 0)


def gm_round_report(round_number, resolutions, constituencies, contagion=None) -> str:
    lines = [f"# GM Round Report — Session {round_number}", "", "## Programme resolutions"]
    for r in resolutions:
        p = r.graded.programme
        lines.append(
            f"- **{p.faction} -> {p.target}** ({p.lever.value}): "
            f"Q{r.graded.q_score} {r.graded.q_tier.value} ({r.graded.q_mod:+d}), "
            f"{r.graded.resonance.value} ({r.graded.resonance_mod:+d}); "
            f"roll {r.dice} -> total {r.total} -> **{r.band.value}**"
        )
        d = r.deltas
        eff = []
        if d.grievance:
            eff.append(f"G {d.grievance:+g}")
        if d.risk:
            eff.append(f"R {d.risk:+g}")
        if d.support_shift:
            eff.append(f"support {d.support_shift:+g}")
        if d.martyr:
            eff.append("MARTYR")
        if d.contagion_seed:
            eff.append("contagion seed")
        lines.append(f"  - effect: {', '.join(eff) or 'none'}")
    lines += ["", "## Constituency state", "", "| Constituency | G | R | P=G-R | T | State |", "|---|---|---|---|---|---|"]
    for c in constituencies:
        lines.append(
            f"| {c.name} | {c.grievance:g} | {c.risk:g} | {c.net_pressure:g} | "
            f"{c.threshold:g} | {c.state.value} |"
        )
    idx = sum(c.size_weight for c in constituencies if c.state is ConstituencyState.ACTIVE)
    band = constants.disruption_band(idx)
    lines += ["", f"**Disruption Index: {idx} — {band['label']}** ({band['effect']})"]
    return "\n".join(lines) + "\n"


def support_report(constituency: Constituency) -> str:
    """GM-only true vs expressed support for one constituency."""
    exp = expressed_support(constituency)
    lines = [
        f"# Support Report (GM-only) — {constituency.name}",
        "",
        f"State: {constituency.state.value} · falsification gap: "
        f"{constituency.falsification_gap:g} pts",
        f"Net pressure P = {constituency.net_pressure:g} vs hidden T = "
        f"{constituency.threshold:g}",
        "",
        "| Faction | True | Expressed |",
        "|---|---|---|",
    ]
    for f in sorted(constituency.true_support, key=lambda k: -constituency.true_support[k]):
        lines.append(
            f"| {f} | {round(constituency.true_support[f])}% | {round(exp.get(f, 0))}% |"
        )
    return "\n".join(lines) + "\n"


def gazette_barometer(round_number, constituencies, gazette) -> str:
    """The in-fiction weekly gazette; shows expressed support only."""
    issue = gazette.get("issue_base", 0) + round_number
    lines = [
        f"# {gazette['gazette']}",
        f"## {gazette['masthead']}",
        f"*{gazette['year_epithet']} — Edición {issue}*",
        "",
        "> El barómetro político de Abuc, según el sentir declarado del pueblo.",
        "",
    ]
    idx = sum(c.size_weight for c in constituencies if c.state is ConstituencyState.ACTIVE)
    band = constants.disruption_band(idx)
    lines += [
        f"**Estado de la Nación:** {band['label']}  ·  índice de agitación {idx}/12",
        "",
        "| Sector | Ánimo | Simpatías declaradas |",
        "|---|---|---|",
    ]
    for c in constituencies:
        mood = "en pie" if c.state is ConstituencyState.ACTIVE else "en calma"
        lines.append(f"| {c.name} | {mood} | {_fmt_support(expressed_support(c))} |")
    lines += [
        "",
        "*El Barómetro no revela las lealtades ocultas; sólo lo que el pueblo se atreve a decir.*",
    ]
    return "\n".join(lines) + "\n"


def save_text(text: str, path) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
