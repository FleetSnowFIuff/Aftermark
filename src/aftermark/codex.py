"""Explicit Codex registration through its own CLI; no hand-edited user config."""
import json
import os
from pathlib import Path
import shutil
import subprocess

from .integration import config


def connect(home: Path, apply: bool = False) -> dict:
    executable = shutil.which("codex")
    if not executable:
        raise ValueError("Codex CLI was not found on PATH. Install it or copy the TOML from aftermark config into Codex settings.")
    desired = config(home)["generic"]["mcpServers"]["aftermark"]
    command = [executable, "mcp", "add", "aftermark", "--", desired["command"], *desired["args"]]
    listed = subprocess.run([executable, "mcp", "list", "--json"], capture_output=True, text=True, encoding="utf-8", timeout=30)
    if listed.returncode:
        raise ValueError("Codex could not list MCP configuration. Run codex mcp list to inspect the error.")
    current = next((s for s in json.loads(listed.stdout) if s["name"] == "aftermark"), None)
    status = "not_configured"
    if current:
        transport = current["transport"]
        normalize = lambda values: [os.path.normcase(os.path.normpath(v)) for v in values]
        matches = transport["type"] == "stdio" and normalize([transport["command"], *transport["args"]]) == normalize([desired["command"], *desired["args"]])
        status = "configured" if matches and current["enabled"] else "conflict"
    if apply and status == "conflict":
        raise ValueError("An existing aftermark server is disabled or points elsewhere. Review codex mcp get aftermark; it was not overwritten.")
    if apply and status == "not_configured":
        added = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", timeout=30)
        if added.returncode:
            raise ValueError("Codex could not register Aftermark. Run the previewed command to inspect the error.")
        status = "configured"
    return {"host": "codex", "status": status, "applied": apply and current is None,
            "command": command, "data_dir": str(home.resolve()),
            "next_step": "Restart the MCP server in Codex settings and start a fresh turn. Verify recall, read_bookmark and an honest usage record. Configuration alone is not a connection or task test."}
