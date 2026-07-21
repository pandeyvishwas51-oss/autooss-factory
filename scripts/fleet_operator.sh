#!/usr/bin/env bash
# Unattended fleet: test all repos + discover + scaffold
# Cron every 6h (Mac must be awake / not sleeping)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p data/runs

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
LOG="data/runs/operator-${STAMP}.log"

{
  echo "==== AutoOSS operator $STAMP ===="
  # Full cycle: tests + discovery + scaffold
  # Add --push only if you want auto GitHub repos (needs gh auth)
  if [[ "${AUTO_PUSH:-false}" == "true" ]]; then
    python -m src.autooss.cli cycle --top 1 --push
  else
    python -m src.autooss.cli cycle --top 1
  fi
  echo "==== done $STAMP ===="
} 2>&1 | tee -a "$LOG" | tee -a data/runs/cron.log

exit ${PIPESTATUS[0]}
