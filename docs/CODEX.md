# Connect and verify Codex

v0.1.4 was exercised by the real Codex CLI on Windows. The current desktop conversation has not passed its own acceptance test.

## Setup

Activate the Aftermark virtual environment, then run:

```sh
aftermark --data-dir .local/library connect codex
aftermark --data-dir .local/library connect codex --apply
```

The first command inspects configuration and previews the argument list. The second calls the installed `codex mcp add`. Other servers are preserved; conflicting or disabled `aftermark` entries are not overwritten. The app's **Connect an agent** page provides a command using your actual Python and library paths. Registration requires Codex on PATH.

CLI and desktop clients on the same host share MCP configuration according to the [official MCP guide](https://learn.chatgpt.com/docs/extend/mcp?surface=cli). In desktop settings, open **MCP servers** and restart `aftermark`. If an externally added entry has not appeared, fully quit and reopen the app, then check again. This reload is a troubleshooting step, not a verified fix for every desktop version. Start a fresh turn and check available tools.

`codex mcp get aftermark` checks registration. `aftermark doctor` checks an actual MCP subprocess. Neither alone proves Codex used the collection.

## Task acceptance

1. Save a note with distinctive task keywords and an exact project name, such as `my-game`.
2. Add a relevant correction. Copy the instructions from **Connect an agent** into that project's `AGENTS.md`, with its exact project name. This repository uses `Aftermark`.
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
| Current desktop conversation | Pending: the user reported the server was not visible in desktop settings after CLI registration. |
| Real code changes or engineering gains | Not tested. These tasks produced checklists from labeled synthetic acceptance notes. |

The marker `AM-CODEX-014` and three evidence levels were supplied only by the saved note, not the task prompt. Both successful answers used them. The fresh run also included the new correction to list desktop acceptance separately. This proves source influence in these tasks, not reliable autonomous recall or automatic outcome logging in every task.

The [evidence summary](evidence/codex-0.1.4.json) contains real statuses, revisions and a saved usage ID. Raw local logs stay outside Git because transcripts can contain private sources and client context. Test notes are explicitly labeled and can be archived after desktop acceptance.
