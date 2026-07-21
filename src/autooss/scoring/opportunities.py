"""Map trend signals → scored portfolio opportunities."""

from __future__ import annotations

import hashlib
import re
from typing import Dict, List

from src.autooss.models import Opportunity, TrendSignal

# Curated gap templates: when signals match keywords, emit concrete projects
GAP_TEMPLATES: List[Dict] = [
    {
        "name": "schemaweaver",
        "display": "SchemaWeaver",
        "keywords": ["schema", "extract", "structured", "json", "unstructured", "llm extract"],
        "one_liner": "Discover and merge JSON schemas from arbitrary web pages without predefined fields",
        "problem": "Scrapers need schemas up front; unsupervised field discovery across sites is missing in OSS",
        "solution": "Multi-strategy extraction + embedding cluster of field names + Pydantic model export",
        "skill_tags": ["ml", "scraping", "llm"],
        "domain": "ml",
        "mvp_modules": ["extractor", "cluster", "schema_merge", "cli", "api"],
        "tech_stack": ["python", "pydantic", "httpx", "fastapi"],
        "novelty": 0.9,
        "feasibility": 0.85,
        "portfolio": 0.9,
    },
    {
        "name": "scrapeguard",
        "display": "ScrapeGuard",
        "keywords": ["scrape", "scrapy", "crawl", "monitor", "observability", "block", "captcha"],
        "one_liner": "Sentry-like health monitoring for scrapers: success rate, selector drift, block detection",
        "problem": "Teams learn scrapers are broken only after pipelines fail",
        "solution": "Sidecar metrics agent + domain health scores + drift alerts",
        "skill_tags": ["scraping", "ops", "systems"],
        "domain": "scraping",
        "mvp_modules": ["agent", "metrics", "health", "cli", "api"],
        "tech_stack": ["python", "fastapi", "sqlite"],
        "novelty": 0.88,
        "feasibility": 0.9,
        "portfolio": 0.88,
    },
    {
        "name": "crawlsync",
        "display": "CrawlSync",
        "keywords": ["diff", "version", "crawl", "product", "change", "dataset"],
        "one_liner": "Git-like semantic diff for crawl outputs: added/removed/changed entities",
        "problem": "CSV diffs ignore entity identity when URLs/titles drift",
        "solution": "Blocking + fuzzy entity match + field-level change report",
        "skill_tags": ["scraping", "data", "systems"],
        "domain": "scraping",
        "mvp_modules": ["diff", "entity_resolve", "cli", "store"],
        "tech_stack": ["python", "sqlite"],
        "novelty": 0.86,
        "feasibility": 0.9,
        "portfolio": 0.85,
    },
    {
        "name": "ragautopsy",
        "display": "RAGAutopsy",
        "keywords": ["rag", "retrieval", "hallucin", "eval", "langfuse", "observ"],
        "one_liner": "Root-cause diagnosis for bad RAG answers: retrieval vs context vs generation",
        "problem": "Eval tools score quality but don't explain which stage failed",
        "solution": "Per-query autopsy with structured failure fingerprints",
        "skill_tags": ["rag", "llm", "ml"],
        "domain": "rag",
        "mvp_modules": ["diagnoser", "api", "cli"],
        "tech_stack": ["python", "pydantic", "fastapi"],
        "novelty": 0.87,
        "feasibility": 0.88,
        "portfolio": 0.92,
    },
    {
        "name": "extractionnet",
        "display": "ExtractionNet",
        "keywords": ["llm", "extract", "cost", "selector", "learn", "site-specific"],
        "one_liner": "Learn site extractors online: LLM cold-start then cheap heuristic hot path",
        "problem": "LLM extraction on every page is expensive at scale",
        "solution": "Tiered extraction with per-site learned selectors and fallback",
        "skill_tags": ["ml", "llm", "scraping"],
        "domain": "ml",
        "mvp_modules": ["tiers", "store", "cli"],
        "tech_stack": ["python", "beautifulsoup4"],
        "novelty": 0.89,
        "feasibility": 0.8,
        "portfolio": 0.9,
    },
    {
        "name": "freshness-aware-rag",
        "display": "FreshnessAwareRAG",
        "keywords": ["rag", "fresh", "vector", "weaviate", "realtime", "news"],
        "one_liner": "Re-rank RAG retrieval by time decay and source authority",
        "problem": "Stale high-similarity chunks beat fresh news",
        "solution": "Composite score: semantic + freshness × decay × authority",
        "skill_tags": ["rag", "ml"],
        "domain": "rag",
        "mvp_modules": ["retriever", "scoring"],
        "tech_stack": ["python", "numpy"],
        "novelty": 0.7,  # already shipped — lower priority to re-scaffold
        "feasibility": 0.95,
        "portfolio": 0.7,
    },
    {
        "name": "sentinelscrape",
        "display": "SentinelScrape",
        "keywords": ["anti-bot", "fingerprint", "cloudflare", "datadome", "bypass"],
        "one_liner": "Adaptive anti-bot probe fleet with ML drift and A/B patches",
        "problem": "Static stealth patches lag vendor rotation",
        "solution": "Probe matrix → classifier → A/B → fingerprint API",
        "skill_tags": ["scraping", "reverse-eng", "ml"],
        "domain": "reverse-eng",
        "mvp_modules": ["controller", "probe"],
        "tech_stack": ["python", "fastapi", "playwright"],
        "novelty": 0.65,  # already shipped
        "feasibility": 0.9,
        "portfolio": 0.7,
    },
]


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", name.lower()).strip("-")


