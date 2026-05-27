# ╔══════════════════════════════════════════════════════════════════╗
# ║  Umbral — state                                                  ║
# ║  « save and restore »                                            ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  JSON (de)serialisation of the game state between rounds.        ║
# ╚══════════════════════════════════════════════════════════════════╝


"""JSON (de)serialisation of the game state between rounds."""
from __future__ import annotations

import json
from pathlib import Path

from umbral.models import Constituency, ConstituencyState


def state_to_dict(constituencies: list[Constituency], round_number: int) -> dict:
    return {
        "round": round_number,
        "constituencies": [
            {
                "name": c.name,
                "size_weight": c.size_weight,
                "grievance": c.grievance,
                "risk": c.risk,
                "threshold": c.threshold,
                "action_mode": c.action_mode,
                "state": c.state.value,
                "falsification_gap": c.falsification_gap,
                "true_support": c.true_support,
            }
            for c in constituencies
        ],
    }


def save_state(constituencies: list[Constituency], round_number: int, path) -> None:
    Path(path).write_text(
        json.dumps(
            state_to_dict(constituencies, round_number), indent=2, ensure_ascii=False
        ),
        encoding="utf-8",
    )


def load_state(path) -> tuple[list[Constituency], int]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    people = [
        Constituency(
            name=d["name"],
            size_weight=int(d["size_weight"]),
            grievance=float(d["grievance"]),
            risk=float(d["risk"]),
            threshold=float(d["threshold"]),
            action_mode=d["action_mode"],
            state=ConstituencyState(d["state"]),
            falsification_gap=float(d["falsification_gap"]),
            true_support=dict(d["true_support"]),
        )
        for d in data["constituencies"]
    ]
    return people, int(data["round"])
