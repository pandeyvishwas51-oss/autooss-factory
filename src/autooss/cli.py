"""CLI: autooss daily | discover | fleet | cycle"""

from __future__ import annotations

import argparse
import logging
import sys

from rich.console import Console

from src.autooss.content.blogger import generate_nightly_posts
from src.autooss.fleet.operator import format_fleet_report, run_fleet
from src.autooss.pipeline.daily import format_report, run_daily
from src.autooss.pipeline.full_cycle import format_full_cycle, run_full_cycle

console = Console()


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(prog="autooss", description="AutoOSS Factory")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_daily = sub.add_parser("daily", help="Discover + score + scaffold")
    p_daily.add_argument("--no-scaffold", action="store_true")
    p_daily.add_argument("--push", action="store_true", help="Push scaffolds to GitHub")
    p_daily.add_argument("--top", type=int, default=None, help="Scaffold top N")
    p_daily.add_argument("--max", type=int, default=None, help="Max opportunities")

    sub.add_parser("discover", help="Discover + score only (no scaffold)")

    p_fleet = sub.add_parser("fleet", help="Test all portfolio repos + local load tests")
    p_fleet.add_argument("--no-load", action="store_true")
    p_fleet.add_argument("--load-requests", type=int, default=40)

    p_cycle = sub.add_parser(
        "cycle",
        help="Full unattended cycle: fleet tests + discover + scaffold",
    )
    p_cycle.add_argument("--push", action="store_true")
    p_cycle.add_argument("--top", type=int, default=1)
    p_cycle.add_argument("--no-load", action="store_true")

    sub.add_parser(
        "content",
        help="Generate nightly Medium + X posts (one blog per project, copy paste)",
    )

    args = parser.parse_args(argv)

    if args.cmd == "daily":
        report = run_daily(
            scaffold=not args.no_scaffold,
            push=bool(args.push),
            scaffold_top_n=args.top,
            max_opportunities=args.max,
        )
        console.print(format_report(report))
        return 0

    if args.cmd == "discover":
        report = run_daily(scaffold=False, push=False)
        console.print(format_report(report))
        return 0

    if args.cmd == "fleet":
        report = run_fleet(
            load_test=not args.no_load,
            load_requests=args.load_requests,
        )
        console.print(format_fleet_report(report))
        return 0 if report.all_green else 1

    if args.cmd == "cycle":
        combined = run_full_cycle(
            push=bool(args.push),
            scaffold_top_n=args.top,
            load_test=not args.no_load,
        )
        console.print(format_full_cycle(combined))
        return 0 if combined["summary"]["all_tests_green"] else 1

    if args.cmd == "content":
        out = generate_nightly_posts()
        console.print(f"Nightly content written to:\n  {out}")
        console.print(f"  Open: {out / 'COPY_PASTE_ALL.md'}")
        console.print(f"  Index: {out / 'INDEX.md'}")
        console.print("One Medium draft + one X post per project. No em dashes.")
        return 0

    return 1



if __name__ == "__main__":
    sys.exit(main())
