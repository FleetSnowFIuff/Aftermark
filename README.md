# Aftermark

[GitHub](https://github.com/FleetSnowFIuff/Aftermark) · [MIT](LICENSE)

**Save what works. Teach your agent when to use it.**

[简体中文](README.zh-CN.md) · [Version plan](docs/ROADMAP.md) · [Architecture](docs/ARCHITECTURE.md) · [Validation](docs/VALIDATION.md)

Aftermark is a local bookmark library for coding agents. Keep a source, why you saved it, which project it applies to, and corrections from real work. Use the same collection from a browser, the CLI, or an MCP-compatible agent.

**v0.1 is a working local foundation.** It does not train a model, understand an unread video, or guarantee that an agent will recall the right thing. It retrieves keyword candidates; your chosen agent checks applicability against the project.

## Start locally

Requires Python 3.11 or newer. From this repository:

```sh
python -m venv .venv
# Windows:
.venv\Scripts\python -m pip install -e .
.venv\Scripts\aftermark serve --open
# macOS / Linux:
.venv/bin/python -m pip install -e .
.venv/bin/aftermark serve --open
```

Open **http://127.0.0.1:43821**. No account, model download, or extra model API key is required. Installation and fetching external pages require internet access; notes, search, PDF parsing, and the local UI work offline after installation.

Try **Import three examples**, then **Use in a task** with `jump input buffering` or `跳跃输入容错`. Inspect the source, add a project-specific correction, and search again.

## What works in v0.1

- Notes, Markdown/TXT, ordinary web-page text, text-based PDFs with page markers, and video links with manually supplied SRT/VTT transcripts.
- An optional intent, one project scope, and a clear distinction between reference material, a method to consider, and an explicit user requirement.
- English tokens and CJK bigram retrieval. No embeddings, model downloads, or background services beyond the local app.
- Source reading, scoped corrections, archive/restore, and honest usage records: referenced, applied, verified, or skipped.
- Original uploaded files retained locally. JSON backup/import includes sources, attachments, corrections, and usage; existing IDs are skipped instead of overwritten.
- Chinese/English local UI, CLI, and a standard MCP stdio server sharing one SQLite database.

## Connect your agent

Open **Connect an agent**, or run:

```sh
aftermark config
```

Copy the generated MCP configuration and suggested instructions into your chosen host. The generated command uses your actual Python executable and absolute data directory. It does not silently modify any client configuration.

MCP tools:

| Tool | Purpose |
| --- | --- |
| `recall` | Find candidates for a task and exact project name; include relevant corrections and previous decisions |
| `read_bookmark` | Read source text in pages without marking it as used |
| `save_bookmark` | Save text or a link at the user's request |
| `add_correction` | Remember an explicit correction and its project scope |
| `record_usage` | Record the actual decision and evidence |

The `use_my_knowledge` MCP prompt starts the workflow explicitly. Automatic tool use depends on your host and model. Standard protocol tests do not establish compatibility with every product; see [validation status](docs/VALIDATION.md) for the exact tested scope.

## CLI examples

```sh
aftermark add --title "Keep our brand" --text "Borrow the hierarchy, not the color palette." --intent "Keep our existing brand colors." --role rule --project my-site
aftermark add --title "A reference" --url https://example.com --fetch
aftermark add --file paper.pdf --intent "Check assumptions before applying this method."
aftermark recall "improve page layout" --project my-site
aftermark show BOOKMARK_ID
aftermark correct BOOKMARK_ID "For prototypes only." --project my-site
aftermark record BOOKMARK_ID --task "Adjust layout" --project my-site --outcome applied --reason "Fits this page" --evidence "src/page.css: spacing change"
aftermark export backup.json
aftermark import backup.json
```

Use `aftermark --data-dir PATH ...` or `AFTERMARK_HOME` to choose a library. All clients must point to the same library. The default location is `%LOCALAPPDATA%\Aftermark` on Windows, `~/Library/Application Support/Aftermark` on macOS, or `$XDG_DATA_HOME/aftermark` (`~/.local/share/aftermark`) on Linux.

## Boundaries

- No automatic transcription, video-frame understanding, OCR, browser extension, cloud sync, multi-user hosting, or autonomous code editing in v0.1.
- Web extraction does not execute JavaScript, log into sites, or bypass paywalls. A failed fetch remains an error; a link-only bookmark is explicitly labeled.
- “Verified” means a user or agent submitted evidence. Aftermark does not execute the check or certify the result. Each record keeps the bookmark revision it refers to.
- Project scopes are exact names, not automatically detected repositories. An empty task scope uses only personal bookmarks. Corrections do not override higher-priority user or host instructions.
- The web server binds to loopback and rejects other origins. This is a personal local application; do not expose it as a public service.
- Imports are trusted backups, not a public ingestion endpoint. Review imported sources and requirements before using them with an agent.

## Development

```sh
python -m pip install -e ".[dev]"
python -m pytest
python -m build
```

The project deliberately uses a small stack: Python, SQLite, FastAPI, the official MCP SDK, and plain browser JavaScript. Input validation lives at boundaries. Internal failures are not converted into empty success responses.

## License

MIT. Example notes are original project content. Imported sources keep their original rights and provenance.
