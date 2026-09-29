# CLI and source reading

Activate your environment. Use `--data-dir .local/library` from the project folder to share the launcher's library.

```sh
aftermark --data-dir .local/library add --title "Keep our brand" --text "Borrow hierarchy, keep the existing palette." --intent "Keep our brand colors." --role rule --project my-site
aftermark --data-dir .local/library add --file paper.pdf
aftermark --data-dir .local/library add --url https://example.com/paper.pdf --fetch --project my-game
aftermark --data-dir .local/library recall "improve layout" --project my-site
aftermark --data-dir .local/library config --project my-site
aftermark --data-dir .local/library correct BOOKMARK_ID "For prototypes only." --project my-site
aftermark --data-dir .local/library export backup.json
aftermark --data-dir .local/library import backup.json
```

`config --project ""` explicitly chooses personal knowledge. Omitting `--project` retains generic instructions that ask the agent to use an exact project name. No client configuration is rewritten by `config`.

## Import a URL

In the app, paste a URL and keep **Import webpage text or PDF** checked. From an agent, ask it to import the URL into your exact project using `import_url`. The CLI uses `add --url URL --fetch`. These share one importer: declared HTML/plain text/Markdown up to 5 MB, or `application/pdf` up to 20 MB. PDF downloads retain their original bytes, source URL and page markers, including when the URL redirects or has no `.pdf` suffix.

`import_url` returns metadata and the saved revision, not the full source. Follow with `recall` and `read_bookmark(expected_revision=...)` before relying on the material. Importing is not reading, adoption or verification. Each successful import creates a new bookmark; it does not deduplicate or refresh an existing one. Do not retry a successful call.

Without `--fetch` (or with the checkbox off), save a title and URL as a link only. MCP `save_bookmark` also does not fetch URLs. Video URLs must use that path; supply SRT/VTT separately for searchable timing. Login, JavaScript rendering, OCR and automatic transcription are unsupported. HTTP, unsupported-format, empty-text, unreadable-PDF and size errors do not save a bookmark. Servers must send a supported Content-Type; binary downloads labeled `application/octet-stream` are not guessed to be PDFs.

Recall returns an original-text excerpt of at most 1,200 Unicode code points. In long sources, keyword-anchored windows are compared by distinct query-term coverage; repeating one word adds no score. Whole English tokens and overlapping Chinese bigrams follow the existing index's token rules. `matched_terms` covers all matching fields, while `excerpt_matched_terms` identifies complete keywords inside the returned passage. A title/correction-only match can have an empty excerpt-term list and a passage from the beginning. This is lexical selection, not a semantic summary or an applicability score. Bookmark ranking is unchanged.

`excerpt_start` counts original Unicode code points, even where lowercase conversion changes string length. Recall also returns `excerpt_locations`. Pass an actual location ID and revision to MCP `read_bookmark` as `anchor` and `expected_revision`, or use:

```sh
aftermark --data-dir .local/library read BOOKMARK_ID --project my-site --anchor page-2 --revision 1
```

Use values returned by recall. A changed revision is rejected. `--offset` counts Unicode code points relative to the selected segment, and `--limit` bounds returned text. PDF pages and subtitle timestamps derive from saved text, not video analysis. The UI can copy revision-bearing citations.

Usage records:

```sh
aftermark --data-dir .local/library record BOOKMARK_ID --revision 1 --task "Adjust layout" --project my-site --outcome applied --reason "Fits this page" --evidence "src/page.css: spacing change"
```

Use the revision actually read, not a guessed latest version. MCP `record_usage` and HTTP usage requests require `expected_revision`; the web form submits the revision shown when it was opened. Missing revisions are rejected. A changed source returns HTTP 409 (MCP tool error / CLI exit 1); no record is written. Reread the source and corrections, reassess the work, then submit the revision you read. Do not just substitute the newer number. Existing JSON backups do not gain this request-only field.

Use `referenced` for reading or advice, `applied` for a real change, `verified` for actual checks with results, or `skipped` with a reason. Aftermark stores the report; it does not execute those checks.

`doctor` launches a real MCP subprocess and checks discovery/recall without adding bookmarks or usage. This is separate from testing your chosen client.
