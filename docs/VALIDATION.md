# Validation — current local preview

Windows, Python 3.13.9. 53 automated tests pass (`-p no:cacheprovider` on the final suite).

| Area | Evidence |
| --- | --- |
| Core library | Project isolation, English/Chinese keyword retrieval, scoped corrections, archival exclusion, original-file backups and restore |
| Revisions | Required read revision on new records, atomic conflict rejection/recovery through Store/HTTP/CLI/MCP, unchanged backup roundtrip, stale usage flags, revision-aware reads and migration from schema 1 to 2 without rewriting exported data |
| Sources | Real two-page PDF extraction, retained original bytes, SRT/VTT timing, Unicode offsets and bounded reads |
| URL imports | Loopback HTTP fixtures through UI API/CLI/MCP; redirected extensionless PDF, retained bytes and backup roundtrip, page reads, project isolation, metadata-only tool response, empty/invalid/unsupported input and download limits |
| Interfaces | HTTP workflows, real MCP stdio calls and read/write annotations, CLI/API diagnostics |
| Onboarding | Codex preview/apply and conflict handling; project-specific instructions via CLI/API, Chinese/quoted names, personal scope and unchanged MCP connection |
| Codex clients | Actual CLI and desktop recall/read/record/readback, with limitations documented in [CODEX.md](CODEX.md) |

Project-guidance and revision-bound recording UI have API and JavaScript syntax checks; interactive browser acceptance remains pending. Earlier manual browser checks do not validate subsequent UI changes. macOS/Linux launcher execution and other agent hosts remain unverified.

The 0.4.0 wheel was installed into a fresh Windows virtual environment; version reporting, actual MCP doctor handshake/recall with all six tools, and PDF URL import passed. Packaged application files were compared byte-for-byte with the release source. The introduction's inline JavaScript and the app script passed syntax checks; the standalone and packaged introduction match.

The [CI template](ci-example.yml) is not enabled because the current publishing credential lacks workflow scope. No remote CI success is claimed.

## Current real-client acceptance

In 0.4, Codex CLI made ten actual Aftermark calls: imported official MCP ToolError documentation, recalled/read it at revision 1, compared existing code and recorded/read back referenced; imported a synthetic PDF URL and read page 1; checked another project returned no candidates; received an actionable unsupported-video error. Independent store inspection found exactly two imports and one referenced record, with no failed-video bookmark. See [0.4 evidence](evidence/codex-0.4.0.json).

The initial acceptance launcher failed on its environment override syntax before Codex ran; correcting the TOML override allowed the real run. A protocol test initially hit an environment proxy for loopback; the test child now explicitly excludes loopback from proxies. These were harness setup fixes, not hidden application fallbacks.

The continuing desktop conversation also recorded a referenced result with expected_revision=3 and independently read back the same usage ID. It used the earlier synthetic acceptance note. New desktop URL import remains untested because this session's tool catalog has not reloaded. Official documentation and synthetic fixtures remain distinguished. None of these guided checks measures engineering gain or reliable autonomous recall.

The earlier 0.3 Codex run inspected a real reproduced defect, ran four focused checks, recovered from a stale revision and read back verified. Its first blocked run remains referenced. See [0.3 evidence](evidence/codex-0.3.0.json).

## Earlier client checks

A directly prompted Codex task completed retrieval, source reading and usage recording. A fresh task with project rules read a newly added correction, but did not record usage automatically. The desktop conversation later completed direct tool calls and read back its persisted record. These were labeled synthetic acceptance notes, not measured improvements to real project code. The initial non-interactive approval failure remains in the evidence.

## Manual task acceptance

1. Save a real source with intent and the exact project name.
2. Generate instructions for that project, connect the agent and start a fresh task.
3. Check the actual retrieved source, correction and revision; another project must not receive scoped content.
4. Inspect the code change or decision and the submitted evidence. Record only what happened.
5. Export/import into a disposable library and confirm the same information survives.

Keep test libraries separate from real project evidence. The schema remains 2 and JSON backups remain format 1.
