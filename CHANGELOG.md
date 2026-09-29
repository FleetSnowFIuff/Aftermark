# Changelog

## 0.5.0 — 2026-09-29

- Show a long-source passage covering more distinct task keywords instead of centering only the first match. Use whole English tokens and overlapping Chinese bigrams; repeated generic words add no score.
- Keep excerpts as exact original-text slices, including Unicode lowercase expansions. Preserve PDF/subtitle locations and expose `excerpt_matched_terms` separately from matches in titles, intent and corrections.
- Real Codex review found a boundary where fixed leading context displaced two keywords that fit in one window. Include keyword-start windows and add exact-boundary regression checks.
- 63 automated tests passed; the second real Codex review passed 28 focused checks and recorded/read back actual results. Preserve its first inaccurate usage claim and the explicit retraction in the evidence summary.
- Compare the released 0.4 wheel and new implementation on the same English/Chinese fixtures. No bookmark-ranking, database-schema, source-content or backup-format change.

## 0.4.0 — 2026-09-29

- Import webpage/text and text PDF URLs through one shared UI/CLI/MCP path. Retain PDF original bytes, requested URL and page citations, including redirects and extensionless URLs.
- Add MCP `import_url` with explicit external-network/write annotations. Return metadata only; require a subsequent source read before relying on the import. Link-only saving remains available.
- Bound HTML/text downloads to 5 MB and PDFs to 20 MB. Reject unsupported media, empty text and unreadable PDFs without saving a bookmark; surface actionable MCP errors.
- Real Codex CLI imported official documentation, compared existing code and recorded/read back referenced; imported/read a synthetic PDF page; checked isolation and unsupported-video failure. Desktop revision-bound writeback/readback also passed. Desktop URL import remains unverified.
- Update bilingual onboarding and introduction. No database or backup-format change.

## 0.3.0 — 2026-09-28

- Bind every new usage report to the revision actually read. Reject stale reports before writing history; serialize the check and insert in one transaction.
- Require `expected_revision` in MCP/HTTP usage requests and `--revision` in CLI recording. This is an input contract change; reload MCP clients and regenerate project instructions. Existing records, schema 2 and backup format 1 are unchanged.
- The web usage form retains its opened revision and explains conflicts without silently retrying.
- Real Codex CLI acceptance exercised stale-write rejection, rereading corrections, four actual code checks, verified recording/readback and project isolation. Preserve the first blocked run as referenced.
- Expose the expected/current revision and recovery instruction through MCP ToolError; this issue was discovered by the first real client run.
- Preserve the redesigned bilingual introduction and its GitHub-first primary button.

## 0.2.0 — 2026-09-28

- Generate project-specific agent instructions from the connection page or `config --project NAME`; empty scope explicitly selects personal knowledge.
- Consolidate onboarding, source-reading guidance and validation into current-function documentation.
- Use a fixed current-release source ZIP link. Consolidate GitHub Releases into the current preview; Git tags and source history remain available.
- Preserve the existing library schema and backup format.

## Early previews — 0.1.x

Established local sources and intent, scoped keyword/correction retrieval, original-file backups, PDF/subtitle citations, revision-aware reading, evidence-bearing usage records, Codex registration and real CLI/desktop acceptance. Detailed implementation history remains in Git; client evidence is linked from `docs/CODEX.md`.
