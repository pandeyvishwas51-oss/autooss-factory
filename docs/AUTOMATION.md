# What runs on your behalf (and what does not)

## Unattended automation (installed)

| Job | When | What |
|-----|------|------|
| **LaunchAgent** `com.pandeyvishwas51.autooss` | Every **6 hours** + at login | Fleet tests all portfolio repos, discover gaps, scaffold next idea |
| **Cron** `daily_loop.sh` | **09:00** daily | Discover + scaffold (backup) |
| **Cron** `nightly_content.sh` | **21:30** daily | Medium + X posts for each OSS project (copy paste, no em dashes) |
| **Grok scheduler** | Every **1 day** | Agent session: expand scaffold into real MVP + push if needed |

### Nightly content (what you paste)

```bash
python -m src.autooss.cli content
# writes: data/content/YYYY-MM-DD/
#   COPY_PASTE_ALL.md   <- open this and copy
#   INDEX.md
#   <project>/MEDIUM.md
#   <project>/X_POST.txt
#   <project>/X_THREAD.txt
```

One **Medium** draft and one **X** post (plus thread) **per project**. Each includes the GitHub URL. No em dashes.

## Commands

```bash
cd /Users/vishwaspandey/autooss-factory
source .venv/bin/activate

python -m src.autooss.cli fleet          # test all repos + local load tests
python -m src.autooss.cli cycle          # fleet + discover + scaffold
python -m src.autooss.cli cycle --push   # also push new scaffolds (careful)
python -m src.autooss.cli discover
```

Install / reinstall background runner:

```bash
bash scripts/install_automation.sh
```

## Load testing policy

- Load tests hit **only local health URLs** (`localhost:8000`, `localhost:8001`) if those services are running.
- They **do not** attack third-party websites.
- If services are down, load test is **skipped** (not a failure).

## Hard limits (honest)

| Can run 24/7 without you | Still needs a coding agent / you |
|--------------------------|----------------------------------|
| pytest on all portfolio repos | Deep new features for novel products |
| HN/GitHub trend discovery | Creative architecture decisions |
| Scaffold next project skeleton | Production reverse-engineering depth |
| Local health load tests | Manual product marketing posts |
| Write JSON reports under `data/runs/` | Approving risky `--push` at scale |

**Your Mac must be awake** (or a always-on machine) for LaunchAgent/cron.  
Sleeping Mac = paused automation.

**True 24/7 coding** = this factory + scheduled agent sessions (Grok) or a CI runner with API keys. No tool invents infinite perfect OSS alone.

## Enable auto-push (optional)

```bash
# in .env
AUTO_PUSH=true
# and ensure: gh auth login as pandeyvishwas51-oss
```

Or per-run: `AUTO_PUSH=true bash scripts/fleet_operator.sh`
