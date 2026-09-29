# Connect and verify Codex

The local preview has been exercised by the real Codex CLI and a desktop conversation on Windows. Retrieval, revision-aware reading, usage recording and readback have direct evidence below.

## Setup

Activate the Aftermark virtual environment, then run:

```sh
aftermark --data-dir .local/library connect codex
aftermark --data-dir .local/library connect codex --apply
```

The first command inspects configuration and previews the argument list. The second calls the installed `codex mcp add`. Other servers are preserved; conflicting or disabled `aftermark` entries are not overwritten. The app's **Connect an agent** page provides a command using your actual Python and library paths. Registration requires Codex on PATH.

CLI and desktop clients on the same host share MCP configuration according to the [official MCP guide](https://learn.chatgpt.com/docs/extend/mcp?surface=cli). In desktop settings, find `aftermark` under MCP servers. The official guide describes a Restart action, but the tested desktop UI showed an update screen with only Uninstall; do not uninstall it to refresh. Fully quit and reopen the app, then check tools in a fresh turn. This reload is a troubleshooting step, not a verified fix for every desktop version.

`codex mcp get aftermark` checks registration. `aftermark doctor` checks an actual MCP subprocess. Neither alone proves Codex used the collection.

## Task acceptance

1. Save a note with distinctive task keywords and an exact project name, such as `my-game`.
2. Add a relevant correction. In **Connect an agent**, enter the exact project name and generate instructions (or run `aftermark --data-dir .local/library config --project my-game`). Copy them into that project's `AGENTS.md`. This repository uses `Aftermark`; empty scope means personal knowledge only.
3. Start a fresh Codex task. Ask it to find related knowledge, read the source at the returned revision, and inspect the current implementation before making a change or decision.
4. Inspect actual tool events and the artifact. Ask it to record what it actually did, passing the revision it read as `expected_revision`. A conflict requires rereading and reassessing, not merely changing the number: a suggestion is `referenced`, `applied` needs a change, and `verified` needs check results.

Approvals still apply. In our non-interactive test, default `codex exec` refused an MCP approval even though the process exited with code 0. Rerunning with its normal `--approve-for-me` review flow allowed the requested calls. Do not disable sandboxing to force a pass. See the [official non-interactive guide](https://learn.chatgpt.com/docs/non-interactive-mode) and installed CLI help.

## Observed results — 2026-09-27

Windows, Python 3.13.9, `codex-cli 0.158.0-alpha.2.1`, configured model `gpt-6-astra`, existing ChatGPT login. These are single-run observations, not success-rate measurements.

| Test | Result |
| --- | --- |
| Default non-interactive approval | Failed at recall: approval required, policy `never`. |
| Explicit task with normal automatic review | `recall → read_bookmark(expected_revision=2) → record_usage` completed; saved outcome `referenced`. |
| Project scope | A test source scoped to another project was absent from the returned candidates. |
| Fresh task with project AGENTS.md, no tool reminder in latest prompt | Recalled and read revision 3, then included a newly added correction in the answer. |
| Automatic usage record in that fresh task | Did not happen: no `record_usage` event or new database record. |
| Desktop on September 27 | Entry visible, but this UI had no Restart action. No direct desktop calls yet. See the September 28 result below. |
| Real code changes or engineering gains | Not tested. These tasks produced checklists from labeled synthetic acceptance notes. |

The marker `AM-CODEX-014` and three evidence levels were supplied only by the saved note, not the task prompt. Both successful answers used them. The fresh run also included the new correction to list desktop acceptance separately. This proves source influence in these tasks, not reliable autonomous recall or automatic outcome logging in every task.

The [evidence summary](evidence/codex-0.1.4.json) contains real statuses, revisions and a saved usage ID. Raw local logs stay outside Git because transcripts can contain private sources and client context. Test notes are explicitly labeled and can be archived after desktop acceptance.

## Desktop follow-up — 2026-09-28

The continuing desktop conversation exposed all five Aftermark tools. Direct `recall(project="Aftermark")` returned the test source; `read_bookmark(expected_revision=3)` returned the source and both corrections. The same task under `Aftermark-desktop-isolation` returned no candidates. `record_usage(outcome="referenced")` succeeded, and a second read returned that exact persisted record at revision 3. See [desktop evidence](evidence/codex-desktop-0.1.5.json).

These were calls from this desktop conversation, not a separate CLI process. The latest user message was just a continuation, but this conversation already contained an explicit acceptance task and project instructions. It is not an unguided or blinded recall benchmark. The precise action that refreshed the tool catalog was not established, so reopening the app remains troubleshooting advice rather than a proven cause.

The earlier correction saying desktop acceptance was pending describes the prior state. It remains in the test source as historical context; fresh tool evidence establishes the current result. Synthetic test notes have not been silently rewritten or presented as real research.

## Revision-bound usage — 0.3.0, September 28

A real 0.2.0 reproduction read revision 1, changed the source, then incorrectly recorded that read against revision 2. The 0.3 change requires the actual read revision in new usage requests, checks it and inserts within one write transaction. Reload the MCP connection after updating; the new argument is required.

Two real Codex CLI runs used an isolated library containing the maintainer-authored reproduction record, plus explicit acceptance corrections and a scope distractor. The prompt asked for the workflow; the bookmarked source supplied the initial code/test targets. This evaluates real project code, but does not establish research benefit or autonomous recall.

| Check | Observed result |
| --- | --- |
| First run | MCP conflict/recovery/readback passed; shell initialization failed and a per-command escalation was rejected. Recorded referenced, not verified. |
| First-run finding | Generic SDK errors concealed the conflict reason. A narrow ToolError conversion now exposes revision numbers and a reread instruction. |
| Second run | User explicitly approved per-command escalation through normal review. No global sandbox bypass. |
| Actual code checks | Codex inspected Store.record, ran store/content/correction + HTTP checks (3 passed), then the CLI check in the new correction (1 passed). Both runs emitted non-fatal pytest cache permission warnings. |
| Stale write | Read v2, added the requested correction to make v3, then writing v2 was refused with expected/current versions and recovery guidance. No new history appeared. |
| Recovery | Recalled and read v3, reassessed and recorded verified with the actual checks; a separate read returned the same usage ID at v3. |
| Isolation | Another project returned no candidates and could not read the source by ID. |

[Machine-readable evidence](evidence/codex-0.3.0.json) includes source hashes, tool-event summaries and persisted record IDs. Raw logs stay local. The first record remains referenced at v2; the second is verified at v3. At that release, the desktop catalog predated the new argument; see the subsequent check below.

## URL import — 0.4.0, September 29

The real Codex CLI imported the [official MCP error-handling documentation](https://py.sdk.modelcontextprotocol.io/servers/handling-errors/) into a separate acceptance library. It recalled ToolError, read revision 1, inspected `src/aftermark/mcp_server.py`, and concluded the documented error handling was already implemented. It recorded **referenced**, then read back the same record. No new code change or improvement was claimed.

It also imported a URL serving a labeled synthetic PDF, recalled its content and read `page-1` at revision 1 with a citation. A different project returned no candidates. Importing a `video/mp4` URL returned a clear unsupported-format error and no success metadata. Independent store inspection found exactly two bookmarks, one referenced usage record and no video bookmark. Ten MCP calls completed the requested workflow, including the expected failed import.

The test used normal automatic approval. Its initial launcher failed before execution because an environment override used JSON instead of TOML; correcting that argument enabled the run. Loopback fixtures explicitly bypass the test environment's HTTP proxy. These facts and the source/record IDs are in [0.4 evidence](evidence/codex-0.4.0.json).

Separately, this desktop conversation successfully supplied expected_revision=3 to record_usage and read back the saved referenced record on the synthetic acceptance note. That validates the new writeback contract here. This desktop session does not yet expose import_url: reload MCP after upgrading to use it. Desktop URL import and other hosts remain unverified. The prompt specified the workflow, so this is not an autonomous-recall benchmark.

## Long-source excerpts — 0.5.0, September 29

The first review prompt asked Codex to assess the excerpt implementation and run relevant checks. It did not name tool calls; the existing AGENTS.md supplied recall/read/record guidance. Codex retrieved a maintainer-authored defect-description note, read page 2 at revision 1, inspected code and passed 25 focused checks. It found an uncovered boundary: alpha at 2000 and beta at 3100 fit together, but fixed leading context selected only alpha.

The first usage report mistakenly claimed the descriptive note itself proved the old excerpt started at 0. Codex subsequently appended a referenced record explicitly retracting that claim. The original record was not silently rewritten. The note is controlled acceptance material, not an external paper or the before/after fixture. [Client evidence](evidence/codex-0.5.0.json) preserves the distinction and record IDs.

After adding keyword-start windows, a second Codex run checked the fix, including exact-fit and just-outside edges, and passed 28 focused tests. It recorded verified for those actual code checks and read back the same usage ID. That second readback was explicitly requested. The independent [0.4 versus 0.5 comparison](evidence/excerpts-0.5.0.json) uses identical controlled English/Chinese sources and actual installed versions.

These runs demonstrate source consultation under project rules and a useful review finding. They do not establish reliable spontaneous recall, research benefit or a broad retrieval success rate. The current desktop session and other hosts were not used to validate the new excerpt algorithm.
