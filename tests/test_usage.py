"""Usage must describe the source actually read, including across clients."""
import json
import subprocess
import sys

import anyio
import pytest
from fastapi.testclient import TestClient
from mcp import Client, StdioServerParameters
from pydantic import ValidationError

from aftermark.models import Bundle, CorrectionInput, ItemInput, UsageInput
from aftermark.store import RevisionConflict, Store
from aftermark.web import create_app


@pytest.mark.parametrize("change", ["correction", "content"])
def test_stale_write_has_no_side_effect_and_recovery_preserves_backup(store, tmp_path, change):
    item = store.create(ItemInput(title="Versioned method", content="Original", project="Aftermark"))
    read = store.read(item["id"], "Aftermark", expected_revision=1)
    if change == "correction":
        store.correct(item["id"], CorrectionInput(text="Reassess", project="Aftermark"))
    else:
        store.update(item["id"], ItemInput(title="Versioned method", content="Revised", project="Aftermark"))
    value = dict(task="Check the method", project="Aftermark", outcome="referenced", reason="Read the source")
    before = store.export()
    for revision in [read["revision"], 99]:
        with pytest.raises(RevisionConflict, match="Read the current source"):
            store.record(item["id"], UsageInput(**value, expected_revision=revision))
        assert store.export() == before
    latest = store.read(item["id"], "Aftermark", expected_revision=2)
    record = store.record(item["id"], UsageInput(**value, expected_revision=latest["revision"]))
    assert record["item_revision"] == 2
    assert "expected_revision" not in record
    restored = Store(tmp_path / "restored")
    restored.import_bundle(Bundle.model_validate(store.export()))
    assert restored.export() == store.export()


def test_usage_requires_positive_revision_and_still_requires_evidence():
    value = dict(task="Check", outcome="verified", reason="Checked", evidence="test result")
    for extra in [{}, {"expected_revision": 0}, {"expected_revision": -1}]:
        with pytest.raises(ValidationError):
            UsageInput(**value, **extra)
    with pytest.raises(ValidationError, match="need a change"):
        UsageInput(**{**value, "evidence": ""}, expected_revision=1)


def test_http_stale_form_returns_conflict_without_creating_history(tmp_path):
    with TestClient(create_app(tmp_path)) as client:
        item = client.post("/api/items", json={"title": "Source", "content": "Old"}).json()
        client.post(f"/api/items/{item['id']}/corrections", json={"text": "New condition"})
        url = f"/api/items/{item['id']}/usage"
        data = {"task": "Evaluate", "outcome": "referenced", "reason": "Read source"}
        assert client.post(url, json=data).status_code == 422
        stale = client.post(url, json={**data, "expected_revision": 1})
        assert stale.status_code == 409
        assert stale.json()["code"] == "revision_conflict"
        assert client.get("/api/history").json() == []
        current = client.get(f"/api/items/{item['id']}").json()
        result = client.post(url, json={**data, "expected_revision": current["revision"]})
        assert result.status_code == 201
        assert result.json()["item_revision"] == 2


def test_cli_revision_is_required_and_stale_attempt_does_not_record(store):
    item = store.create(ItemInput(title="Source", content="Old"))
    store.correct(item["id"], CorrectionInput(text="New condition"))
    command = [sys.executable, "-m", "aftermark", "--data-dir", str(store.home), "record", item["id"],
               "--task", "Evaluate", "--outcome", "referenced", "--reason", "Read source"]
    def run(*extra):
        return subprocess.run([*command, *extra], capture_output=True, text=True, encoding="utf-8")
    assert run().returncode == 2
    stale = run("--revision", "1")
    assert stale.returncode == 1 and "current revision 2" in stale.stderr
    assert store.history() == []
    success = run("--revision", "2")
    assert success.returncode == 0
    assert json.loads(success.stdout)["item_revision"] == 2


def test_mcp_revision_conflict_then_reread_and_record(tmp_path):
    async def workflow():
        params = StdioServerParameters(command=sys.executable, args=["-m", "aftermark", "--data-dir", str(tmp_path), "mcp"])
        async with Client(params) as client:
            tools = await client.list_tools()
            record_tool = next(t for t in tools.tools if t.name == "record_usage")
            assert "expected_revision" in record_tool.input_schema["required"]
            saved = await client.call_tool("save_bookmark", {"title": "Versioned source", "content": "Original", "project": "Aftermark"})
            item_id = saved.structured_content["id"]
            read = await client.call_tool("read_bookmark", {"bookmark_id": item_id, "project": "Aftermark", "expected_revision": 1})
            await client.call_tool("add_correction", {"bookmark_id": item_id, "project": "Aftermark", "text": "Reassess the decision"})
            args = {"bookmark_id": item_id, "project": "Aftermark", "task": "Check", "outcome": "referenced", "reason": "Read source", "expected_revision": read.structured_content["revision"]}
            stale = await client.call_tool("record_usage", args)
            assert stale.is_error
            assert "expected revision 1, current revision 2" in stale.content[0].text
            assert "Read the current source and corrections" in stale.content[0].text
            reread = await client.call_tool("read_bookmark", {"bookmark_id": item_id, "project": "Aftermark", "expected_revision": 2})
            assert reread.structured_content["usage"] == []
            assert reread.structured_content["corrections"][0]["text"] == "Reassess the decision"
            good = await client.call_tool("record_usage", {**args, "expected_revision": reread.structured_content["revision"]})
            assert not good.is_error and good.structured_content["item_revision"] == 2
            wrong_project = await client.call_tool("record_usage", {**args, "expected_revision": 2, "project": "other"})
            assert wrong_project.is_error
    anyio.run(workflow)
