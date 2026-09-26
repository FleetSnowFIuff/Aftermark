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
    store.record(item["id"], UsageInput(task="Improve jumping", outcome="verified", reason="Added buffering", evidence="controller.test: 6 checks passed"))
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
            UsageInput(task="Improve", outcome=outcome, reason="It worked")
    item = bookmark(store, project="alpha")
    with pytest.raises(ValueError, match="different project"):
        store.record(item["id"], UsageInput(task="Improve", outcome="referenced", reason="Read it", project="beta"))
    with pytest.raises(ValueError, match="match"):
        store.correct(item["id"], CorrectionInput(text="Wrong project", project="beta"))


def test_backup_roundtrip_preserves_original_and_history(store, tmp_path):
    item = store.create(ItemInput(title="Transcript", kind="video", content="00:01.000 --> 00:02.000\nJump buffer"), ("lesson.vtt", "text/plain", b"WEBVTT\nsource bytes"))
    store.correct(item["id"], CorrectionInput(text="Keep controls", project="game"))
    store.record(item["id"], UsageInput(task="Jump", outcome="referenced", reason="Read source", project="game"))
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
