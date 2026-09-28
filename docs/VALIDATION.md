# Validation — current local preview

Windows, Python 3.13.9. 37 automated tests pass.

| Area | Evidence |
| --- | --- |
| Core library | Project isolation, English/Chinese keyword retrieval, scoped corrections, archival exclusion, original-file backups and restore |
| Revisions | Stale usage flags, revision-aware reads and migration from schema 1 to 2 without rewriting exported data |
| Sources | Real two-page PDF extraction, retained original bytes, SRT/VTT timing, Unicode offsets and bounded reads |
| Interfaces | HTTP workflows, real MCP stdio calls and read/write annotations, CLI/API diagnostics |
| Onboarding | Codex preview/apply and conflict handling; project-specific instructions via CLI/API, Chinese/quoted names, personal scope and unchanged MCP connection |
| Codex clients | Actual CLI and desktop recall/read/record/readback, with limitations documented in [CODEX.md](CODEX.md) |

The new project-guidance UI has API and JavaScript syntax checks; interactive browser acceptance remains pending. Earlier manual browser checks do not validate subsequent UI changes. macOS/Linux launcher execution and other agent hosts remain unverified.

The [CI template](ci-example.yml) is not enabled because the current publishing credential lacks workflow scope. No remote CI success is claimed.

## What the client checks establish

A directly prompted Codex task completed retrieval, source reading and usage recording. A fresh task with project rules read a newly added correction, but did not record usage automatically. The desktop conversation later completed direct tool calls and read back its persisted record. These were labeled synthetic acceptance notes, not measured improvements to real project code. The initial non-interactive approval failure remains in the evidence.

## Manual task acceptance

1. Save a real source with intent and the exact project name.
2. Generate instructions for that project, connect the agent and start a fresh task.
3. Check the actual retrieved source, correction and revision; another project must not receive scoped content.
4. Inspect the code change or decision and the submitted evidence. Record only what happened.
5. Export/import into a disposable library and confirm the same information survives.

Keep test libraries separate from real project evidence. The schema remains 2 and JSON backups remain format 1.
