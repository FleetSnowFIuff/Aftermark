# Aftermark

**Save what works. Teach your agent when to use it.**

[简体中文](README.zh-CN.md) · [Download current release](https://github.com/FleetSnowFIuff/Aftermark/releases/latest) · [MIT](LICENSE)

A local bookmark library for coding agents. Keep a source, why you saved it, the project it applies to, and corrections from real work. Your browser, CLI and MCP-compatible agent share one collection.

## Start in three steps

Requires **Python 3.11+**. [Download the source ZIP](https://github.com/FleetSnowFIuff/Aftermark/releases/latest/download/Aftermark-source.zip), extract it, then:

| Platform | Install once | Open the app |
| --- | --- | --- |
| Windows | Double-click `setup.cmd` | Double-click `start-aftermark.cmd` |
| macOS / Linux | `sh setup.sh` | `sh start-aftermark.sh` |

1. Open **http://127.0.0.1:43821**, save a note or import the three examples.
2. In **Connect an agent**, copy the Codex setup command or your host's MCP configuration.
3. Choose the exact project name, generate its instructions and add them to your agent's project rules. Try a relevant task and inspect what it actually used.

Empty project means personal/global bookmarks only. Generating instructions changes no host files. Automatic recall depends on your host and instructions.

No account or extra model API key is needed for Aftermark. Installation and fetching webpages need internet; local notes, PDFs and keyword search work offline afterward. The project is not published to PyPI: use the source ZIP or the wheel on the release page.

## What you can keep

| Source | Supported |
| --- | --- |
| Your own knowledge | Notes, Markdown, TXT, intent and scoped corrections |
| Web | Ordinary page text, or explicitly link-only bookmarks |
| Papers | Text PDFs, retained original files and page citations |
| Videos | Links and supplied SRT/VTT subtitles with timestamp locations |

Search finds task keywords in sources and applicable corrections. Read the matching page or subtitle segment, then decide with your agent whether it fits the project. Usage records distinguish referenced, applied, verified and skipped; changed sources leave older evidence clearly marked. A usage record must include the revision actually read. If the source changes during the task, reread its content and corrections and reassess before recording.

## Connect and use

In an activated environment:

```sh
aftermark --data-dir .local/library config --project my-game
aftermark --data-dir .local/library connect codex
aftermark --data-dir .local/library connect codex --apply
```

The first command generates project-specific instructions. The next previews Codex registration; `--apply` registers it through Codex's CLI and preserves conflicting entries. Other MCP hosts use the generated JSON. Tools are `recall`, `read_bookmark`, `save_bookmark`, `add_correction` and `record_usage`.

**Upgrading to 0.3:** new usage requests require `expected_revision` (CLI: `record --revision N`). Existing history and backups are unchanged. Restart running Aftermark services, reload your agent’s MCP connection and regenerate project instructions. Older clients that omit the revision receive an error instead of silently attributing work to a new source.

[Codex setup and real-client evidence](docs/CODEX.md) · [CLI and source reading](docs/USAGE.md)

## Does it work?

In 0.3, a real Codex CLI run read an observed project defect from Aftermark, inspected the fix, ran four relevant checks, recovered from a stale-revision rejection and read back its persisted `verified` record. The first blocked run remains recorded as `referenced`. This was a guided acceptance task in a separate library, not a productivity or unguided-recall benchmark. Earlier desktop calls validated the basic workflow; the new desktop writeback contract and other hosts remain unverified. [Exact validation scope](docs/VALIDATION.md).

## Your data

The launchers use `.local/library` inside the project. Use `--data-dir .local/library` from this directory to access it from the CLI. Without that flag, the default is `%LOCALAPPDATA%\Aftermark` on Windows, `~/Library/Application Support/Aftermark` on macOS, or `$XDG_DATA_HOME/aftermark` on Linux. `AFTERMARK_HOME` can also select a directory. All clients must use the same library.

JSON export/import includes original files and history. Existing IDs are skipped on import. Back up before upgrades; schema 2 and JSON backup format 1 remain unchanged in this release. The app is for personal, local use and binds to loopback.

## Limits

Keyword retrieval, not semantic search. No OCR, automatic video transcription, frame understanding or cloud sync. Web extraction does not execute JavaScript or bypass login. Usage evidence is submitted by the user or agent; Aftermark does not independently verify it. Sources remain references and cannot override higher-priority instructions.

## Development

```sh
python -m pip install -e ".[dev]"
python -m pytest
python -m build
```

Python, SQLite, FastAPI, the official MCP SDK and plain browser JavaScript. [Architecture](docs/ARCHITECTURE.md) · [Short roadmap](docs/ROADMAP.md) · [Changelog](CHANGELOG.md).

MIT. Example notes are original project content. Imported sources retain their original rights.
