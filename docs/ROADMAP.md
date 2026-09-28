# Short roadmap

The current local preview contains the complete save → retrieve → read → record → correct workflow, shared by the UI, CLI and MCP. Project-specific onboarding and current-release downloads are now part of that foundation.

Next, in order:

1. Use a real saved method on a real code change. Compare the decision and evidence with the source, not just whether tools were called.
2. Fix observed retrieval misses and capture friction; keep a small English/Chinese regression set.
3. Verify another host and improve the most common setup failures.

Keep the scope short. No cloud accounts, multi-user collaboration, agent marketplace or automatic research pipeline in this cycle. Add semantic retrieval only if concrete evaluation shows a useful improvement.

Validate external inputs at domain boundaries. Share behavior across adapters. Avoid catch-all fallbacks, speculative abstractions and tests that only mirror implementation. Update pages and real validation results together; keep GitHub Releases focused on the current usable preview.
