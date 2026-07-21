"""Portfolio repos the fleet tests and tracks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PortfolioRepo:
    name: str
    local_path: str
    github: str
    health_url: Optional[str] = None  # optional local service to load-test
    test_cmd: str = "pytest tests/ -q --tb=line"
    domain: str = "ai-ml-scraping"


def default_catalog(home: str = "/Users/vishwaspandey") -> List[PortfolioRepo]:
    return [
        PortfolioRepo(
            name="autooss-factory",
            local_path=f"{home}/autooss-factory",
            github="https://github.com/pandeyvishwas51-oss/autooss-factory",
        ),
        PortfolioRepo(
            name="sentinelscrape",
            local_path=f"{home}/sentinelscraping",
            github="https://github.com/pandeyvishwas51-oss/sentinelscrape",
            health_url="http://127.0.0.1:8000/health",
        ),
        PortfolioRepo(
            name="freshness-aware-rag",
            local_path=f"{home}/freshness-aware-rag",
            github="https://github.com/pandeyvishwas51-oss/freshness-aware-rag",
            health_url="http://127.0.0.1:8001/health",
        ),
        PortfolioRepo(
            name="schemaweaver",
            local_path=f"{home}/schemaweaver",
            github="https://github.com/pandeyvishwas51-oss/schemaweaver",
        ),
        PortfolioRepo(
            name="scrapeguard",
            local_path=f"{home}/scrapeguard",
            github="https://github.com/pandeyvishwas51-oss/scrapeguard",
        ),
        PortfolioRepo(
            name="crawlsync",
            local_path=f"{home}/crawlsync",
            github="https://github.com/pandeyvishwas51-oss/crawlsync",
        ),
    ]
