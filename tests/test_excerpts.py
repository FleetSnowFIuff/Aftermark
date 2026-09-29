import pytest

from aftermark.models import Bundle, CorrectionInput, ItemInput
from aftermark.sources import task_excerpt
from aftermark.store import Store, terms


@pytest.mark.parametrize(("query", "early", "relevant"), [
    ("MCP ToolError import failures", "MCP overview.", "MCP ToolError preserves actionable import failures."),
    ("跳跃输入缓冲", "跳跃概述。", "跳跃输入缓冲适用于提前按键。"),
])
def test_recall_finds_later_keyword_cluster_and_page(store, query, early, relevant):
    content = "[Page 1]\n" + early + "\n" + "Background. " * 200 + "\n[Page 2]\n" + relevant
    item = store.create(ItemInput(title="Long source", kind="pdf", content=content, project="demo"))
    before = store.export()
    found = store.recall(query, "demo")["candidates"][0]
    assert relevant in found["excerpt"]
    assert len(found["excerpt"]) <= 1200
    assert content[found["excerpt_start"]:found["excerpt_start"] + 1200] == found["excerpt"]
    page = next(m for m in found["excerpt_locations"] if m["id"] == "page-2")
    read = store.read(item["id"], "demo", anchor=page["id"], expected_revision=found["revision"])
    assert relevant in read["content"] and "Page 2" in read["citation"]
    assert set(found["excerpt_matched_terms"]) == set(terms(query))
    assert store.export() == before
    assert store.recall(query, "other")["candidates"] == []


def test_repetition_and_substrings_do_not_hide_relevant_passage():
    text = "buffering " * 150 + "buffer " * 200 + "\nJump buffer controls"
    result = task_excerpt(text, terms("jump buffer controls"))
    assert "Jump buffer controls" in result["excerpt"]
    assert set(result["excerpt_matched_terms"]) == {"jump", "buffer", "controls"}
    only_substrings = task_excerpt("buffering " * 200 + "\nactual buffer", ["buffer"])
    assert "actual buffer" in only_substrings["excerpt"]


def test_unicode_case_expansion_preserves_original_offsets():
    text = "İ 😀 " * 500 + "\nExact buffer controls"
    result = task_excerpt(text, terms("buffer controls"))
    assert "Exact buffer controls" in result["excerpt"]
    assert result["excerpt_start"] == text.index("buffer") - 160
    assert text[result["excerpt_start"]:result["excerpt_start"] + 1200] == result["excerpt"]


@pytest.mark.parametrize("distance", [1100, 1196])
def test_context_padding_cannot_displace_keywords_that_fit(distance):
    text = "." * 2000 + "alpha" + "." * (distance - 5) + "beta"
    result = task_excerpt(text, ["alpha", "beta"])
    assert result["excerpt_start"] == 2000
    assert result["excerpt_matched_terms"] == ["alpha", "beta"]
    assert "alpha" in result["excerpt"] and result["excerpt"].endswith("beta")


def test_a_partial_keyword_at_window_edge_does_not_count():
    text = "." * 2000 + "alpha" + "." * 1192 + "beta"
    result = task_excerpt(text, ["alpha", "beta"])
    assert result["excerpt_matched_terms"] == ["alpha"]


def test_metadata_and_correction_matches_do_not_claim_body_matches(store):
    item = store.create(ItemInput(title="Latency", content="Unrelated body.", project="demo"))
    store.correct(item["id"], CorrectionInput(text="Measure frame pacing", project="demo"))
    result = store.recall("latency frame pacing", "demo")["candidates"][0]
    assert set(result["match_locations"]) == {"title", "corrections"}
    assert result["excerpt_matched_terms"] == [] and result["excerpt_start"] == 0
    assert result["excerpt"] == "Unrelated body."
    link = store.create(ItemInput(title="Link", source_url="https://example.com", project="demo"))
    result = store.recall("link", "demo")["candidates"][0]
    assert result["id"] == link["id"] and result["excerpt"] == ""
    assert result["excerpt_matched_terms"] == [] and result["source_status"] == "link_only"


def test_ties_are_stable_and_existing_backups_need_no_migration(store, tmp_path):
    text = "buffer controls\n" + "background " * 150 + "\nbuffer controls"
    saved = store.create(ItemInput(title="Note", content=text))
    before = store.export()
    first = store.recall("buffer controls")["candidates"][0]
    assert first["excerpt_start"] == 0
    restored = Store(tmp_path / "restored")
    restored.import_bundle(Bundle.model_validate(before))
    assert restored.recall("buffer controls")["candidates"][0] == first
    assert restored.export() == before and store.get(saved["id"])["revision"] == 1


def test_late_subtitle_passage_keeps_timestamp_location(store):
    text = "WEBVTT\n\n00:00:01.000 --> 00:00:05.000\nInput overview\n\n" + "Background " * 150
    text += "\n\n00:02:03.000 --> 00:02:08.000\nJump input buffering handles early presses.\n"
    saved = store.create(ItemInput(title="Transcript", content=text, kind="video"))
    found = store.recall("jump input buffering")["candidates"][0]
    assert "early presses" in found["excerpt"]
    cue = next(m for m in found["excerpt_locations"] if m["id"] == "cue-2")
    assert cue["start_seconds"] == 123
    assert "early presses" in store.read(saved["id"], anchor=cue["id"], expected_revision=1)["content"]
