# Architecture

```text
Browser UI → FastAPI ─┐
CLI ─────────────────┼→ Store → SQLite + FTS5
MCP stdio ────────────┘     ↑
                     input models
Web / PDF / text → ingest → ItemInput
```

`models.py` defines boundary contracts. `store.py` owns persistence, retrieval, project filters, revisions and backup transactions. `ingest.py` extracts source text without inventing summaries. `web.py`, `cli.py` and `mcp_server.py` are thin entry points sharing those functions.

The local app and each MCP process open short SQLite connections. WAL supports concurrent readers; transactions keep updates and the search index consistent. Schema version 1 is recorded with `PRAGMA user_version`; no migration framework is needed before the second schema exists.

## Retrieval

English words and CJK bigrams are indexed with SQLite FTS5. Title, intent and tags carry more weight than source text. Queries filter out archived items and projects other than the exact requested project; personal records remain available. Returned excerpts, corrections and past decisions are candidates for the agent, not a claim that the method is suitable.

The library UI can browse all local projects; the task-oriented MCP reader enforces project scope. Recall does not create usage records. Corrections stay attached to the source and carry their own scope. Records preserve the source revision at the time of use.

## Boundaries

No model client, provider key, orchestration loop or background job queue is required. The host agent supplies reasoning. Source text is never executed or inserted as HTML. The UI renders imported content as text. The local HTTP service binds to loopback, checks the Host header, and rejects cross-origin requests.

Original uploaded files are stored in SQLite blobs and downloaded as attachments. Backups contain them as base64; this is a small personal library format, not a streaming data lake. Imports are validated before a transaction and add new bookmark IDs only.

## Source-of-truth links

- [Official MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP server tools](https://py.sdk.modelcontextprotocol.io/servers/)
- [MCP stdio client transport](https://py.sdk.modelcontextprotocol.io/client/transports/)

The project targets the installed and tested MCP SDK 2.x API (`MCPServer`); it does not contain a speculative v1 fallback.

## v0.1.2 retrieval and diagnostics

Schema 2 adds a derived FTS5 correction index. Existing correction records are indexed transactionally on first opening an older database. Source and correction results are scope-filtered independently, then combined using reciprocal rank fusion (constant 60, up to 100 distinct candidates per list). No raw BM25 scores are compared across indexes. Corrections remain attached to their original source; imported backups rebuild the derived index. The JSON interchange format remains version 1.

Usage records keep their recorded revision. APIs calculate `is_current_revision` when reading, so updates never silently turn old evidence into current evidence. A revision mismatch requests reassessment; it does not invalidate the historical observation.

`doctor` and the browser diagnostic endpoint share one function that launches the configured local MCP stdio subprocess. It lists tools and calls recall, without writing bookmarks or usage. This validates the transport, not any third-party host's behavior.
