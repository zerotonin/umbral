# ╔══════════════════════════════════════════════════════════════════╗
# ║  Umbral — cli                                                    ║
# ║  « the entry point »                                             ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  umbral init  -> fresh starting state                            ║
# ║  umbral run-round  -> resolve a session and write reports        ║
# ╚══════════════════════════════════════════════════════════════════╝


"""Command-line entry point for the umbral engine."""
from __future__ import annotations

import argparse
from pathlib import Path

from umbral import engine


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="umbral", description="Mass-response engine for The Fate of Abuc."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="write a fresh starting state from data/")
    p_init.add_argument("--out", type=Path, default=Path("state.json"))

    p_run = sub.add_parser("run-round", help="resolve one session and write reports")
    p_run.add_argument("--state", type=Path, required=True)
    p_run.add_argument("--programmes", type=Path, required=True)
    p_run.add_argument("--grades", type=Path, required=True)
    p_run.add_argument("--outdir", type=Path, required=True)
    p_run.add_argument("--seed", type=int, default=None)
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "init":
        engine.init_state(args.out)
        print(f"wrote starting state to {args.out}")
    elif args.command == "run-round":
        summary = engine.run_round(
            args.state, args.programmes, args.grades, args.outdir, seed=args.seed
        )
        print(
            f"round {summary['round']} resolved; tipped={summary['tipped']}; "
            f"disruption={summary['disruption_index']}; outputs in {args.outdir}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
