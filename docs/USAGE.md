# CLI and source reading

Activate your environment. Use `--data-dir .local/library` from the project folder to share the launcher's library.

```sh
aftermark --data-dir .local/library add --title "Keep our brand" --text "Borrow hierarchy, keep the existing palette." --intent "Keep our brand colors." --role rule --project my-site
aftermark --data-dir .local/library add --file paper.pdf
aftermark --data-dir .local/library recall "improve layout" --project my-site
aftermark --data-dir .local/library config --project my-site
aftermark --data-dir .local/library correct BOOKMARK_ID "For prototypes only." --project my-site
aftermark --data-dir .local/library export backup.json
aftermark --data-dir .local/library import backup.json
```

`config --project ""` explicitly chooses personal knowledge. Omitting `--project` retains generic instructions that ask the agent to use an exact project name. No client configuration is rewritten by `config`.

Recall returns `excerpt_locations`. Pass an actual location ID and revision to MCP `read_bookmark` as `anchor` and `expected_revision`, or use:

```sh
aftermark --data-dir .local/library read BOOKMARK_ID --project my-site --anchor page-2 --revision 1
```

Use values returned by recall. A changed revision is rejected. `--offset` counts Unicode code points relative to the selected segment, and `--limit` bounds returned text. PDF pages and subtitle timestamps derive from saved text, not video analysis. The UI can copy revision-bearing citations.

Usage records:

```sh
aftermark --data-dir .local/library record BOOKMARK_ID --task "Adjust layout" --project my-site --outcome applied --reason "Fits this page" --evidence "src/page.css: spacing change"
```

Use `referenced` for reading or advice, `applied` for a real change, `verified` for actual checks with results, or `skipped` with a reason. Aftermark stores the report; it does not execute those checks.

`doctor` launches a real MCP subprocess and checks discovery/recall without adding bookmarks or usage. This is separate from testing your chosen client.
