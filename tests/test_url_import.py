import json
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import anyio
import pytest
from fastapi.testclient import TestClient
from mcp import Client, StdioServerParameters

from aftermark import ingest
from aftermark.store import Store
from aftermark.web import create_app
from conftest import text_pdf


@pytest.fixture
def sources():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/redirect":
                self.send_response(302)
                self.send_header("Location", "/paper")
                self.end_headers()
                return
            bodies = {
                "/paper": ("application/pdf", text_pdf()),
                "/page": ("text/html", b"<title>Jump method</title><article>Jump input buffering reference.</article>"),
                "/video": ("video/mp4", b"not a supported source"),
                "/empty": ("text/plain", b" \n"),
                "/broken": ("application/pdf", b"not a PDF"),
            }
            mime, body = bodies.get(self.path, ("text/plain", b"not found"))
            self.send_response(200 if self.path in bodies else 404)
            self.send_header("Content-Type", mime)
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_redirected_pdf_keeps_url_bytes_scope_and_metadata(sources):
    item, attachment = ingest.fetch_url(sources + "/redirect", title="Saved paper", project="game",
                                        role="method", intent="Input timing", tags=[" jump ", "jump"])
    assert (item.title, item.project, item.role, item.intent, item.tags) == (
        "Saved paper", "game", "method", "Input timing", ["jump"])
    assert item.source_url == sources + "/redirect"
    assert item.source_name == "paper.pdf"
    assert "[Page 1]" in item.content and "Jump input buffering" in item.content
    assert attachment == ("paper.pdf", "application/pdf", text_pdf())


@pytest.mark.parametrize(("path", "message"), [
    ("/video", "Unsupported content type"), ("/empty", "no readable text"),
    ("/broken", "could not be read"),
])
def test_failed_url_import_leaves_collection_unchanged(tmp_path, sources, path, message):
    with TestClient(create_app(tmp_path)) as client:
        before = client.get("/api/export").json()
        result = client.post("/api/import/web", json={"url": sources + path})
        assert result.status_code == 422
        assert message in result.text
        assert client.get("/api/export").json() == before


@pytest.mark.parametrize(("path", "limit", "message"), [
    ("/page", "MAX_WEB_BYTES", "5 MB"), ("/paper", "MAX_FILE_BYTES", "20 MB"),
])
def test_each_format_enforces_its_download_limit(sources, monkeypatch, path, limit, message):
    monkeypatch.setattr(ingest, limit, 8)
    with pytest.raises(ValueError, match=message):
        ingest.fetch_url(sources + path)


def test_invalid_metadata_is_rejected_before_network(monkeypatch):
    def unexpected_network(**kwargs):
        pytest.fail("Invalid input must not perform a network request")
    monkeypatch.setattr(ingest.httpx, "Client", unexpected_network)
    with pytest.raises(ValueError):
        ingest.fetch_url("https://example.com", role="not-a-role")


def test_http_pdf_import_original_and_backup_roundtrip(tmp_path, sources):
    with TestClient(create_app(tmp_path / "web")) as client:
        response = client.post("/api/import/web", json={"url": sources + "/paper", "project": "game"})
        assert response.status_code == 201
        item = response.json()
        assert client.get(f"/api/items/{item['id']}/original").content == text_pdf()
        backup = client.get("/api/export").json()
    with TestClient(create_app(tmp_path / "restored")) as client:
        assert client.post("/api/import/bundle", json=backup).status_code == 200
        assert client.get("/api/export").json() == backup
        assert client.get(f"/api/items/{item['id']}/original").content == text_pdf()


def test_cli_fetch_imports_pdf(sources, tmp_path):
    result = subprocess.run([sys.executable, "-m", "aftermark", "--data-dir", str(tmp_path),
                             "add", "--url", sources + "/paper", "--fetch", "--project", "game"],
                            text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    item = Store(tmp_path).export()["items"][0]
    assert item["kind"] == "pdf" and item["project"] == "game"
    assert "Jump input buffering" in item["content"]


def test_mcp_import_recall_read_and_failure_without_false_success(sources, tmp_path):
    async def workflow():
        params = StdioServerParameters(command=sys.executable, args=["-m", "aftermark", "--data-dir", str(tmp_path), "mcp"],
                                      env={"NO_PROXY": "127.0.0.1,localhost"})
        async with Client(params) as client:
            result = await client.call_tool("import_url", {"url": sources + "/redirect", "project": "game"})
            assert not result.is_error
            item = result.structured_content
            assert item["original_saved"] and item["revision"] == 1
            assert "content" not in item and "Jump input buffering" not in json.dumps(item)
            assert (await client.call_tool("recall", {"task": "jump", "project": "other"})).structured_content["candidates"] == []
            found = (await client.call_tool("recall", {"task": "jump", "project": "game"})).structured_content
            assert found["candidates"][0]["id"] == item["id"]
            read = await client.call_tool("read_bookmark", {"bookmark_id": item["id"], "project": "game", "expected_revision": 1, "anchor": "page-1"})
            assert "Jump input buffering" in read.structured_content["content"]
            assert "Page 1" in read.structured_content["citation"]
            assert read.structured_content["usage"] == []
            before = Store(tmp_path).export()
            failed = await client.call_tool("import_url", {"url": sources + "/video", "project": "game"})
            assert failed.is_error
            assert "no bookmark saved" in failed.content[0].text
            assert Store(tmp_path).export() == before
    anyio.run(workflow)
