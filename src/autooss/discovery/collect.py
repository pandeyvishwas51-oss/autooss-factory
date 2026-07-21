"""Trend collectors — public APIs only, polite rate limits."""

from __future__ import annotations

import logging
import time
from typing import List

import httpx

from src.autooss.config import settings
from src.autooss.models import TrendSignal

logger = logging.getLogger(__name__)

# Seed catalog of known gaps (portfolio queue) always available offline
SEED_OPPORTUNITIES = [
    TrendSignal(
        source="seed",
        title="SchemaWeaver: unsupervised JSON schema discovery from web pages",
        url="https://github.com/topics/web-scraping",
        score=90,
        tags=["ml", "extraction", "schema", "scraping"],
    ),
    TrendSignal(
        source="seed",
        title="ScrapeGuard: observability and canary monitoring for scrapers",
        url="https://github.com/topics/scrapy",
        score=88,
        tags=["scraping", "observability", "ops"],
    ),
    TrendSignal(
        source="seed",
        title="CrawlSync: semantic version control / diff for crawl datasets",
        url="https://github.com/topics/web-scraping",
        score=85,
        tags=["scraping", "data", "diff"],
    ),
    TrendSignal(
        source="seed",
        title="ExtractionNet: self-improving site extractors cutting LLM cost",
        url="https://github.com/topics/llm",
        score=84,
        tags=["ml", "llm", "extraction"],
    ),
    TrendSignal(
        source="seed",
        title="RAGAutopsy: root-cause analysis for production RAG failures",
        url="https://github.com/topics/rag",
        score=83,
        tags=["rag", "llm", "observability"],
    ),
    TrendSignal(
        source="seed",
        title="RateMap: collaborative anti-bot site temperament intelligence",
        url="https://github.com/topics/web-scraping",
        score=80,
        tags=["scraping", "anti-bot"],
    ),
]


def collect_hackernews(limit: int | None = None) -> List[TrendSignal]:
    limit = limit or settings.HN_TOP_N
    signals: List[TrendSignal] = []
    try:
        with httpx.Client(timeout=20.0) as client:
            ids = client.get(
                "https://hacker-news.firebaseio.com/v0/topstories.json"
            ).json()[: limit * 2]
            keywords = (
                "scrape",
                "scraping",
                "rag",
                "llm",
                "crawl",
                "browser",
                "vector",
                "openai",
                "agent",
                "data pipeline",
                "embedding",
            )
            for i, story_id in enumerate(ids):
                if len(signals) >= limit:
                    break
                item = client.get(
                    f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                ).json()
                if not item or item.get("type") != "story":
                    continue
                title = item.get("title") or ""
                low = title.lower()
                if not any(k in low for k in keywords):
                    continue
                signals.append(
                    TrendSignal(
                        source="hn",
                        title=title,
                        url=item.get("url") or f"https://news.ycombinator.com/item?id={story_id}",
                        score=float(item.get("score") or 0),
                        tags=["hn"],
                        raw={"id": story_id, "by": item.get("by")},
                    )
                )
                time.sleep(0.05)
    except Exception as e:
        logger.warning("HN collect failed: %s", e)
    return signals


def collect_github_search() -> List[TrendSignal]:
    """GitHub search for hot repos (unauthenticated = low rate limit)."""
    signals: List[TrendSignal] = []
    token = settings.GITHUB_TOKEN
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    queries = [q.strip() for q in settings.GITHUB_SEARCH_QUERIES.split(",") if q.strip()]
    try:
        with httpx.Client(timeout=25.0, headers=headers) as client:
            for q in queries[:5]:
                # recently updated / stars
                resp = client.get(
                    "https://api.github.com/search/repositories",
                    params={
                        "q": f"{q} stars:>50",
                        "sort": "updated",
                        "order": "desc",
                        "per_page": 5,
                    },
                )
                if resp.status_code != 200:
                    logger.warning("GitHub search %s → %s", q, resp.status_code)
                    continue
                data = resp.json()
                for repo in data.get("items", []):
                    signals.append(
                        TrendSignal(
                            source="github",
                            title=f"{repo['full_name']}: {repo.get('description') or ''}"[:200],
                            url=repo.get("html_url", ""),
                            score=float(repo.get("stargazers_count") or 0),
                            tags=["github", q.replace(" ", "-")],
                            raw={
                                "stars": repo.get("stargazers_count"),
                                "language": repo.get("language"),
                            },
                        )
                    )
                time.sleep(0.8 if not token else 0.2)
    except Exception as e:
        logger.warning("GitHub collect failed: %s", e)
    return signals


def collect_all_signals() -> List[TrendSignal]:
    signals: List[TrendSignal] = list(SEED_OPPORTUNITIES)
    signals.extend(collect_hackernews())
    signals.extend(collect_github_search())
    # de-dupe by title
    seen = set()
    unique: List[TrendSignal] = []
    for s in signals:
        key = s.title.lower()[:80]
        if key in seen:
            continue
        seen.add(key)
        unique.append(s)
    logger.info("Collected %d trend signals", len(unique))
    return unique
