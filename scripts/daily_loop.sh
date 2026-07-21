#!/usr/bin/env bash
# Cron-friendly daily AutoOSS loop
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
if [[ -f .venv/bin/activate ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
# Discover + score + scaffold 1 project (set AUTO_PUSH=true in .env to push)
python -m src.autooss.cli daily --top 1 "$@" | tee -a data/runs/cron.log
