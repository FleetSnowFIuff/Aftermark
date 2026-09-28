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
4. Inspect actual tool events and the artifact. Ask it to record what it actually did: a suggestion is `referenced`, `applied` needs a change, and `verified` needs check results.

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
