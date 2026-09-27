# v0.1.1 validation

Validated locally on Windows with Python 3.13.9:

- 19 automated tests pass: project isolation, Chinese/English retrieval, corrections, revision-bound evidence, archiving, original-file backups and restore, source parsing, the HTTP workflow, and a real MCP stdio client/server process.
- Browser checks: import examples, retrieve a Chinese task, save a scoped correction and see it immediately, switch languages, save a new note, and inspect generated MCP configuration.
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
