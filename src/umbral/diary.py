# ╔══════════════════════════════════════════════════════════════════╗
# ║  Umbral — diary                                                  ║
# ║  « the append-only ledger »                                      ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  Every action, grade, roll, delta, and tip recorded as JSONL,    ║
# ║  so a round can be audited or replayed.                          ║
# ╚══════════════════════════════════════════════════════════════════╝


"""Append-only JSONL ledger of every action, grade, roll, and state change."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


class Diary:
    """Append-only event log; one JSON object per line."""

    def __init__(self, path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, event: dict) -> None:
        record = {"ts": datetime.now(timezone.utc).isoformat(), **event}
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    def log_resolution(self, resolution, round_number: int) -> None:
        g = resolution.graded
        p = g.programme
        self.log(
            {
                "kind": "resolution",
                "round": round_number,
                "faction": p.faction,
                "target": p.target,
                "lever": p.lever.value,
                "q_score": g.q_score,
                "q_tier": g.q_tier.value,
                "resonance": g.resonance.value,
                "static_modifier": g.static_modifier,
                "dice": resolution.dice,
                "total": resolution.total,
                "band": resolution.band.value,
                "deltas": {
                    "grievance": resolution.deltas.grievance,
                    "risk": resolution.deltas.risk,
                    "support_shift": resolution.deltas.support_shift,
                    "falsification_gap": resolution.deltas.falsification_gap,
                    "martyr": resolution.deltas.martyr,
                },
            }
        )

    def log_tipping(self, round_number: int, tipped: list[str], disruption: int) -> None:
        self.log(
            {
                "kind": "tipping",
                "round": round_number,
                "tipped": tipped,
                "disruption_index": disruption,
            }
        )
