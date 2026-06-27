#!/usr/bin/env bash
set -euo pipefail

LABEL="${WATCHTOWER_LAUNCHD_LABEL:-com.praxis.github-watchtower}"
USER_ID="${UID:-$(id -u)}"
PLIST="${WATCHTOWER_PLIST_PATH:-$HOME/Library/LaunchAgents/$LABEL.plist}"

echo "Plist: $PLIST"
if [[ -f "$PLIST" ]]; then
  plutil -lint "$PLIST"
else
  echo "Missing plist: $PLIST" >&2
fi

echo
echo "launchctl status:"
launchctl print "gui/$USER_ID/$LABEL"
