#!/usr/bin/env bash
# Nightly Medium + X copy-paste packs for all portfolio projects
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p data/runs data/content

if [[ ! -f .venv/bin/activate ]]; then
  python3 -m venv .venv
  # shellcheck disable=SC1091
  source .venv/bin/activate
  pip install -U pip -q
  pip install -e ".[dev]" -q
else
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
{
  echo "==== nightly content $STAMP ===="
  python -m src.autooss.cli content
  DAY="$(date -u +%Y-%m-%d)"
  echo "Paste file: $ROOT/data/content/$DAY/COPY_PASTE_ALL.md"
  echo "==== done content $STAMP ===="
} 2>&1 | tee -a "data/runs/content-${STAMP}.log" | tee -a data/runs/cron.log
