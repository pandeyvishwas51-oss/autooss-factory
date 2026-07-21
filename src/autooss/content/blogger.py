"""
Nightly copy-paste content for Medium + X (Twitter).

Rules:
- One blog per portfolio topic/project
- Include GitHub URL
- No em dashes (U+2014) or en dashes used as em dashes
- Plain ASCII punctuation preferred for paste safety
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from src.autooss.config import settings


@dataclass
class ProjectTopic:
    name: str
    one_liner: str
    problem: str
    audience: str
    github: str
    bullets: List[str]
    hashtags: List[str]


@dataclass
class SocialPack:
    project: str
    github: str
    medium_title: str
    medium_body: str
    x_post: str
    x_thread: List[str] = field(default_factory=list)


PORTFOLIO: List[ProjectTopic] = [
    ProjectTopic(
        name="SentinelScrape",
        one_liner="Adaptive anti-bot fingerprint probing with ML drift detection and A/B patch validation",
        problem="Static stealth libraries lag when Cloudflare or DataDome rotate detection vectors",
        audience="scraper platform engineers and reverse engineering builders",
        github="https://github.com/pandeyvishwas51-oss/sentinelscrape",
        bullets=[
            "Probe fleets vary TLS, canvas, WebGL, and behavior dimensions",
            "Random forest style classifiers surface which signal is blocking you",
            "A/B tests candidate patches against a control profile before deploy",
            "Scrapers pull winners over REST or WebSocket",
        ],
        hashtags=["OpenSource", "WebScraping", "MachineLearning", "Python"],
    ),
    ProjectTopic(
        name="Freshness-Aware RAG",
        one_liner="Re-rank vector search with time decay and source authority, not cosine similarity alone",
        problem="Stale high-similarity chunks beat fresh trusted sources in classic RAG",
        audience="RAG and LLM application engineers",
        github="https://github.com/pandeyvishwas51-oss/freshness-aware-rag",
        bullets=[
            "Composite score blends semantic similarity with freshness and authority",
            "Exponential time decay scales with how often a source updates",
            "Works offline for demos or with Weaviate for production recall",
            "Drop-in re-ranker after any vector store",
        ],
        hashtags=["RAG", "LLM", "OpenSource", "VectorSearch"],
    ),
    ProjectTopic(
        name="SchemaWeaver",
        one_liner="Discover and merge JSON schemas from messy web extractions without predefined fields",
        problem="Most extractors require a schema up front even when fields differ across sites",
        audience="data engineers building multi-site scrapers",
        github="https://github.com/pandeyvishwas51-oss/schemaweaver",
        bullets=[
            "Normalizes synonyms like cost, amount, and sale_price into price",
            "Reports field frequency, confidence, and aliases",
            "Exports a generated Pydantic model for your pipeline",
            "Useful cold-start before LLM extraction at scale",
        ],
        hashtags=["DataEngineering", "WebScraping", "Python", "OpenSource"],
    ),
    ProjectTopic(
        name="ScrapeGuard",
        one_liner="Health monitoring for scrapers: success rate, blocks, captchas, selector drift",
        problem="Teams learn crawlers are broken only after downstream jobs fail",
        audience="scraping SRE and data platform teams",
        github="https://github.com/pandeyvishwas51-oss/scrapeguard",
        bullets=[
            "Record per-request outcomes with latency and error type",
            "Domain health scores with actionable alerts",
            "Detect elevated blocks, captcha spikes, and selector failures",
            "SQLite or in-memory store for local and sidecar use",
        ],
        hashtags=["Observability", "WebScraping", "Python", "OpenSource"],
    ),
    ProjectTopic(
        name="CrawlSync",
        one_liner="Semantic diff for crawl datasets with entity identity, not blind file diffs",
        problem="CSV and JSON diffs miss that the same product may change URL or title",
        audience="catalog and pricing intelligence engineers",
        github="https://github.com/pandeyvishwas51-oss/crawlsync",
        bullets=[
            "Match entities by sku, url, or title",
            "Report added, removed, and field-level changes",
            "Ignore noisy scrape timestamps when comparing",
            "CLI demo included for quick checks",
        ],
        hashtags=["DataDiff", "ETL", "WebScraping", "OpenSource"],
    ),
    ProjectTopic(
        name="AutoOSS Factory",
        one_liner="Discover AI and scraping open-source gaps, score them, scaffold projects, keep the fleet tested",
        problem="Portfolio work stalls without a repeatable discovery and test loop",
        audience="indie OSS builders and AI engineers growing a public portfolio",
        github="https://github.com/pandeyvishwas51-oss/autooss-factory",
        bullets=[
            "Pulls HN and GitHub signals plus curated gap seeds",
            "Scores novelty, demand, feasibility, and portfolio fit",
            "Fleet operator runs pytest across all portfolio repos",
            "Nightly content packs for Medium and X ready to paste",
        ],
        hashtags=["OpenSource", "Automation", "Python", "BuildInPublic"],
    ),
]


def strip_em_dashes(text: str) -> str:
    """Remove em/en dashes and similar punctuation users do not want."""
    text = text.replace("\u2014", " - ")  # em dash
    text = text.replace("\u2013", "-")  # en dash
    text = text.replace("\u2015", " - ")
    text = re.sub(r"\s+-\s+", " - ", text)
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


def _medium_body(p: ProjectTopic) -> str:
    bullets = "\n".join(f"- {b}" for b in p.bullets)
    body = f"""# {p.name}: {p.one_liner}

## Who this is for

If you are one of the {p.audience}, this write-up is for you.

## The problem

{p.problem}.

Most teams paper over that with one-off scripts and hope. That does not scale, and it does not teach the system to improve.

