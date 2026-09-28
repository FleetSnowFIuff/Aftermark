# Changelog

## 0.1.5 — 2026-09-28

- Verify direct Aftermark MCP calls in the current Codex desktop conversation, including project isolation and persisted usage readback.
- Correct setup guidance for desktop versions without a Restart button; preview and conflict states now give appropriate next steps.
- Publish desktop evidence and synchronize bilingual setup and introduction pages. Synthetic acceptance remains separate from claims of engineering gains.

## 0.1.4 — 2026-09-27

- Add explicit `connect codex` preview/apply commands, preserve conflicting registrations and provide a copyable command in the bilingual UI.
- Declare MCP read/write and local-only tool annotations without bypassing client approvals.
- Add project instructions and real Codex CLI evidence: explicit recall/read/record passed; a fresh project-guided task used a new correction but did not record usage automatically.
- Document the initial approval failure and pending desktop acceptance. The synthetic checklist task does not establish engineering gains.

## 0.1.3 — 2026-09-27

- Derive PDF page and SRT/VTT subtitle locations from saved text, and include relevant locations in task recall.
- Read a selected source segment through the shared CLI/MCP reader, with bounded pagination, project scope and optional revision checks.
- Add a source-location selector and copyable revision-bearing citations to the bilingual local UI.
- Keep original files, backup format and database schema unchanged. Locations describe saved text; no video analysis or inferred timestamps.

## 0.1.2 — 2026-09-27

- Search relevant corrections as well as source text, with both bookmark and correction project scopes enforced. Show where each result matched.
- Mark usage records that refer to an older bookmark revision without rewriting the original outcome or evidence.
- Add `aftermark doctor` and a bilingual connection-check button that start a real local MCP process and call recall without writing bookmarks or usage.
- Upgrade schema v1 to v2 automatically by indexing existing corrections. JSON backup format remains version 1; old application versions cannot open schema v2.
- Point the introduction page's install action directly to setup instructions.

## 0.1.1 — 2026-09-27

- Save imported tags, source text and original files in one operation; reject invalid tags before writing. Imports start at revision 1.
- Allow extracted web titles and file names to supply the bookmark title. Show when source text comes from an import.
- Keep projects containing only archived bookmarks available in the project filter.
- Add Windows and macOS/Linux setup/start scripts using the same project-local library.
- Add bilingual download/install guidance, and a script to synchronize the standalone page with the app introduction.

## 0.1.0 — 2026-09-26

- First local workflow: sources, intent, scope, retrieval, corrections and evidence-bearing usage records.
- Bilingual browser UI, CLI, MCP stdio, original files and JSON backups.
