import json
import subprocess
import sys

from fastapi.testclient import TestClient

from aftermark.integration import config
from aftermark.models import ItemInput
from aftermark.store import Store
from aftermark.web import create_app


def test_project_instructions_roundtrip_through_cli_and_retrieval(tmp_path):
    project = '游戏 "demo"'
    store = Store(tmp_path)
    store.create(ItemInput(title="Jump buffer", content="Keep jump input", project=project))
    output = subprocess.run([sys.executable, "-m", "aftermark", "--data-dir", str(tmp_path), "config", "--project", "  " + project + "  "], capture_output=True, text=True, encoding="utf-8", check=True)
    result = json.loads(output.stdout)
    assert result["project"] == project
    assert json.dumps(project, ensure_ascii=False) in result["instructions"]
    assert len(store.recall("jump", result["project"])["candidates"]) == 1
    assert store.recall("jump", "another-game")["candidates"] == []
    assert result["generic"] == config(tmp_path)["generic"]


def test_web_config_distinguishes_unspecified_personal_and_project(tmp_path):
    with TestClient(create_app(tmp_path)) as client:
        generic = client.get("/api/integration").json()
        personal = client.get("/api/integration", params={"project": " "}).json()
        scoped = client.get("/api/integration", params={"project": "Aftermark"}).json()
        assert generic["project"] is None
        assert personal["project"] == "" and "personal/global" in personal["instructions"]
        assert scoped["project"] == "Aftermark" and '"Aftermark"' in scoped["instructions"]
        assert generic["generic"] == personal["generic"] == scoped["generic"]
        assert client.get("/api/integration", params={"project": "x" * 161}).status_code == 422
        assert client.get("/api/items").json() == []
