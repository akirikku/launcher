# Project Launcher

A local web dashboard for the projects in `~/Projects`. Each project gets a card showing:

- **Summary**: from `.project.json` (`{"summary": "..."}`), or the first paragraph of the project's README
- **Last work done**: the latest git commit, or the most recently edited file if the project isn't a git repo
- **Journal**: entries you add from the page, stored in the project's own `JOURNAL.md`
- **Open Terminal**: opens a terminal in the project folder (Konsole on Linux, Terminal on macOS)
- **Resume with Claude**: opens a terminal there running `claude --continue`, which picks up the last [Claude Code](https://claude.com/claude-code) conversation in that folder or starts a new one. When you quit Claude, the window stays open on a shell in the project folder.
- **Open in VS Code**: opens the project folder in VS Code, like `cd <project> && code .`

It runs on Linux (KDE) and macOS. It uses only the Python 3 standard library, so there is nothing to install.

## Quick start

```sh
python3 server.py
```

Then open <http://127.0.0.1:8765>. Resume with Claude needs [Claude Code](https://claude.com/claude-code) installed (`claude` on your `PATH`). The dashboard only works while the server is running.

## Run it at login

```sh
service/install.sh
```

The script detects the OS and installs the matching background service, pointed at wherever this repo lives:

| OS | Mechanism | Installed file |
|---|---|---|
| Linux | systemd user service | `~/.config/systemd/user/project-launcher.service` |
| macOS | launchd LaunchAgent | `~/Library/LaunchAgents/local.project-launcher.plist` |

Run it again after moving the repo or editing a template in `service/`. It overwrites the installed file and restarts the service. Edit the templates, not the installed copies.

**Day to day:**

| | Linux | macOS |
|---|---|---|
| Status | `systemctl --user status project-launcher` | `launchctl print gui/$(id -u)/local.project-launcher` |
| Restart (after editing `server.py`) | `systemctl --user restart project-launcher` | `launchctl kickstart -k gui/$(id -u)/local.project-launcher` |
| Logs | `journalctl --user -u project-launcher -f` | `tail -f ~/Library/Logs/project-launcher.log` |
| Remove | `systemctl --user disable --now project-launcher` | `launchctl bootout gui/$(id -u)/local.project-launcher` and delete the plist |

Changes to `index.html` only need a browser reload.

## Configuration

Settings that differ between machines go in `config.json` next to `server.py`. Git ignores this file. Copy `config.example.json` to start:

```json
{
  "projects_dir": "~/Projects",
  "terminal": ["open", "-a", "iTerm", "{dir}"]
}
```

- `projects_dir`: the folder whose subfolders become cards. Default: `~/Projects`.
- `terminal`: the command run by Open Terminal, with `{dir}` replaced by the project path. Defaults:
  - Linux: `["konsole", "--workdir", "{dir}"]`
  - macOS: `["open", "-a", "Terminal", "{dir}"]`

  Other examples: `["open", "-a", "Ghostty", "{dir}"]`, or `["code", "{dir}"]` to open VS Code instead.
- `claude`: the command run by Resume with Claude, also using `{dir}`. Defaults:
  - Linux: `["konsole", "--workdir", "{dir}", "-e", "bash", "-ic", "claude --continue; exec bash"]`
  - macOS: an `osascript` command that tells Terminal to run `cd <dir> && claude --continue`. See `DEFAULT_CLAUDE` in `server.py`.
- `vscode`: the command run by Open in VS Code. Defaults:
  - Linux: `["code", "{dir}"]`
  - macOS: `["open", "-a", "Visual Studio Code", "{dir}"]`

  This also works for other editors, for example `["cursor", "{dir}"]`.

Restart the service after changing `config.json`.

## How it works

Browsers don't let web pages start programs, so a small local server does it. `server.py` serves the page and handles these endpoints:

- `GET /api/projects` lists the projects and their info
- `POST /api/terminal`, `/api/claude`, `/api/vscode` launch the matching command in a project
- `POST /api/journal` adds a journal entry

Safety measures:

- The server only listens on `127.0.0.1`, so nothing else on the network can reach it.
- The page sends a project *name*, never a path. The server only accepts names of folders in `projects_dir`.
- POST requests must carry an `X-Launcher` header. Browsers won't let other websites add a custom header to requests aimed at localhost, so a site you visit can't trigger launches.

## Files

```
server.py              HTTP server and launcher
index.html             the dashboard page
config.example.json    sample per-machine settings
service/install.sh     installs the login service (Linux or macOS)
service/linux/         systemd unit template
service/macos/         launchd plist template
```

## macOS notes

- `python3` comes with the Xcode Command Line Tools (`xcode-select --install`) or Homebrew. `install.sh` records the full path of whichever `python3` is on your `PATH`.
- If `projects_dir` is inside `~/Documents` or `~/Desktop`, macOS privacy controls may block the background service from reading it. Use a folder like `~/Projects`, or give `python3` Full Disk Access in System Settings → Privacy & Security.
