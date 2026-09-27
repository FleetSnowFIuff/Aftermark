# Keeping code, pages and GitHub together

For each small release:

1. Implement one bounded improvement and update behavior tests.
2. Update the version, bilingual README, `CHANGELOG.md`, and the actual tested scope in `VALIDATION.md`.
3. Edit the standalone source `website/Aftermark-介绍页.html`, then run `python scripts/sync_site.py`. The app page is a synchronized copy.
4. Run `python scripts/sync_site.py --check`, relevant tests, and `python -m build`. New install paths must be checked from a clean folder.
5. Push code, tag the matching commit, and attach the wheel and source archive to the GitHub release. Source ZIP links must refer to an existing tag before publishing the page.
6. Update the hosted introduction from the same standalone file using the site's publishing workflow. Preserve its existing visibility. The local knowledge database is not part of that site.

Do not describe roadmap work as available. Keep host compatibility and automation claims tied to checks actually performed. A failed check must stay visible in the validation notes.
