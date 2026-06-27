#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${WATCHTOWER_PROJECT_DIR:-$PWD}"
REPORT_DATE="${WATCHTOWER_REPORT_DATE:-$(date +%F)}"
REPORT_DIR="$PROJECT_DIR/reports/$REPORT_DATE"

if [[ -f "$REPORT_DIR/latest-summary.txt" ]]; then
  cat "$REPORT_DIR/latest-summary.txt"
elif [[ -f "$REPORT_DIR/latest-summary.md" ]]; then
  cat "$REPORT_DIR/latest-summary.md"
else
  echo "No latest report found: $REPORT_DIR" >&2
  exit 1
fi
