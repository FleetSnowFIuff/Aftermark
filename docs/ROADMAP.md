# Short roadmap

The current local preview contains the complete save → retrieve → read → record → correct workflow, shared by the UI, CLI and MCP. URL imports now fetch ordinary webpage text and text PDFs through all three interfaces. Project-specific onboarding and current-release downloads are part of that foundation.

Next, in order:

1. Repeat the guided project-defect acceptance on a user-selected research or game method. The revision workflow is now verified in Codex CLI; measure actual decision quality next, without treating guided tests as automatic recall.
2. Continue fixing observed retrieval misses. The first English/Chinese passage regression set now covers later keyword clusters, token boundaries, Unicode offsets and PDF/subtitle locations; evaluate real task phrasing next.
3. Verify another host and improve the most common setup failures.

Keep the scope short. No cloud accounts, multi-user collaboration, agent marketplace or automatic research pipeline in this cycle. Add semantic retrieval only if concrete evaluation shows a useful improvement.

Validate external inputs at domain boundaries. Share behavior across adapters. Avoid catch-all fallbacks, speculative abstractions and tests that only mirror implementation. Update pages and real validation results together; keep GitHub Releases focused on the current usable preview.
