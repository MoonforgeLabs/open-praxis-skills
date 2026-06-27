#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${WATCHTOWER_PROJECT_DIR:-$PWD}"
CONFIG_FILE="${WATCHTOWER_CONFIG:-repos.yaml}"
cd "$PROJECT_DIR"

if [[ ! -x ".venv/bin/python" ]]; then
  echo "Missing .venv/bin/python in $PROJECT_DIR. Initialize the watchtower project first." >&2
  exit 1
fi

if [[ ! -f "scripts/watch.py" ]]; then
  echo "Missing scripts/watch.py in $PROJECT_DIR." >&2
  exit 1
fi

exec .venv/bin/python scripts/watch.py --config "$CONFIG_FILE" --mode local --sync-forks --scan-forks "$@"
