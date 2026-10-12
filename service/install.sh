#!/usr/bin/env bash
# Install (or reinstall) the project-launcher systemd user service.
# Safe to run again: it overwrites the unit file and restarts the service.
set -euo pipefail

SERVICE=project-launcher.service
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$HERE")"
UNIT_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"

mkdir -p "$UNIT_DIR"
# Point ExecStart at wherever this repo actually lives.
sed "s|@REPO_DIR@|$REPO_DIR|g" "$HERE/$SERVICE" > "$UNIT_DIR/$SERVICE"

systemctl --user daemon-reload
systemctl --user enable "$SERVICE"
systemctl --user restart "$SERVICE"

echo "Installed $UNIT_DIR/$SERVICE"
echo "Dashboard: http://127.0.0.1:8765"
