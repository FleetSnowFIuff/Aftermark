"""Exercise the real local MCP transport without writing bookmarks or usage."""
import sys

import anyio
from mcp import Client, StdioServerParameters

from . import __version__
from .integration import config
from .store import Store


async def check_connection(store: Store) -> dict:
    entry = config(store.home)["generic"]["mcpServers"]["aftermark"]
    with anyio.fail_after(20):
        async with Client(StdioServerParameters(command=entry["command"], args=entry["args"])) as client:
            names = sorted(tool.name for tool in (await client.list_tools()).tools)
            required = {"recall", "read_bookmark", "save_bookmark", "add_correction", "record_usage"}
            if not required.issubset(names):
                raise RuntimeError("The MCP server is missing required Aftermark tools.")
            response = await client.call_tool("recall", {"task": "aftermark_connection_check"})
            if response.is_error or not isinstance(response.structured_content, dict) or "candidates" not in response.structured_content:
                raise RuntimeError("The MCP server did not return a valid recall response.")
    return {"ok": True, "version": __version__, "python": sys.executable,
            "data_dir": str(store.home.resolve()), "tools": names, "transport": "stdio",
            "note": "Local MCP handshake and recall succeeded. No bookmarks or usage records were written. This does not verify a particular agent host or proactive tool use."}
