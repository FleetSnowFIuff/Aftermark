from io import BytesIO

import pytest
from pypdf import PdfReader, PdfWriter

from aftermark.ingest import parse_file
from aftermark.models import ItemInput, CorrectionInput
from aftermark.sources import locations, read_source
from conftest import text_pdf


def pdf_item(store, project=""):
    return store.create(ItemInput(title="Paper", kind="pdf", project=project,
        content="[Page 1]\nIntro 😀\n\n[Page 2]\nInput buffering helps jumping."))


def test_real_pdf_import_has_page_locations(store):
    writer = PdfWriter()
    reader = PdfReader(BytesIO(text_pdf()))
    writer.add_page(reader.pages[0])
    writer.add_page(reader.pages[0])
    output = BytesIO()
    writer.write(output)
    item, attachment = parse_file("two-pages.pdf", output.getvalue())
    saved = store.create(item, attachment)
    markers = store.get(saved["id"])["locations"]
    assert [m["page"] for m in markers] == [1, 2]
    read = store.read(saved["id"], anchor=markers[1]["id"])
    assert read["content"].startswith("[Page 2]")
    assert "[Page 1]" not in read["content"]
    assert "Page 2" in read["citation"]
    assert store.attachment(saved["id"])["data"] == output.getvalue()


def test_pdf_recall_locations_and_anchor_pagination(store):
    item = pdf_item(store)
    result = store.recall("buffering")["candidates"][0]
    assert any(m["page"] == 2 for m in result["excerpt_locations"])
    first = store.read(item["id"], anchor="page-2", limit=12, expected_revision=1)
    second = store.read(item["id"], anchor="page-2", offset=first["next_offset"], expected_revision=1)
    assert first["content"] + second["content"] == "[Page 2]\nInput buffering helps jumping."
    assert first["source_offset"] == item["content"].index("[Page 2]")
    assert second["next_offset"] is None
    assert item["id"] in first["citation"] and "v1" in first["citation"]


@pytest.mark.parametrize("extension,header,stamp", [
    ("srt", "1\r\n", "00:00:03,250 --> 00:00:05,750"),
    ("vtt", "WEBVTT\n\ncue-a\n", "00:03.250 --> 00:05.750 align:start"),
])
def test_subtitle_cue_preserves_timestamp_text_and_original(store, extension, header, stamp):
    data = (header + stamp + "\n😀 Jump now\n\n2\n00:00:06.000 --> 00:00:08.000\nOther cue").encode()
    source, attachment = parse_file("clip." + extension, data)
    item = store.create(source, attachment)
    markers = store.get(item["id"])["locations"]
    assert len(markers) == 2
    assert markers[0]["start_seconds"] == 3.25
    assert markers[0]["end_seconds"] == 5.75
    read = store.read(item["id"], anchor="cue-1")
    assert "😀 Jump now" in read["content"]
    assert "Other cue" not in read["content"]
    assert "03.250" in read["citation"]
    assert store.attachment(item["id"])["data"] == data


def test_locations_are_not_invented_for_plain_or_invalid_content(store):
    for kind, content in [("note", "[Page 1]\nA user note"), ("video", "00:10.000 --> 00:09.000\nBad timing"), ("video", "An ordinary untimed transcript")]:
        item = store.create(ItemInput(title="Source", kind=kind, content=content))
        assert locations(item) == []
        assert read_source(item)["content"] == content


def test_anchor_reads_reject_changed_wrong_scope_and_archived_sources(store):
    item = pdf_item(store, project="alpha")
    with pytest.raises(ValueError, match="another project"):
        store.read(item["id"], project="beta", anchor="page-1")
    store.correct(item["id"], CorrectionInput(text="Changed interpretation", project="alpha"))
    with pytest.raises(ValueError, match="changed"):
        store.read(item["id"], project="alpha", anchor="page-1", expected_revision=1)
    with pytest.raises(ValueError, match="not found"):
        store.read(item["id"], project="alpha", anchor="page-99")
    store.archive(item["id"], True)
    with pytest.raises(ValueError, match="archived"):
        store.read(item["id"], project="alpha", anchor="page-1")
    assert store.get(item["id"])["usage"] == []
