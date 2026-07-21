# AutoOSS Factory

Discover gaps in **AI / ML / web scraping**, score portfolio opportunities, scaffold projects, and optionally push to GitHub.

This is the **automation layer** around your open-source factory — not a spam bot.

## What it does (daily loop)

```text
1. Collect signals   HN (filtered) + GitHub search + curated seed gaps
2. Score             novelty × demand × feasibility × portfolio fit
3. Report            data/opportunities/<run>.json
4. Scaffold          top N projects under ~/autooss-workspace/
5. Push (optional)   gh repo create --push when --push / AUTO_PUSH=true
```

**Promotion (HN/Reddit/Twitter) is intentionally NOT auto-posted.**  
The factory writes opportunities and code; you publish when ready.

## Install

```bash
cd autooss-factory
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
# optional: GITHUB_TOKEN for higher GitHub API limits + push
```

## Commands

```bash
# Discover + score only
python -m src.autooss.cli discover

# Full daily: discover, score, scaffold 1 project
python -m src.autooss.cli daily --top 1

# Also push scaffold to GitHub (needs gh auth)
python -m src.autooss.cli daily --top 1 --push
```

## Run on your behalf (fleet + schedule)

```bash
# Test ALL portfolio repos (+ local load tests if services up)
python -m src.autooss.cli fleet

# Full cycle: fleet tests + discover gaps + scaffold next idea
python -m src.autooss.cli cycle

# Install background runner (every 6 hours while Mac is logged in)
bash scripts/install_automation.sh
```

Details: [docs/AUTOMATION.md](./docs/AUTOMATION.md)

Cron backup at 09:00: `scripts/daily_loop.sh` (already installable via crontab).

## Already shipped portfolio (manual)

| Repo | Focus |
|------|--------|
| [sentinelscrape](https://github.com/pandeyvishwas51-oss/sentinelscrape) | Anti-bot probe + ML + A/B |
| [freshness-aware-rag](https://github.com/pandeyvishwas51-oss/freshness-aware-rag) | Freshness re-rank for RAG |
| [schemaweaver](https://github.com/pandeyvishwas51-oss/schemaweaver) | Schema discovery |
| [scrapeguard](https://github.com/pandeyvishwas51-oss/scrapeguard) | Scraper health |
| [crawlsync](https://github.com/pandeyvishwas51-oss/crawlsync) | Crawl dataset diff |

## Safety

- Uses public APIs (HN Firebase, GitHub Search) with polite delays  
- Respects rate limits; set `GITHUB_TOKEN`  
- Does **not** auto-spam social networks  
- Scaffolds are starting points — expand real code before calling it “done”

## License

MIT
