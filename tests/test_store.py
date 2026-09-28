import pytest
from pydantic import ValidationError

from aftermark.models import Bundle, CorrectionInput, ItemInput, UsageInput
from aftermark.store import Store


def bookmark(store, **overrides):
    values = dict(title="Jump buffering", content="Use an input buffer for jump controls.", intent="Keep existing buttons.", role="method")
    values.update(overrides)
    return store.create(ItemInput(**values))


def test_project_scope_and_corrections_do_not_leak(store):
    personal = bookmark(store)
    project_a = bookmark(store, project="game-a")
    project_b = bookmark(store, project="game-b")
    store.correct(personal["id"], CorrectionInput(text="Only prototypes in A", project="game-a"))
    a = store.recall("jump input", "game-a")["candidates"]
    assert {c["id"] for c in a} == {personal["id"], project_a["id"]}
    assert next(c for c in a if c["id"] == personal["id"])["corrections"][0]["text"] == "Only prototypes in A"
    b = store.recall("jump", "game-b")["candidates"]
    assert {c["id"] for c in b} == {personal["id"], project_b["id"]}
    assert next(c for c in b if c["id"] == personal["id"])["corrections"] == []
    assert [c["id"] for c in store.recall("jump")["candidates"]] == [personal["id"]]


def test_chinese_recall_archive_and_no_match(store):
    item = bookmark(store, title="跳跃操作容错", content="使用跳跃输入缓冲，避免漏掉提前按下的输入。")
    assert store.recall("改善跳跃输入容错")["candidates"][0]["id"] == item["id"]
    assert store.recall("postgresql migrations")["candidates"] == []
    assert store.recall("??!!!")["candidates"] == []
    store.archive(item["id"], True)
    assert store.recall("跳跃")["candidates"] == []
    store.archive(item["id"], False)
    assert len(store.recall("跳跃")["candidates"]) == 1


def test_recall_does_not_create_a_usage_claim(store):
    item = bookmark(store)
    store.recall("jump")
    assert store.get(item["id"])["usage"] == []


def test_usage_keeps_original_revision_after_correction_and_edit(store):
    item = bookmark(store)
    store.record(item["id"], UsageInput(expected_revision=1, task="Improve jumping", outcome="verified", reason="Added buffering", evidence="controller.test: 6 checks passed"))
    store.correct(item["id"], CorrectionInput(text="Prototype only"))
    updated = ItemInput(**{k: item[k] for k in ItemInput.model_fields})
    updated.title = "Controller latency"
    updated.content = "Latency measurement"
    updated.intent = "Measure before changing"
    store.update(item["id"], updated)
    result = store.get(item["id"])
    assert result["revision"] == 3
    assert result["usage"][0]["item_revision"] == 1
    assert store.recall("buffering")["candidates"] == []
    assert store.recall("latency")["candidates"][0]["revision"] == 3


def test_outcomes_require_evidence_and_matching_project(store):
    for outcome in ["applied", "verified"]:
        with pytest.raises(ValidationError):
            UsageInput(expected_revision=1, task="Improve", outcome=outcome, reason="It worked")
    item = bookmark(store, project="alpha")
    with pytest.raises(ValueError, match="different project"):
        store.record(item["id"], UsageInput(expected_revision=1, task="Improve", outcome="referenced", reason="Read it", project="beta"))
    with pytest.raises(ValueError, match="match"):
        store.correct(item["id"], CorrectionInput(text="Wrong project", project="beta"))


def test_backup_roundtrip_preserves_original_and_history(store, tmp_path):
    item = store.create(ItemInput(title="Transcript", kind="video", content="00:01.000 --> 00:02.000\nJump buffer"), ("lesson.vtt", "text/plain", b"WEBVTT\nsource bytes"))
    store.correct(item["id"], CorrectionInput(text="Keep controls", project="game"))
    store.record(item["id"], UsageInput(expected_revision=2, task="Jump", outcome="referenced", reason="Read source", project="game"))
    exported = store.export()
    restored = Store(tmp_path / "restored")
    assert restored.import_bundle(Bundle.model_validate(exported)) == {"imported": 1, "skipped": 0}
    assert restored.export() == exported
    assert restored.attachment(item["id"])["data"] == b"WEBVTT\nsource bytes"
    assert restored.import_bundle(Bundle.model_validate(exported)) == {"imported": 0, "skipped": 1}
    assert Store(tmp_path / "restored").get(item["id"])["corrections"][0]["text"] == "Keep controls"


