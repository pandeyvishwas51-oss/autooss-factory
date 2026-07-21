# Coding agent runbook — AutoOSS daily execution

When the user says “run the factory” or the cron fires, do this **in order**:

## Step 0 — Constraints

- Domain focus: AI, ML, RAG, web scraping, reverse-engineering tooling  
- Do **not** auto-post to HN/Reddit/Twitter  
- Prefer public APIs; no credential stuffing  
- Skip re-scaffolding `sentinelscrape`, `freshness-aware-rag`, `autooss-factory`

## Step 1 — Discover

```bash
cd /Users/vishwaspandey/autooss-factory
source .venv/bin/activate
python -m src.autooss.cli discover
```

Read latest `data/opportunities/*.json`.

## Step 2 — Pick top new opportunity

Choose highest `total_score` whose repo does **not** already exist under  
`https://github.com/pandeyvishwas51-oss/<name>`.

## Step 3 — Build real MVP (not empty scaffold)

If scaffold only exists:

1. Implement core module with tests  
2. `pytest` green  
3. Technical README (no marketing spam)  
4. MIT LICENSE  

Minimum bar: **≥2 unit tests**, working CLI, one-liner problem/solution.

## Step 4 — Push

```bash
gh auth switch --user pandeyvishwas51-oss
# git init, commit, gh repo create --public --push
# gh repo edit --description "..." --add-topic ...
```

## Step 5 — Report to user

Paste:

- Opportunity name + score  
- Repo URL  
- What was implemented  
- Next opportunity in queue  

## Step 6 — Loop tomorrow

Cron / scheduler runs Step 1 daily. Human (or agent session) does Steps 2–5 when available.
