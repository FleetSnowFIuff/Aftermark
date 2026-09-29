from io import BytesIO

import httpx
import pytest
from pypdf import PdfWriter

from aftermark import ingest
from conftest import text_pdf


def test_web_extraction_and_remote_failure(monkeypatch):
    html = b"<html><title>Useful method</title><body><nav>Ignore menu</nav><article><h1>Input</h1><p>Keep this method.</p><script>alert(1)</script></article></body></html>"
    client = httpx.Client
    transport = httpx.MockTransport(lambda request: httpx.Response(200, headers={"Content-Type": "text/html"}, content=html))
    monkeypatch.setattr(ingest.httpx, "Client", lambda **kwargs: client(transport=transport, **kwargs))
    item, attachment = ingest.fetch_url("https://example.com/method")
    assert attachment is None
    assert item.title == "Useful method"
    assert "Keep this method" in item.content
    assert "Ignore menu" not in item.content and "alert" not in item.content
    transport = httpx.MockTransport(lambda request: httpx.Response(404))
    with pytest.raises(httpx.HTTPStatusError):
        ingest.fetch_url("https://example.com/missing")


def test_pdf_has_page_provenance_and_preserves_original():
    data = text_pdf()
    item, attachment = ingest.parse_file("paper.pdf", data)
    assert item.kind == "pdf"
    assert "[Page 1]" in item.content
    assert "Jump input buffering" in item.content
    assert attachment == ("paper.pdf", "application/pdf", data)


def test_scanned_or_blank_pdf_is_not_fake_success():
    writer = PdfWriter()
    writer.add_blank_page(200, 200)
    stream = BytesIO()
    writer.write(stream)
    with pytest.raises(ValueError, match="OCR"):
        ingest.parse_file("scan.pdf", stream.getvalue())


def test_subtitles_keep_timestamps_and_source_url():
    transcript = "WEBVTT\n\n00:00:03.000 --> 00:00:05.000\n输入缓冲\n"
    item, original = ingest.parse_file("clip.vtt", transcript.encode(), source_url="https://example.com/video")
    assert item.kind == "video"
    assert "00:00:03.000" in item.content
    assert item.source_url == "https://example.com/video"
    assert original[2] == transcript.encode()


def test_invalid_format_and_size_are_clear(monkeypatch):
    with pytest.raises(ValueError, match="Supported files"):
        ingest.parse_file("movie.mp4", b"video")
    monkeypatch.setattr(ingest, "MAX_FILE_BYTES", 3)
    with pytest.raises(ValueError, match="20 MB"):
        ingest.parse_file("note.txt", b"longer")


def test_import_tags_follow_the_same_validation_as_notes():
    item, _ = ingest.parse_file("note.txt", b"text", tags=["tag", " tag "])
    assert item.tags == ["tag"]
    with pytest.raises(ValueError):
        ingest.parse_file("note.txt", b"text", tags=[str(i) for i in range(21)])
