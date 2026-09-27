# v0.1.3 validation

Validated locally on Windows with Python 3.13.9:

- 32 automated tests pass: project isolation, Chinese/English retrieval, corrections, revision-bound evidence, archiving, original-file backups and restore, source parsing, the HTTP workflow, and a real MCP stdio client/server process.
- Browser checks from v0.1.0: import examples, retrieve a Chinese task, save a scoped correction and see it immediately, switch languages, save a new note, and inspect generated MCP configuration. These do not verify subsequent UI changes.
- Fresh Windows source installation through `setup.cmd` succeeds in a separate folder with a new virtual environment.
- The source distribution and wheel build successfully. Static UI, example data, and the standalone introduction are included.

The [CI template](ci-example.yml) covers Windows and Ubuntu with Python 3.11 and 3.13. It is not enabled: publishing GitHub workflows requires an additional workflow permission. To enable it, place the template at `.github/workflows/test.yml` after granting that permission. Remote jobs have not run. Specific coding-agent hosts are **not yet verified**. Protocol tests alone do not prove proactive tool use or product-specific configuration compatibility.

## Short manual acceptance

1. Install, run `aftermark serve`, import examples.
2. Recall `jump input buffering` under a project name of your choice.
3. Add a correction for that project and recall again. A different project must not receive the correction.
4. Connect a real MCP host using `aftermark config` and add the suggested instructions.
5. Ask the host to inspect a relevant source and the current code, then report an actual decision with evidence.

Use disposable test libraries with `--data-dir`; never treat generated sample usage as evidence of a real project improvement.

For v0.1.1, HTTP regression tests additionally cover atomic tagged imports, source-title defaults, tag validation and archived project filters. Browser automation was unavailable in this session because its execution environment failed to start; the changed form flow still needs a fresh browser check. macOS/Linux setup scripts have not been run on those operating systems.

v0.1.2 checks additionally cover correction-only matches in English/Chinese, both levels of project scope, archival exclusion, old-database migration without changing exported data, correction indexing after backup restore, stale usage evidence, combined result ranking, and read-only CLI/API MCP diagnostics. Windows installer verification was performed for v0.1.1; browser and specific host compatibility remain pending.

v0.1.3 checks cover real two-page PDF extraction and original bytes, page-specific reads, SRT/VTT timings, CRLF input, Unicode offsets, bounded pagination, missing anchors, stale revisions, project scope and archived sources. A real MCP subprocess reads a selected PDF page and rejects its stale revision after a correction. Browser execution could not start in this environment; the new location selector and copy-citation action still need a browser check. The schema remains 2.

The v0.1.3 wheel was installed in a separate virtual environment. Its CLI successfully read a scoped PDF page with a revision-bearing citation, and `doctor` passed through the installed package's real MCP subprocess.
