# Release Checklist v0.1.0

This checklist records the release-line verification state. It does not establish general production readiness beyond the checks listed here. Post-v0.1.0 `master` work is recorded separately and does not retroactively change the immutable `v0.1.0` tag.

## MCP Server Core

- [x] Server initialization and bootstrap path are implemented.
- [x] JSON-RPC initialization is recorded as verified for the 0.1.0 release line.
- [x] SDK tool errors are returned with `isError=True`.
- [x] STDIO protocol output is protected from ordinary stderr logging.

## Tool Registry and Baseline Operations

- [x] `list_tools()` is recorded as returning registered tools.
- [x] Workspace, Git, and Python built-in tools are registered.
- [x] All 15 Workspace/Git/Python operations have TOOL-0001 service/registry/representative SDK-session verification.
- [x] `python.version`, `git.status`, and `workspace.read_file` are recorded as verified representative operations.

## Quality Checks

- [x] Historical DOC-0004 baseline: pytest 54 passed; Ruff 0; mypy 0; `git diff --check` passed.
- [x] Post-MCP-0003 baseline: pytest 59 passed; Ruff 0; mypy 0; `git diff --check` passed.
- [x] TOOL-0001 baseline: pytest 89 passed; Ruff 0; mypy 0; `git diff --check` passed.
- [x] REL-0001 baseline: pytest 90 passed; Ruff 0; mypy 0; `git diff --check` passed.
- [x] CI-0001 GitHub Actions baseline: Linux/Python 3.11, pytest 90 passed when CI was introduced; Ruff and mypy passed.
- [x] SAFE-0001 Linux baseline: pytest 99 passed, Ruff 0 findings, mypy 0 findings in 69 source files.
- [x] SAFE-0001 Windows-local baseline: pytest 98 passed, 1 skipped; Ruff 0; mypy 0 in 69 source files.
- [x] The SAFE-0001 Windows skip is limited to the symlink-escape fixture because the process lacked symlink-creation privilege (`WinError 1314`).
- [x] AUTO-0001 Linux CI baseline: pytest 112 passed, Ruff 0 findings, mypy 0 findings in 71 source files.
- [x] AUTO-0002 Linux CI baseline: pytest 142 passed, Ruff 0 findings, mypy 0 findings in 77 source files.
- [x] SAFE-0002 Linux CI baseline: pytest **155 passed**, Ruff 0 findings, mypy 0 findings in 79 source files.
- [x] SAFE-0002 final Windows-local baseline: pytest **153 passed, 2 skipped**, Ruff 0, mypy 0 in 79 source files; `git diff --check` passed; working tree clean.
- [x] The two final Windows skips are limited to SAFE-0001 Workspace and SAFE-0002 Python symlink fixtures because the process lacked symlink-creation privilege (`WinError 1314`); equivalent coverage executes in Linux CI.

## Local Distribution Verification

- [x] Wheel build passed (`ai_engineering-0.1.0-py3-none-any.whl`).
- [x] Sdist build passed (`ai_engineering-0.1.0.tar.gz`).
- [x] Wheel content passed the runtime-only policy.
- [x] Sdist content passed the approved source policy.
- [x] Isolated wheel install passed in a fresh external virtual environment.
- [x] Installed package import and path-isolation checks passed.
- [x] Installed version and distribution metadata checks passed.
- [x] Installed `ai-engineering` console-script help and project-create smoke checks passed.
- [x] Post-v0.1.0 AUTO-0001 verification confirms installed `project --help` exposes `bootstrap`.
- [x] Post-v0.1.0 AUTO-0001 verification confirms installed `ai-engineering project bootstrap` creates the `python-engineering` scaffold outside the source checkout, reports the approved success contract, creates Git `main`, and has an initial commit.
- [x] Post-v0.1.0 AUTO-0002 verification confirms installed `project --help` exposes `docs` and `project docs --help` exposes `check`, `plan`, and `apply`.
- [x] Installed AUTO-0002 `check` reports manual review for an unmarked bootstrap project without mutating it.
- [x] Installed AUTO-0002 `plan` produces deterministic bounded updates for a marked isolated fixture.
- [x] Installed AUTO-0002 `apply` updates only the three approved documents, reports `verification=passed`, leaves Git HEAD/staging unchanged, and is followed by a clean installed `check`.
- [x] Current verification may use package-index access for isolated build dependency resolution; offline support is not claimed.

## Publication Verification

- [x] Git tag `v0.1.0` was created for approved commit `73929bd15fa7637db8162aac199697582bb25e67`.
- [x] GitHub Release `AI-Engineering 0.1.0` was published for `v0.1.0`.
- [x] AUTO-0001, AUTO-0002, and SAFE-0002 were implemented after `v0.1.0` and are not claimed as part of that immutable published tag/artifact.
- [ ] PyPI publishing remains not approved and not performed.

## CI Verification

- [x] GitHub Actions quality workflow exists and is triggered for PRs targeting `master` and pushes to `master`.
- [x] The quality job uses Linux/Python 3.11 and locked dev dependency synchronization.
- [x] Ruff, mypy, and full pytest execute without `continue-on-error`.
- [x] REL-0001 distribution verification remains part of the full pytest suite.
- [x] CI-0001 has successful PR and post-merge `master` evidence.
- [x] AUTO-0002 implementation PR #46 and post-merge Quality run #59 both passed the full quality workflow.
- [x] SAFE-0002 Python link-escape PR #51 passed Quality run #70; post-merge Quality run #71 passed the full suite with 155 tests.
- [x] The Windows-discovered AUTO-0002 newline assertion portability repair PR #52 passed Quality run #72; post-merge Quality run #73 passed.

