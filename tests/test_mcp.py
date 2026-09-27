import sys

import anyio
from mcp import Client, StdioServerParameters


def test_real_stdio_roundtrip(tmp_path):
    async def workflow():
        params = StdioServerParameters(command=sys.executable, args=["-m", "aftermark", "--data-dir", str(tmp_path / "mcp"), "mcp"])
        async with Client(params) as client:
            tools = await client.list_tools()
            assert {tool.name for tool in tools.tools} == {"recall", "read_bookmark", "save_bookmark", "record_usage", "add_correction"}
            saved = await client.call_tool("save_bookmark", {"title": "Jump buffer", "content": "Keep recent jump input", "intent": "Keep the buttons", "project": "game", "role": "method"})
            item_id = saved.structured_content["id"]
            empty = await client.call_tool("recall", {"task": "jump", "project": "other"})
            assert empty.structured_content["candidates"] == []
            await client.call_tool("add_correction", {"bookmark_id": item_id, "text": "Prototype only", "project": "game"})
            found = await client.call_tool("recall", {"task": "jump", "project": "game"})
            assert found.structured_content["candidates"][0]["corrections"][0]["text"] == "Prototype only"
            read = await client.call_tool("read_bookmark", {"bookmark_id": item_id, "project": "game", "limit": 5})
            assert read.structured_content["content"] == "Keep "
            assert read.structured_content["next_offset"] == 5
            assert read.structured_content["usage"] == []
            await client.call_tool("record_usage", {"bookmark_id": item_id, "task": "Improve jump", "project": "game", "outcome": "applied", "reason": "Fits controller", "evidence": "controller.py: input buffer added"})
            read = await client.call_tool("read_bookmark", {"bookmark_id": item_id, "project": "game"})
            assert read.structured_content["usage"][0]["item_revision"] == 2
    anyio.run(workflow)


def test_doctor_uses_real_stdio_without_changing_collection(store):
    from aftermark.diagnostics import check_connection
    from aftermark.models import ItemInput
    store.create(ItemInput(title="My note", content="Keep my own words"))
    before = store.export()
    report = anyio.run(check_connection, store)
    assert report["ok"] is True
    assert report["transport"] == "stdio"
    assert report["data_dir"] == str(store.home.resolve())
    assert "recall" in report["tools"]
    assert store.export() == before
