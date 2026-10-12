#!/usr/bin/env bash
# Install (or reinstall) the project-launcher background service so the dashboard
# starts at login: a systemd user service on Linux, a launchd LaunchAgent on macOS.
# Safe to run again: it overwrites the installed file and restarts the service.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$HERE")"
# Services start with a minimal PATH, so bake in the full python3 path found now.
PYTHON="$(command -v python3)" || { echo "python3 not found" >&2; exit 1; }

render() {  # render <template> <dest>
  sed -e "s|@REPO_DIR@|$REPO_DIR|g" -e "s|@PYTHON@|$PYTHON|g" -e "s|@HOME@|$HOME|g" "$1" > "$2"
}

case "$(uname -s)" in
  Linux)
    SERVICE=project-launcher.service
    UNIT_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
    mkdir -p "$UNIT_DIR"
    render "$HERE/linux/$SERVICE" "$UNIT_DIR/$SERVICE"
    systemctl --user daemon-reload
    systemctl --user enable "$SERVICE"
    systemctl --user restart "$SERVICE"
    echo "Installed $UNIT_DIR/$SERVICE"
    ;;
  Darwin)
    LABEL=local.project-launcher
    PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
    mkdir -p "$HOME/Library/LaunchAgents" "$HOME/Library/Logs"
    render "$HERE/macos/$LABEL.plist" "$PLIST"
    launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true  # stop old copy if loaded
    launchctl bootstrap "gui/$(id -u)" "$PLIST"
    echo "Installed $PLIST"
    ;;
  *)
    echo "Unsupported OS: $(uname -s)" >&2; exit 1
    ;;
esac

echo "Dashboard: http://127.0.0.1:8765"
