# Short roadmap

This plan limits the initial project to one useful local product. It is a scope plan, not a release-date promise.

## v0.1 — Complete foundation

Ship the full vertical workflow in one release:

- A shared SQLite library with sources, intent, reference/method/rule distinction, project scope and bookmark revisions.
- Notes, ordinary web extraction, text-based PDFs, local text/subtitle imports and explicit link-only records.
- A usable bilingual browser UI, CLI, and standard MCP stdio interface.
- Keyword retrieval, bounded source reads, corrections and evidence-bearing usage records.
- Original files, export/import, archive/restore, example content, installation instructions and meaningful integration tests.

Acceptance: start from a clean installation, save a source, find it in the right project, read it through MCP, record a decision, add a correction and see it on the next retrieval. A different project must not receive scoped content. Export/import must preserve the same information. No false claim of automatic application or verification.

## v0.1.x — Fix what real use reveals

One short hardening pass, not new subsystems:

- Test the documented setup with a small number of real hosts; publish the actual compatibility results.
- Improve empty states, keyboard flow, import errors, install instructions and source display.
- Fix retrieval misses with concrete English/Chinese examples. Keep a small regression dataset.
- Measure setup time and whether users actually reuse or correct their bookmarks.

Exit when the main workflow is dependable for the initial users. Do not add embeddings just because they are available.

## v0.2 — Improve the existing inputs and integrations

Choose only the improvements that address observed friction:

- Better article extraction and source anchors; clearer PDF page and transcript timestamp navigation.
- A convenience capture entry point or installer for the most-used hosts.
- Optional semantic retrieval only if a measured benchmark shows useful gains over the existing keyword baseline.

Keep the same core data model and interfaces. No microservices, accounts, cloud sync, agent marketplace, autonomous experiments, or whole-video pipeline in this cycle.

## Engineering rules

- Validate external inputs once with the domain models. Use clear failures at file/network/database boundaries.
- Do not catch every exception, return empty results on failure, add duplicate validation at every internal layer, or introduce speculative compatibility branches.
- Prefer one implementation shared by adapters. Add an abstraction after a real second need, not before it.
- Tests protect behavior: project isolation, provenance, evidence rules, persistence, backup and actual MCP transport. Do not assert implementation details simply to increase test count.