## Workspace Path Safety Verification

- [x] Active MCP Workspace handlers use a service bound to `MCPConfig.workspace_root`.
- [x] Relative in-root and representative absolute in-root paths are verified.
- [x] Relative traversal and absolute outside-root paths are rejected.
- [x] Sibling-prefix containment is verified without string-prefix authorization.
- [x] Prospective create/write destinations cannot escape the root.
- [x] `workspace.move` independently authorizes source and destination.
- [x] Workspace-root move and delete are rejected.
- [x] Boundary violations use controlled `WorkspacePermissionError` behavior.
- [x] Linux CI executes link-escape coverage successfully.
- [x] Windows-local verification passed with the privilege-dependent symlink fixture explicitly skipped.
- [x] SAFE-0001 is recorded as a Workspace path-authorization boundary, not an OS-level sandbox.

## Git/Python Execution Safety Verification

- [x] Active MCP Git handlers use a bounded service rooted at `MCPConfig.workspace_root`.
- [x] MCP Git operations succeed when the configured root is the exact Git repository top level.
- [x] A configured root inside a parent Git repository is rejected rather than allowing discovery above the authority root.
- [x] Git command scope remains limited to the existing read-only tool families plus repository-top-level verification.
- [x] Active MCP Python path-taking operations are rooted at `MCPConfig.workspace_root`.
- [x] Relative and absolute in-root syntax/package targets succeed.
- [x] Traversal and absolute outside-root syntax/package/test targets are rejected with controlled Python permission errors.
- [x] Python link-escape coverage executes on Linux and records only privilege-dependent fixture skips on Windows.
- [x] `python.run_tests` rejects unauthorized targets before subprocess launch.
- [x] Authorized pytest execution uses `sys.executable -m pytest`, workspace-root cwd, `shell=False`, `stdin=DEVNULL`, captured output, and a bounded timeout.
- [x] Representative MCP SDK-session Git/Python success and controlled boundary errors are verified.
- [x] SAFE-0002 is recorded as an active-MCP authority-root/subprocess boundary, not an OS sandbox or containment of malicious code already authorized to run in-root.

## Engineering Bootstrap Verification

- [x] AUTO-0001 V1 accepts exactly the `python-engineering` profile.
- [x] Bootstrap core delegates project generation to the existing SDK public API and verifies the result read-only.
- [x] Fail-closed verification covers required files, target containment, Git root, `main`, initial commit, package, and smoke-test presence.
- [x] `ai-engineering project bootstrap` is additive; existing `project create` behavior remains verified.
- [x] Expected bootstrap failures use controlled stderr/exit-1 behavior; usage errors and unexpected failures retain their defined exit behavior.
- [x] Installed-wheel bootstrap smoke succeeds outside the source checkout without editable-install or `PYTHONPATH` reliance.

## Documentation Synchronization Verification

- [x] AUTO-0002 V1 inspection is deterministic, local, and read-only.
- [x] Drift detection and synchronization planning are deterministic and write nothing.
- [x] V1 writable scope is exactly `CURRENT_STATUS.md`, `MASTER_INDEX.md`, and `PROJECT_MAP.md`.
- [x] Missing/malformed ownership markers are manual-review conditions, not destructive normalization.
- [x] Plans contain SHA-256 original-content guards; stale plans fail closed before writes.
- [x] Guarded apply preserves human-owned prefix/suffix content and verifies exact written replacement content.
- [x] Source document line endings are preserved; tests are portable across LF and CRLF.
- [x] Post-apply reinspection proves resolved drift is cleared.
- [x] AUTO-0002 performs no Git stage/commit/push behavior.
- [x] Installed `project docs check/plan/apply` behavior is verified from an isolated wheel outside the source checkout.

## Documentation

- [x] MCP diagnostics documentation exists.
- [x] MCP SDK migration report is synchronized with implemented code and bounded client-verification claims.
- [x] Root README records the published v0.1.0 boundary.
- [x] SDK-0001.2 `ai-engineering project create` CLI is recorded as implemented and verified.
- [x] MCP-0003 Antigravity interoperability evidence is recorded.
- [x] TOOL-0001 verification and the Git porcelain parsing repair are recorded.
- [x] REL-0001 local distribution evidence is recorded.
- [x] CI-0001 automated quality-gate evidence is recorded.
- [x] SAFE-0001 Linux and Windows verification evidence is recorded.
- [x] REL-0002 v0.1.0 GitHub publication evidence is recorded.
- [x] AUTO-0001 API, CLI, and isolated installed-wheel verification evidence is recorded.
- [x] AUTO-0002 inspection, drift, guarded apply, CLI, isolated installed-wheel, and CI evidence is recorded.
- [x] SAFE-0002 Linux/Windows Git/Python boundary and subprocess evidence is recorded.

## Follow-up Verification

- [x] VS Code 1.132.1 built-in MCP interoperability is recorded as verified for MCP-0002.
- [x] Antigravity interoperability is recorded as verified for its MCP-0003 stdio contract.
- [ ] Record client-specific evidence before claiming ChatGPT/OpenAI, Claude Desktop, or other-client interoperability.
- [ ] Define a separate version/release decision before publishing any future release containing post-v0.1.0 work.
