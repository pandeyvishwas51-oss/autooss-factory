"""CLI: autooss daily | discover | report"""

from __future__ import annotations

import argparse
import logging
import sys

from rich.console import Console

from src.autooss.pipeline.daily import format_report, run_daily

console = Console()


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(prog="autooss", description="AutoOSS Factory")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_daily = sub.add_parser("daily", help="Full daily loop")
    p_daily.add_argument("--no-scaffold", action="store_true")
    p_daily.add_argument("--push", action="store_true", help="Push scaffolds to GitHub")
    p_daily.add_argument("--top", type=int, default=None, help="Scaffold top N")
    p_daily.add_argument("--max", type=int, default=None, help="Max opportunities")

    sub.add_parser("discover", help="Discover + score only (no scaffold)")

    args = parser.parse_args(argv)

    if args.cmd == "daily":
        report = run_daily(
            scaffold=not args.no_scaffold,
            push=args.push if args.push else False,
            scaffold_top_n=args.top,
            max_opportunities=args.max,
        )
        console.print(format_report(report))
        return 0

    if args.cmd == "discover":
        report = run_daily(scaffold=False, push=False)
        console.print(format_report(report))
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
