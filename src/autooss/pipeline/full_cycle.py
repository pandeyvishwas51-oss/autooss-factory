"""
Full unattended cycle used by cron:

1) Fleet tests all portfolio repos
2) Discover + score opportunities
3) Scaffold next gap project (optional push)
4) Re-test fleet (if something new was scaffolded)
5) Persist combined status report
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from src.autooss.config import settings
from src.autooss.fleet.operator import format_fleet_report, run_fleet
from src.autooss.pipeline.daily import format_report, run_daily

logger = logging.getLogger(__name__)


def run_full_cycle(
    *,
    push: bool = False,
    scaffold_top_n: int = 1,
    load_test: bool = True,
) -> Dict[str, Any]:
    started = datetime.utcnow().isoformat() + "Z"

    fleet_before = run_fleet(load_test=load_test)
    daily = run_daily(scaffold=True, push=push, scaffold_top_n=scaffold_top_n)

    fleet_after = None
    if daily.scaffolded:
        # new code appeared — re-run tests on fleet (scaffolds may live in workspace)
        fleet_after = run_fleet(load_test=False)

    combined = {
        "started": started,
        "finished": datetime.utcnow().isoformat() + "Z",
        "fleet_before": fleet_before.to_dict(),
        "daily": json.loads(daily.model_dump_json()),
        "fleet_after": fleet_after.to_dict() if fleet_after else None,
        "summary": {
            "all_tests_green": fleet_before.all_green,
            "opportunities": len(daily.opportunities),
            "scaffolded": daily.scaffolded,
            "pushed": daily.pushed,
        },
    }

    path = (
        settings.data_dir
        / "runs"
        / f"full-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.json"
    )
    path.write_text(json.dumps(combined, indent=2, default=str), encoding="utf-8")
    combined["report_path"] = str(path)
    return combined


def format_full_cycle(combined: Dict[str, Any]) -> str:
    lines = [
        "=" * 60,
        "AUTOSS FULL CYCLE",
        "=" * 60,
        "",
        format_fleet_report(
            # reconstruct minimal view from dict for display
            __import__(
                "src.autooss.fleet.operator", fromlist=["FleetReport", "RepoTestResult", "LoadTestResult"]
            ).FleetReport(
                run_id=combined["fleet_before"]["run_id"],
                started_at=combined["fleet_before"]["started_at"],
                finished_at=combined["fleet_before"].get("finished_at", ""),
                all_green=combined["fleet_before"]["all_green"],
                notes=combined["fleet_before"].get("notes", []),
                repo_results=[
                    __import__(
                        "src.autooss.fleet.operator", fromlist=["RepoTestResult"]
                    ).RepoTestResult(**r)
                    for r in combined["fleet_before"]["repo_results"]
                ],
                load_results=[
                    __import__(
                        "src.autooss.fleet.operator", fromlist=["LoadTestResult"]
                    ).LoadTestResult(**r)
                    for r in combined["fleet_before"].get("load_results", [])
                ],
            )
        ),
        "",
        "Discovery / scaffold:",
        f"  opportunities: {combined['summary']['opportunities']}",
        f"  scaffolded: {combined['summary']['scaffolded']}",
        f"  pushed: {combined['summary']['pushed']}",
        f"  report: {combined.get('report_path')}",
        "",
        "Note: Full novel product coding still needs an agent session;",
        "this cycle keeps tests green, discovers gaps, scaffolds next work.",
    ]
    return "\n".join(lines)
