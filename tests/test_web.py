from fastapi.testclient import TestClient

from aftermark.web import create_app
from conftest import text_pdf


def test_complete_browser_api_workflow(tmp_path):
    with TestClient(create_app(tmp_path / "web")) as client:
        assert client.get("/").status_code == 200
        assert client.get("/static/app.js").status_code == 200
        assert client.get("/about").status_code == 200
        data = {"title": "Jump buffer", "content": "Keep jump input briefly", "intent": "Keep buttons", "role": "method", "project": "demo"}
        saved = client.post("/api/items", json=data)
        assert saved.status_code == 201
        item_id = saved.json()["id"]
        assert client.post("/api/recall", json={"task": "jump", "project": "other"}).json()["candidates"] == []
        assert client.post(f"/api/items/{item_id}/corrections", json={"text": "Prototype only", "project": "demo"}).status_code == 201
        result = client.post("/api/recall", json={"task": "jump", "project": "demo"}).json()
        assert result["candidates"][0]["corrections"][0]["text"] == "Prototype only"
        no_evidence = {"task": "Jump", "outcome": "verified", "project": "demo", "reason": "Works"}
        assert client.post(f"/api/items/{item_id}/usage", json=no_evidence).status_code == 422
        assert client.post(f"/api/items/{item_id}/usage", json={**no_evidence, "evidence": "tests/test_jump.py passed"}).status_code == 201
        assert client.get("/api/history").json()[0]["item_revision"] == 2
        pdf = client.post("/api/import/file", files={"file": ("sample.pdf", text_pdf(), "application/pdf")})
        assert pdf.status_code == 201
        assert client.get(f"/api/items/{pdf.json()['id']}/original").content == text_pdf()
        backup = client.get("/api/export").json()
        assert len(backup["items"]) == 2
        assert client.post("/api/import/bundle", json=backup).json()["skipped"] == 2
        assert client.patch(f"/api/items/{item_id}/archive", json={"archived": True}).status_code == 200
        assert client.post("/api/recall", json={"task": "jump", "project": "demo"}).json()["candidates"][0]["kind"] == "pdf"


def test_local_service_rejects_other_origins_and_hosts(tmp_path):
    with TestClient(create_app(tmp_path / "web")) as client:
        assert client.post("/api/examples", headers={"Origin": "https://unrelated.example"}).status_code == 403
        assert client.get("/api/items", headers={"Host": "attacker.example"}).status_code == 400
        assert client.post("/api/examples").status_code == 200
        assert client.post("/api/examples").json()["imported"] == 0
        assert client.get("/api/items/not-here").status_code == 404