## What I open-sourced

**{p.name}** is public on GitHub:

{p.github}

In one line: {p.one_liner}.

## What it actually does

{bullets}

## Why I built it

I am an AI engineer focused on hyper-scale scraping, reverse engineering, ML, and RAG products. I want my public repos to solve sharp production problems, not wrap a chat API and call it a day.

## Try it

```bash
git clone {p.github}.git
cd {p.name.lower().replace(" ", "-").replace("_", "-")}
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/ -v
```

If the folder name differs, use the repo name from the URL above.

## Closing

If this is useful, star the repo, open an issue with your domain, or fork it and harden it for your stack.

Repo again: {p.github}

#OpenSource #AI #Python
"""
    return strip_em_dashes(body)


def _x_post(p: ProjectTopic) -> str:
    tags = " ".join(f"#{t}" for t in p.hashtags[:4])
    # Keep under ~280 when possible; allow slight overflow for clarity
    post = (
        f"{p.name}: {p.one_liner}.\n\n"
        f"Problem: {p.problem}.\n\n"
        f"Repo: {p.github}\n\n"
        f"{tags}"
    )
    return strip_em_dashes(post)


def _x_thread(p: ProjectTopic) -> List[str]:
    tags = " ".join(f"#{t}" for t in p.hashtags[:3])
    parts = [
        strip_em_dashes(
            f"1/{min(4, 2 + len(p.bullets))} Building in public: {p.name}\n\n{p.one_liner}\n\n{p.github}"
        ),
        strip_em_dashes(f"2/ Problem\n\n{p.problem}."),
    ]
    if p.bullets:
        btxt = "\n".join(f"- {b}" for b in p.bullets[:4])
        parts.append(strip_em_dashes(f"3/ What shipped\n\n{btxt}"))
    parts.append(
        strip_em_dashes(
            f"4/ If you work on this stack, star or fork:\n{p.github}\n\n{tags}"
        )
    )
    return parts


def build_pack(p: ProjectTopic) -> SocialPack:
    return SocialPack(
        project=p.name,
        github=p.github,
        medium_title=strip_em_dashes(f"{p.name}: {p.one_liner}"),
        medium_body=_medium_body(p),
        x_post=_x_post(p),
        x_thread=_x_thread(p),
    )


def generate_nightly_posts(
    *,
    out_dir: Optional[Path] = None,
    topics: Optional[List[ProjectTopic]] = None,
) -> Path:
    """
    Write one Medium + X pack per project into data/content/YYYY-MM-DD/.
    Returns the directory path.
    """
    topics = topics or PORTFOLIO
    day = datetime.utcnow().strftime("%Y-%m-%d")
    out_dir = out_dir or (settings.data_dir / "content" / day)
    out_dir.mkdir(parents=True, exist_ok=True)

    index_lines = [
        f"# Nightly content pack - {day}",
        "",
        "Copy paste ready. No em dashes.",
        "One Medium draft + one X post (and thread) per project.",
        "",
    ]

    all_packs = []
    for p in topics:
        pack = build_pack(p)
        all_packs.append(pack)
        slug = re.sub(r"[^a-z0-9]+", "-", p.name.lower()).strip("-")
        proj_dir = out_dir / slug
        proj_dir.mkdir(parents=True, exist_ok=True)

        (proj_dir / "MEDIUM_TITLE.txt").write_text(pack.medium_title + "\n", encoding="utf-8")
        (proj_dir / "MEDIUM.md").write_text(pack.medium_body + "\n", encoding="utf-8")
        (proj_dir / "X_POST.txt").write_text(pack.x_post + "\n", encoding="utf-8")
        (proj_dir / "X_THREAD.txt").write_text(
            "\n\n---\n\n".join(pack.x_thread) + "\n", encoding="utf-8"
        )
        (proj_dir / "meta.json").write_text(
            json.dumps(asdict(pack), indent=2),
            encoding="utf-8",
        )

        # guard: fail generation if em dash slipped in
        for label, text in [
            ("medium", pack.medium_body),
            ("x", pack.x_post),
            *[(f"thread{i}", t) for i, t in enumerate(pack.x_thread)],
        ]:
            if "\u2014" in text or "\u2013" in text:
                raise ValueError(f"em/en dash found in {p.name} {label}")

        index_lines.append(f"## {p.name}")
        index_lines.append(f"- Folder: `{slug}/`")
        index_lines.append(f"- GitHub: {p.github}")
        index_lines.append(f"- Medium title: {pack.medium_title}")
        index_lines.append(f"- X post: `{slug}/X_POST.txt`")
        index_lines.append("")

    (out_dir / "INDEX.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    (out_dir / "all.json").write_text(
        json.dumps([asdict(p) for p in all_packs], indent=2),
        encoding="utf-8",
    )

    # convenience: single file with everything to scroll
    mega = [f"# ALL POSTS {day}\n"]
    for pack in all_packs:
        mega.append(f"\n\n{'=' * 72}\n# {pack.project}\n{'=' * 72}\n")
        mega.append(f"GitHub: {pack.github}\n")
        mega.append("\n## MEDIUM TITLE\n")
        mega.append(pack.medium_title + "\n")
        mega.append("\n## MEDIUM BODY\n")
        mega.append(pack.medium_body + "\n")
        mega.append("\n## X POST (single)\n")
        mega.append(pack.x_post + "\n")
        mega.append("\n## X THREAD\n")
        mega.append("\n---\n".join(pack.x_thread) + "\n")
    (out_dir / "COPY_PASTE_ALL.md").write_text("".join(mega), encoding="utf-8")

    return out_dir