def test_bad_import_is_atomic(store):
    item = bookmark(store)
    exported = store.export()
    exported["items"][0]["id"] = "new-source"
    exported["corrections"] = [{"id": "bad", "item_id": "missing", "text": "No parent", "project": "", "created_at": "2026-09-26"}]
    with pytest.raises(ValueError, match="without its bookmark"):
        store.import_bundle(Bundle.model_validate(exported))
    assert len(store.list()) == 1
    assert store.list()[0]["id"] == item["id"]


def test_rules_require_intent_and_urls_are_http():
    with pytest.raises(ValidationError):
        ItemInput(title="Rule", content="Source", role="rule")
    with pytest.raises(ValidationError):
        ItemInput(title="Link", source_url="javascript:alert(1)")


def test_correction_only_matches_respect_both_scopes(store):
    personal = bookmark(store)
    private = bookmark(store, project="alpha")
    store.correct(personal["id"], CorrectionInput(text="检查触屏延迟 touchscreen latency", project="alpha"))
    store.correct(private["id"], CorrectionInput(text="photogrammetry"))
    found = store.recall("检查触屏延迟", "alpha")["candidates"]
    assert [x["id"] for x in found] == [personal["id"]]
    assert found[0]["match_locations"] == ["corrections"]
    assert "触屏" in found[0]["matched_terms"]
    for scope in ("", "beta"):
        assert store.recall("touchscreen latency", scope)["candidates"] == []
        assert store.recall("photogrammetry", scope)["candidates"] == []
    assert store.recall("photogrammetry", "alpha")["candidates"][0]["id"] == private["id"]
    store.archive(personal["id"], True)
    assert store.recall("touchscreen", "alpha")["candidates"] == []


def test_corrections_survive_backup_and_v1_database_upgrade(store, tmp_path):
    item = bookmark(store)
    store.correct(item["id"], CorrectionInput(text="Check accessibility", project="game"))
    exported = store.export()
    with store.connection() as db:
        db.execute("DROP TABLE correction_search")
        db.execute("PRAGMA user_version=1")
    upgraded = Store(store.home)
    assert upgraded.export() == exported
    assert upgraded.recall("accessibility", "game")["candidates"][0]["id"] == item["id"]
    restored = Store(tmp_path / "restored-v2")
    restored.import_bundle(Bundle.model_validate(exported))
    assert restored.recall("accessibility", "game")["candidates"][0]["id"] == item["id"]
    assert restored.recall("accessibility", "other")["candidates"] == []
    assert Store(store.home).export() == exported


def test_old_usage_is_explicitly_marked_after_a_correction(store):
    item = bookmark(store)
    store.record(item["id"], UsageInput(expected_revision=1, task="Jump", outcome="verified", reason="Tested", evidence="test_jump passed"))
    assert store.get(item["id"])["usage"][0]["is_current_revision"] is True
    store.correct(item["id"], CorrectionInput(text="Prototype only"))
    assert store.get(item["id"])["usage"][0]["is_current_revision"] is False
    assert not store.history()[0]["is_current_revision"]
    recalled = store.recall("jump")["candidates"][0]
    assert recalled["previous_usage"][0]["is_current_revision"] is False
    assert recalled["previous_usage"][0]["outcome"] == "verified"


def test_source_and_correction_matches_are_combined_without_duplicate_results(store):
    source = bookmark(store, title="Accessibility", content="Keyboard navigation", intent="", role="reference")
    both = bookmark(store, title="Accessibility", content="Keyboard navigation", intent="", role="reference")
    store.correct(both["id"], CorrectionInput(text="Accessibility in menus"))
    result = store.recall("accessibility")["candidates"]
    assert [x["id"] for x in result] == [both["id"], source["id"]]
    assert set(result[0]["match_locations"]) == {"title", "corrections"}