def _match_score(text: str, keywords: List[str]) -> float:
    t = text.lower()
    hits = sum(1 for k in keywords if k in t)
    return hits / max(len(keywords), 1)


def signals_to_opportunities(signals: List[TrendSignal], max_n: int = 10) -> List[Opportunity]:
    # Always consider full gap catalog; boost by matching live signals
    demand_boost: Dict[str, float] = {t["name"]: 0.0 for t in GAP_TEMPLATES}
    related: Dict[str, List[str]] = {t["name"]: [] for t in GAP_TEMPLATES}

    for sig in signals:
        blob = f"{sig.title} {' '.join(sig.tags)}"
        for tmpl in GAP_TEMPLATES:
            m = _match_score(blob, tmpl["keywords"])
            if m > 0:
                demand_boost[tmpl["name"]] += m * (1.0 + min(sig.score, 500) / 500.0)
                related[tmpl["name"]].append(sig.title[:100])

    opportunities: List[Opportunity] = []
    for tmpl in GAP_TEMPLATES:
        demand = min(1.0, 0.35 + demand_boost[tmpl["name"]] * 0.25)
        # seed signals always present → baseline demand
        if any(s.source == "seed" and tmpl["display"].split(":")[0].lower() in s.title.lower() for s in signals):
            demand = max(demand, 0.75)

        novelty = tmpl["novelty"]
        feasibility = tmpl["feasibility"]
        portfolio = tmpl["portfolio"]
        total = 0.35 * novelty + 0.25 * demand + 0.2 * feasibility + 0.2 * portfolio

        oid = hashlib.sha1(tmpl["name"].encode()).hexdigest()[:10]
        opportunities.append(
            Opportunity(
                id=oid,
                name=tmpl["display"],
                one_liner=tmpl["one_liner"],
                problem=tmpl["problem"],
                solution=tmpl["solution"],
                skill_tags=tmpl["skill_tags"],
                domain=tmpl["domain"],
                novelty_score=novelty,
                demand_score=demand,
                feasibility_score=feasibility,
                portfolio_score=portfolio,
                total_score=round(total, 4),
                related_signals=related[tmpl["name"]][:5],
                mvp_modules=tmpl["mvp_modules"],
                tech_stack=tmpl["tech_stack"],
            )
        )

    opportunities.sort(key=lambda o: o.total_score, reverse=True)
    return opportunities[:max_n]
