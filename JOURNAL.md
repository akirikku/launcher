
## 2026-10-12 05:50
Built the first prototype with Claude: Python stdlib server (server.py) + index.html. Cards for each folder in ~/Projects, Resume Work launches `konsole --workdir`. Next: try it out, decide on the "visual map" layout, maybe run it as a systemd user service.

## 2026-10-12 06:10
Turned the prototype into a real project:
- Runs at login as a systemd user service; service/install.sh installs it (template in service/linux)
- Added macOS support: terminal command and projects dir configurable via config.json (Terminal.app default on Mac), launchd LaunchAgent in service/macos, install.sh detects the OS
- Wrote README.md
- Put it under git and published it: https://github.com/akirikku/launcher (description + topics set)

Next: clone and install on the work Mac and test Resume Work there (macOS side is untested so far); add summaries (.project.json) for the other projects; think about the "visual map" layout.
