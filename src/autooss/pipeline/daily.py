"""Daily AutoOSS loop: discover → score → report → scaffold → optional push."""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from src.autooss.config import settings
from src.autooss.discovery.collect import collect_all_signals
from src.autooss.github_ops.push import init_and_push
from src.autooss.models import DailyRunReport, Opportunity
from src.autooss.scaffold.generator import scaffold_opportunity
from src.autooss.scoring.opportunities import signals_to_opportunities

logger = logging.getLogger(__name__)


def run_daily(
    *,
    scaffold: bool = True,
    push: Optional[bool] = None,
    max_opportunities: Optional[int] = None,
    scaffold_top_n: Optional[int] = None,
    workspace: Optional[Path] = None,
) -> DailyRunReport:
    push = settings.AUTO_PUSH if push is None else push
    max_n = max_opportunities or settings.MAX_OPPORTUNITIES
    top_n = scaffold_top_n if scaffold_top_n is not None else settings.SCAFFOLD_TOP_N
    ws = workspace or settings.workspace
    ws.mkdir(parents=True, exist_ok=True)

    run_id = datetime.utcnow().strftime("%Y%m%d") + "-" + uuid.uuid4().hex[:6]
    report = DailyRunReport(run_id=run_id, started_at=datetime.utcnow())

    # 1) Discover
    signals = collect_all_signals()
    report.signals_count = len(signals)
    report.notes.append(f"signals={len(signals)}")

    # 2) Score
    opps = signals_to_opportunities(signals, max_n=max_n)
    report.opportunities = opps

    # 3) Persist opportunity report
    out_dir = settings.data_dir / "opportunities"
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / f"{run_id}.json"
    report_path.write_text(
        json.dumps(
            {
                "run_id": run_id,
                "opportunities": [o.model_dump(mode="json") for o in opps],
                "signals_count": len(signals),
            },
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )
    report.notes.append(f"wrote {report_path}")

    # Skip names already built
    already = {
        "sentinelscrape",
        "sentinelscraping",
        "freshness-aware-rag",
        "autooss-factory",
    }

    # 4) Scaffold top N not yet existing
    if scaffold:
        built = 0
        for opp in opps:
            if built >= top_n:
                break
            slug = opp.name.lower().split(":")[0].strip().replace(" ", "-")
            slug = "".join(c if c.isalnum() or c == "-" else "-" for c in slug)
            if slug.lower() in already:
                report.notes.append(f"skip existing product {slug}")
                continue
            dest = ws / slug
            if dest.exists() and any(dest.iterdir()):
                report.notes.append(f"skip existing dir {dest}")
                continue
            path = scaffold_opportunity(opp, ws)
            report.scaffolded.append(str(path))
            built += 1

            if push:
                url = init_and_push(
                    path,
                    repo_name=path.name,
                    description=opp.one_liner,
                )
                if url:
                    report.pushed.append(url)
                    report.notes.append(f"pushed {url}")
                else:
                    report.notes.append(f"push failed for {path.name}")

    report.finished_at = datetime.utcnow()
    runs = settings.data_dir / "runs"
    runs.mkdir(parents=True, exist_ok=True)
    (runs / f"{run_id}.json").write_text(
        report.model_dump_json(indent=2),
        encoding="utf-8",
    )
    return report


def format_report(report: DailyRunReport) -> str:
    lines = [
        f"AutoOSS run {report.run_id}",
        f"signals: {report.signals_count}",
        f"opportunities: {len(report.opportunities)}",
        "",
        "Top opportunities:",
    ]
    for i, o in enumerate(report.opportunities[:8], 1):
        lines.append(
            f"  {i}. [{o.total_score:.3f}] {o.name} — {o.one_liner}"
        )
    if report.scaffolded:
        lines.append("")
        lines.append("Scaffolded:")
        for s in report.scaffolded:
            lines.append(f"  - {s}")
    if report.pushed:
        lines.append("")
        lines.append("Pushed:")
        for u in report.pushed:
            lines.append(f"  - {u}")
    if report.notes:
        lines.append("")
        lines.append("Notes: " + "; ".join(report.notes[:12]))
    return "\n".join(lines)
