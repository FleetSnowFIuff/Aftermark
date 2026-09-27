import json
import subprocess

import pytest

from aftermark.codex import connect
from aftermark.integration import config


def codex_stub(monkeypatch, servers):
    calls = []
    monkeypatch.setattr("aftermark.codex.shutil.which", lambda _: "codex")
    def run(args, **kwargs):
        calls.append(args)
        return subprocess.CompletedProcess(args, 0, json.dumps(servers) if "list" in args else "Added", "")
    monkeypatch.setattr("aftermark.codex.subprocess.run", run)
    return calls


def test_preview_then_explicit_registration(tmp_path, monkeypatch):
    calls = codex_stub(monkeypatch, [])
    assert connect(tmp_path)["status"] == "not_configured"
    assert len(calls) == 1 and "list" in calls[0]
    assert connect(tmp_path, apply=True)["applied"] is True
    assert calls[-1][1:5] == ["mcp", "add", "aftermark", "--"]
    assert str(tmp_path.resolve()) in calls[-1]


def test_existing_connection_is_not_overwritten(tmp_path, monkeypatch):
    entry = config(tmp_path)["generic"]["mcpServers"]["aftermark"]
    current = {"name": "aftermark", "enabled": True, "transport": {"type": "stdio", **entry}}
    calls = codex_stub(monkeypatch, [current])
    assert connect(tmp_path, apply=True)["status"] == "configured"
    current["transport"]["args"] = ["a-different-library"]
    assert connect(tmp_path)["status"] == "conflict"
    with pytest.raises(ValueError, match="not overwritten"):
        connect(tmp_path, apply=True)
    assert all("add" not in args for args in calls)


def test_disabled_and_missing_cli_are_reported(tmp_path, monkeypatch):
    codex_stub(monkeypatch, [{"name": "aftermark", "enabled": False, "transport": {"type": "http", "url": "https://example.com"}}])
    with pytest.raises(ValueError, match="disabled"):
        connect(tmp_path, apply=True)
    monkeypatch.setattr("aftermark.codex.shutil.which", lambda _: None)
    with pytest.raises(ValueError, match="not found"):
        connect(tmp_path)
