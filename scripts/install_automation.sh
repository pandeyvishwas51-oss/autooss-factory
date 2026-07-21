#!/usr/bin/env bash
# Install launchd job so fleet keeps running while you are logged in
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLIST="$HOME/Library/LaunchAgents/com.pandeyvishwas51.autooss.plist"
LABEL="com.pandeyvishwas51.autooss"

mkdir -p "$HOME/Library/LaunchAgents"
mkdir -p "$ROOT/data/runs"

cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>${ROOT}/scripts/fleet_operator.sh</string>
  </array>
  <key>StartInterval</key>
  <integer>21600</integer>
  <key>RunAtLoad</key>
  <true/>
  <key>WorkingDirectory</key>
  <string>${ROOT}</string>
  <key>StandardOutPath</key>
  <string>${ROOT}/data/runs/launchd.out.log</string>
  <key>StandardErrorPath</key>
  <string>${ROOT}/data/runs/launchd.err.log</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
    <key>HOME</key>
    <string>${HOME}</string>
  </dict>
</dict>
</plist>
EOF

launchctl bootout "gui/$(id -u)/${LABEL}" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
launchctl enable "gui/$(id -u)/${LABEL}"
launchctl kickstart -k "gui/$(id -u)/${LABEL}" || true

echo "Installed LaunchAgent: $PLIST"
echo "Runs every 21600s (6 hours) + at login."
echo "Logs: $ROOT/data/runs/"
echo "To stop: launchctl bootout gui/\$(id -u)/${LABEL}"
