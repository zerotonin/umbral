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


# ── change colouring (teal up / orange down; see constants) ───────────────
def _span(text: str, color: str) -> str:
    return f'<span style="color:{color}">{text}</span>'


def _delta(after: float, before: float, fmt: str = "{:+g}") -> str:
    """Coloured ``(Δ)`` suffix, or empty string when nothing changed."""
    d = after - before
    if abs(d) < 1e-9:
        return ""
    color = constants.COLOR_INCREASE if d > 0 else constants.COLOR_DECREASE
    return " " + _span(f"({fmt.format(d)})", color)


def _val(after: float, before: float) -> str:
    return f"{after:g}{_delta(after, before)}"


def _state_cell(after: str, before: str) -> str:
    if after == before:
        return after
    color = constants.COLOR_INCREASE if after == "active" else constants.COLOR_DECREASE
    return _span(f"{after} (was {before})", color)


def _effect_token(label: str, value: float) -> str:
    color = constants.COLOR_INCREASE if value > 0 else constants.COLOR_DECREASE
    return _span(f"{label} {value:+g}", color)


def snapshot(constituencies: list[Constituency]) -> dict:
    """Capture per-constituency state for diffing against the post-round state."""
    return {
        c.name: {
            "grievance": c.grievance,
            "risk": c.risk,
            "threshold": c.threshold,
            "net_pressure": c.net_pressure,
            "falsification_gap": c.falsification_gap,
            "state": c.state.value,
            "true_support": dict(c.true_support),
        }
        for c in constituencies
    }


_LEGEND = (
    "Changes this session are coloured: "
    f"{_span('increase', constants.COLOR_INCREASE)} / "
    f"{_span('decrease', constants.COLOR_DECREASE)}."
)

_SUPPORT_ORDER = ["RPA", "OldGuard", "Moderns", "OUP", "PPA", "Church"]


def _all_factions(constituencies: list[Constituency]) -> list[str]:
    """Union of factions across all constituencies, in a stable column order."""
    present: set[str] = set()
    for c in constituencies:
        present |= set(c.true_support)
    extra = sorted(f for f in present if f not in _SUPPORT_ORDER)
    return [f for f in _SUPPORT_ORDER if f in present] + extra


def _true_support_table(constituencies, before, factions) -> list[str]:
    head = "| Constituency | " + " | ".join(factions) + " | Gap |"
    rows = [head, "|" + "---|" * (len(factions) + 2)]
    for c in constituencies:
        b = before[c.name]
        cells = []
        for f in factions:
            if f in c.true_support:
                now, was = round(c.true_support[f]), round(b["true_support"].get(f, 0.0))
                cells.append(f"{now}%{_delta(now, was)}")
            else:
                cells.append("—")
        gap = _val(c.falsification_gap, b["falsification_gap"])
        rows.append(f"| {c.name} | " + " | ".join(cells) + f" | {gap} |")
    return rows


def _expressed_support_table(constituencies, factions) -> list[str]:
    head = "| Constituency | " + " | ".join(factions) + " |"
    rows = [head, "|" + "---|" * (len(factions) + 1)]
    for c in constituencies:
        exp = expressed_support(c)
        cells = [f"{round(exp[f])}%" if f in exp else "—" for f in factions]
        rows.append(f"| {c.name} | " + " | ".join(cells) + " |")
    return rows


def gm_round_report(round_number, resolutions, constituencies, before, contagion=None) -> str:
    """Full GM report: resolutions, state, disruption, and support tables.

    ``before`` is a :func:`snapshot` taken at the start of the round; every
    table shows the post-round value with a coloured change against it.
    """
    lines = [f"# GM Round Report — Session {round_number}", "", _LEGEND, ""]

    # ── programme resolutions ────────────────────────────────────────────
    lines.append("## Programme resolutions")
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
            eff.append(_effect_token("G", d.grievance))
        if d.risk:
            eff.append(_effect_token("R", d.risk))
        if d.support_shift:
            eff.append(_effect_token("support", d.support_shift))
        if d.martyr:
            eff.append("**MARTYR**")
        if d.contagion_seed:
            eff.append("**contagion seed**")
        lines.append(f"  - effect: {', '.join(eff) or 'none'}")
    if not resolutions:
        lines.append("- (no programmes resolved this session)")

    # ── constituency state ───────────────────────────────────────────────
    lines += [
        "",
        "## Constituency state",
        "",
        "| Constituency | G | R | P=G-R | T | Gap | State |",
        "|---|---|---|---|---|---|---|",
    ]
    for c in constituencies:
        b = before[c.name]
        lines.append(
            f"| {c.name} "
            f"| {_val(c.grievance, b['grievance'])} "
            f"| {_val(c.risk, b['risk'])} "
            f"| {_val(c.net_pressure, b['net_pressure'])} "
            f"| {_val(c.threshold, b['threshold'])} "
            f"| {_val(c.falsification_gap, b['falsification_gap'])} "
            f"| {_state_cell(c.state.value, b['state'])} |"
        )

    # ── disruption index ─────────────────────────────────────────────────
    idx = sum(c.size_weight for c in constituencies if c.state is ConstituencyState.ACTIVE)
    before_idx = sum(
        c.size_weight for c in constituencies if before[c.name]["state"] == "active"
    )
    band = constants.disruption_band(idx)
    lines += [
        "",
        f"**Disruption Index: {idx}{_delta(idx, before_idx)} — {band['label']}** "
        f"({band['effect']})",
    ]

    # ── support: two wide matrices, true (GM-only) then expressed ────────
    factions = _all_factions(constituencies)
    lines += [
        "",
        "## Constituency support",
        "",
        "Two views of the same allegiances. **True** is the GM-only reality "
        "(changes coloured vs round start); **Expressed** is what each "
        "constituency dares to say in public after preference falsification. "
        "Both are allegiance shares and are distinct from a faction's "
        "*affinity/resonance* — see the docs.",
        "",
        "### True support (GM-only)",
        "",
    ]
    lines += _true_support_table(constituencies, before, factions)
    lines += ["", "### Expressed support (public / falsified)", ""]
    lines += _expressed_support_table(constituencies, factions)
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
