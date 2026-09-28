# Changelog

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
