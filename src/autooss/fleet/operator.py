"""
Fleet operator: test all portfolio repos + optional local load checks + report.

This is what cron runs so the portfolio stays green without manual babysitting.
"""

from __future__ import annotations

import json
import logging
import os
import statistics
import subprocess
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import httpx

from src.autooss.config import settings
from src.autooss.fleet.catalog import PortfolioRepo, default_catalog

logger = logging.getLogger(__name__)


@dataclass
class RepoTestResult:
    name: str
    path: str
    ok: bool
    exit_code: int
    duration_s: float
    output_tail: str = ""
    error: str = ""


@dataclass
class LoadTestResult:
    url: str
    ok: bool
    requests: int
    success: int
    rps: float
    p50_ms: float
    p95_ms: float
    errors: int
    note: str = ""


@dataclass
class FleetReport:
    run_id: str
    started_at: str
    finished_at: str = ""
    repo_results: List[RepoTestResult] = field(default_factory=list)
    load_results: List[LoadTestResult] = field(default_factory=list)
    all_green: bool = False
    notes: List[str] = field(default_factory=list)

    def to_dict(self):
        return {
            "run_id": self.run_id,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "all_green": self.all_green,
            "notes": self.notes,
            "repo_results": [asdict(r) for r in self.repo_results],
            "load_results": [asdict(r) for r in self.load_results],
        }


def _ensure_venv_and_test(repo: PortfolioRepo, timeout: int = 300) -> RepoTestResult:
    path = Path(repo.local_path)
    if not path.exists():
        return RepoTestResult(
            name=repo.name,
            path=repo.local_path,
            ok=False,
            exit_code=127,
            duration_s=0.0,
            error="path_missing",
        )

    venv_py = path / ".venv" / "bin" / "python"
    t0 = time.time()
    try:
        if not venv_py.exists():
            subprocess.run(
                ["python3", "-m", "venv", ".venv"],
                cwd=str(path),
                check=True,
                capture_output=True,
                text=True,
                timeout=120,
            )
            subprocess.run(
                [str(venv_py), "-m", "pip", "install", "-e", ".[dev]", "-q"],
                cwd=str(path),
                check=False,
                capture_output=True,
                text=True,
                timeout=300,
            )
            # fallback without optional
            if not (path / ".venv" / "bin" / "pytest").exists():
                subprocess.run(
                    [str(venv_py), "-m", "pip", "install", "-e", ".", "pytest", "-q"],
                    cwd=str(path),
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=300,
                )

        env = os.environ.copy()
        env["PYTHONPATH"] = str(path)
        proc = subprocess.run(
            [str(venv_py), "-m", "pytest", "tests/", "-q", "--tb=line"],
            cwd=str(path),
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        tail = (proc.stdout or "")[-1500:] + (proc.stderr or "")[-500:]
        return RepoTestResult(
            name=repo.name,
            path=repo.local_path,
            ok=proc.returncode == 0,
            exit_code=proc.returncode,
            duration_s=round(time.time() - t0, 2),
            output_tail=tail,
        )
    except subprocess.TimeoutExpired:
        return RepoTestResult(
            name=repo.name,
            path=repo.local_path,
            ok=False,
            exit_code=124,
            duration_s=round(time.time() - t0, 2),
            error="timeout",
        )
    except Exception as e:
        return RepoTestResult(
            name=repo.name,
            path=repo.local_path,
            ok=False,
            exit_code=1,
            duration_s=round(time.time() - t0, 2),
            error=str(e),
        )


def load_test_url(
    url: str,
    *,
    requests_n: int = 50,
    concurrency: int = 10,
    timeout: float = 2.0,
) -> LoadTestResult:
    """
    Light load test against YOUR local health endpoints only.
    Skips cleanly if service is down (does not fail the fleet).
    """
    latencies: List[float] = []
    success = 0
    errors = 0

    def one(_: int):
        nonlocal success, errors
        try:
            t0 = time.perf_counter()
            r = httpx.get(url, timeout=timeout)
            ms = (time.perf_counter() - t0) * 1000
            if r.status_code < 500:
                success += 1
                latencies.append(ms)
            else:
                errors += 1
        except Exception:
            errors += 1

    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=concurrency) as ex:
        futs = [ex.submit(one, i) for i in range(requests_n)]
        for f in as_completed(futs):
            _ = f.result()
    elapsed = max(time.perf_counter() - t0, 1e-6)

    if not latencies and errors:
        return LoadTestResult(
            url=url,
            ok=True,  # service optional
            requests=requests_n,
            success=0,
            rps=0.0,
            p50_ms=0.0,
            p95_ms=0.0,
            errors=errors,
            note="service_down_skipped",
        )

    latencies.sort()
    p50 = latencies[len(latencies) // 2] if latencies else 0.0
    p95 = latencies[int(len(latencies) * 0.95)] if latencies else 0.0
    return LoadTestResult(
        url=url,
        ok=errors < requests_n * 0.5,
        requests=requests_n,
        success=success,
        rps=round(success / elapsed, 1),
        p50_ms=round(p50, 1),
        p95_ms=round(p95, 1),
        errors=errors,
        note="ok" if success else "no_success",
    )


def run_fleet(
    *,
    catalog: Optional[List[PortfolioRepo]] = None,
    load_test: bool = True,
    load_requests: int = 40,
) -> FleetReport:
    catalog = catalog or default_catalog()
    run_id = datetime.utcnow().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:4]
    report = FleetReport(run_id=run_id, started_at=datetime.utcnow().isoformat() + "Z")

    for repo in catalog:
        logger.info("Testing %s ...", repo.name)
        result = _ensure_venv_and_test(repo)
        report.repo_results.append(result)
        status = "PASS" if result.ok else "FAIL"
        report.notes.append(f"{repo.name}: {status} ({result.duration_s}s)")

    if load_test:
        urls = [r.health_url for r in catalog if r.health_url]
        for url in urls:
            logger.info("Load test %s ...", url)
            report.load_results.append(
                load_test_url(url, requests_n=load_requests, concurrency=8)
            )

    report.all_green = all(r.ok for r in report.repo_results)
    report.finished_at = datetime.utcnow().isoformat() + "Z"

    out = settings.data_dir / "runs" / f"fleet-{run_id}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
    report.notes.append(f"report={out}")
    return report


def format_fleet_report(report: FleetReport) -> str:
    lines = [
        f"FLEET RUN {report.run_id}",
        f"all_green={report.all_green}",
        "",
        "Unit / integration tests:",
    ]
    for r in report.repo_results:
        mark = "OK" if r.ok else "FAIL"
        lines.append(f"  [{mark}] {r.name:22} {r.duration_s:>6.1f}s  exit={r.exit_code}")
        if r.error:
            lines.append(f"         error: {r.error}")
    if report.load_results:
        lines.append("")
        lines.append("Local load tests (health endpoints only):")
        for lt in report.load_results:
            lines.append(
                f"  {lt.url}  success={lt.success}/{lt.requests}  "
                f"rps={lt.rps}  p50={lt.p50_ms}ms  p95={lt.p95_ms}ms  "
                f"note={lt.note}"
            )
    lines.append("")
    lines.append("Notes: " + "; ".join(report.notes[-8:]))
    return "\n".join(lines)
