
## 2026-10-12 05:50
Built the first prototype with Claude: Python stdlib server (server.py) + index.html. Cards for each folder in ~/Projects, Resume Work launches `konsole --workdir`. Next: try it out, decide on the "visual map" layout, maybe run it as a systemd user service.

## 2026-10-12 06:10
Turned the prototype into a real project:
- Runs at login as a systemd user service; service/install.sh installs it (template in service/linux)
- Added macOS support: terminal command and projects dir configurable via config.json (Terminal.app default on Mac), launchd LaunchAgent in service/macos, install.sh detects the OS
- Wrote README.md
- Put it under git and published it: https://github.com/akirikku/launcher (description + topics set)

Next: clone and install on the work Mac and test Resume Work there (macOS side is untested so far); add summaries (.project.json) for the other projects; think about the "visual map" layout.

## 2026-10-12 06:25
Launch buttons, round two:
- Added "Resume with Claude": opens Konsole running `claude --continue` (new conversation if none), window stays on a shell afterwards. Tested by resuming this very session from the dashboard.
- Added "Open in VS Code" (`code <dir>`; `open -a "Visual Studio Code"` on macOS)
- Renamed "Resume Work" to "Open Terminal"; all three buttons go through one LAUNCH_ENDPOINTS table (/api/terminal, /api/claude, /api/vscode), each command configurable in config.json
- Restyled: pastel GitHub-purple accent, buttons stacked full width with aligned SVG icons
- README updated; everything pushed to GitHub

Next: test on the work Mac (all macOS paths still untested, incl. the AppleScript for Claude); add summaries for the other projects; visual map layout; maybe Windows (wt.exe + Startup folder / Task Scheduler).
