#!/usr/bin/env python3
"""Local project dashboard: serves index.html and opens a terminal in a project dir.

Run:  python3 server.py   then open http://127.0.0.1:8765
Per-machine settings go in config.json next to this file (see config.example.json).
"""
import json
import platform
import subprocess
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HOST, PORT = "127.0.0.1", 8765  # localhost only: never expose this to the network
HERE = Path(__file__).parent
JOURNAL = "JOURNAL.md"

# "{dir}" in the terminal command is replaced with the project directory.
DEFAULT_TERMINAL = {
    "Linux": ["konsole", "--workdir", "{dir}"],
    "Darwin": ["open", "-a", "Terminal", "{dir}"],  # e.g. "iTerm" or "Ghostty" instead
}


def load_config():
    f = HERE / "config.json"
    cfg = json.loads(f.read_text()) if f.exists() else {}
    return {
        "projects_dir": Path(cfg.get("projects_dir", "~/Projects")).expanduser(),
        "terminal": cfg.get("terminal") or DEFAULT_TERMINAL[platform.system()],
    }


CONFIG = load_config()
PROJECTS_DIR = CONFIG["projects_dir"]


def project_dirs():
    return sorted(p for p in PROJECTS_DIR.iterdir() if p.is_dir() and not p.name.startswith("."))


def resolve(name):
    """Map a project name from the browser to a real dir. Only known projects are allowed."""
    for p in project_dirs():
        if p.name == name:
            return p
    return None


def last_work(p):
    if (p / ".git").exists():
        out = subprocess.run(["git", "-C", str(p), "log", "-1", "--format=%cI|%s"],
                             capture_output=True, text=True).stdout.strip()
        if out:
            when, msg = out.split("|", 1)
            return {"when": when, "what": f"commit: {msg}"}
    files = [f for f in p.rglob("*") if f.is_file() and ".git" not in f.parts]
    if not files:
        return None
    newest = max(files, key=lambda f: f.stat().st_mtime)
    when = datetime.fromtimestamp(newest.stat().st_mtime).isoformat(timespec="seconds")
    return {"when": when, "what": f"edited {newest.relative_to(p)}"}


def summary(p):
    meta = p / ".project.json"
    if meta.exists():
        return json.loads(meta.read_text()).get("summary", "")
    for name in ("README.md", "README.txt", "README"):
        f = p / name
        if f.exists():
            paras = [s.strip() for s in f.read_text().split("\n\n")]
            return next((s for s in paras if s and not s.startswith("#")), "")
    return ""


def project_info(p):
    j = p / JOURNAL
    return {
        "name": p.name,
        "path": str(p),
        "summary": summary(p),
        "last": last_work(p),
        "journal": j.read_text() if j.exists() else "",
    }


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/":
            self._send(200, (HERE / "index.html").read_bytes(), "text/html; charset=utf-8")
        elif self.path == "/api/projects":
            self._send(200, [project_info(p) for p in project_dirs()])
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        # CSRF guard: any website you visit could POST to localhost. Browsers won't let
        # other origins send this custom header without a CORS preflight, which we never approve.
        if self.headers.get("X-Launcher") != "1":
            return self._send(403, {"error": "forbidden"})
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        p = resolve(body.get("name", ""))
        if not p:
            return self._send(404, {"error": "unknown project"})

        if self.path == "/api/resume":
            # Popen + start_new_session: the terminal outlives the request and the server.
            cmd = [arg.replace("{dir}", str(p)) for arg in CONFIG["terminal"]]
            subprocess.Popen(cmd, start_new_session=True,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self._send(200, {"ok": True})
        elif self.path == "/api/journal":
            entry = body.get("entry", "").strip()
            if entry:
                stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                with open(p / JOURNAL, "a") as f:
                    f.write(f"\n## {stamp}\n{entry}\n")
            self._send(200, project_info(p))
        else:
            self._send(404, {"error": "not found"})

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    print(f"Dashboard at http://{HOST}:{PORT}")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
