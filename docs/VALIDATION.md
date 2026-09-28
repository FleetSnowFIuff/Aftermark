# Validation — current local preview

Windows, Python 3.13.9. 43 automated tests pass (`-p no:cacheprovider` on the final suite).

| Area | Evidence |
| --- | --- |
| Core library | Project isolation, English/Chinese keyword retrieval, scoped corrections, archival exclusion, original-file backups and restore |
| Revisions | Required read revision on new records, atomic conflict rejection/recovery through Store/HTTP/CLI/MCP, unchanged backup roundtrip, stale usage flags, revision-aware reads and migration from schema 1 to 2 without rewriting exported data |
| Sources | Real two-page PDF extraction, retained original bytes, SRT/VTT timing, Unicode offsets and bounded reads |
| Interfaces | HTTP workflows, real MCP stdio calls and read/write annotations, CLI/API diagnostics |
| Onboarding | Codex preview/apply and conflict handling; project-specific instructions via CLI/API, Chinese/quoted names, personal scope and unchanged MCP connection |
| Codex clients | Actual CLI and desktop recall/read/record/readback, with limitations documented in [CODEX.md](CODEX.md) |

Project-guidance and revision-bound recording UI have API and JavaScript syntax checks; interactive browser acceptance remains pending. Earlier manual browser checks do not validate subsequent UI changes. macOS/Linux launcher execution and other agent hosts remain unverified.

The 0.3.0 wheel was installed into a fresh Windows virtual environment; version reporting and an actual MCP doctor handshake/recall passed. Package files were checked against the release source.

The [CI template](ci-example.yml) is not enabled because the current publishing credential lacks workflow scope. No remote CI success is claimed.

## Current real-client acceptance

Codex CLI read the actual reproduced revision-attribution defect, inspected the fix and ran four focused checks from the source and its correction. It observed an explicit stale-write refusal, reread v3, recorded verified and independently read that record back. Project isolation passed. The first run was blocked by the shell/approval environment and stayed referenced; the user then authorized single-command escalation for the second run. Both CLI pytest commands passed with cache-write permission warnings. See [0.3 evidence](evidence/codex-0.3.0.json).

The separate test library contains a maintainer-authored real defect record and controlled corrections, not user research. This is prompted acceptance, not measured engineering gain or an unguided recall benchmark. New desktop writeback still needs a refreshed tool catalog and its own run.

## Earlier client checks

A directly prompted Codex task completed retrieval, source reading and usage recording. A fresh task with project rules read a newly added correction, but did not record usage automatically. The desktop conversation later completed direct tool calls and read back its persisted record. These were labeled synthetic acceptance notes, not measured improvements to real project code. The initial non-interactive approval failure remains in the evidence.

## Manual task acceptance

1. Save a real source with intent and the exact project name.
2. Generate instructions for that project, connect the agent and start a fresh task.
3. Check the actual retrieved source, correction and revision; another project must not receive scoped content.
4. Inspect the code change or decision and the submitted evidence. Record only what happened.
5. Export/import into a disposable library and confirm the same information survives.

Keep test libraries separate from real project evidence. The schema remains 2 and JSON backups remain format 1.
