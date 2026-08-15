# Release Checklist v0.1.0 / v0.2.0

This checklist records release-line verification state. It does not establish general production readiness beyond the checks listed here. Historical `v0.1.0` remains immutable; `v0.2.0` is the current published GitHub release. PyPI remains separately gated.

## MCP Server Core

- [x] Server initialization and bootstrap path are implemented.
- [x] JSON-RPC initialization is recorded as verified.
- [x] SDK tool errors are returned with `isError=True`.
- [x] STDIO protocol output is protected from ordinary stderr logging.

## Tool Registry and Baseline Operations

- [x] `list_tools()` is recorded as returning registered tools.
- [x] Workspace, Git, and Python built-in tools are registered.
- [x] All 15 Workspace/Git/Python operations have TOOL-0001 service/registry/representative SDK-session verification.

## Quality Checks

- [x] REL-0001 baseline: pytest 90 passed; Ruff 0; mypy 0; `git diff --check` passed.
- [x] SAFE-0001 Linux baseline: pytest 99 passed; Windows-local: pytest 98 passed / 1 privilege-dependent symlink skip.
- [x] AUTO-0001 Linux CI baseline: pytest 112 passed, Ruff 0, mypy 0 in 71 source files.
- [x] AUTO-0002 Linux CI baseline: pytest 142 passed, Ruff 0, mypy 0 in 77 source files.
- [x] SAFE-0002 Linux CI baseline: pytest 155 passed, Ruff 0, mypy 0 in 79 source files.
- [x] SAFE-0002 Windows-local baseline: pytest 153 passed / 2 privilege-dependent symlink-fixture skips, Ruff 0, mypy 0 in 79 source files; `git diff --check` passed; working tree clean.
- [x] Exact 0.2.0 candidate passed GitHub Actions Quality #79.
- [x] 0.2.0 readiness documentation passed PR Quality #80 and post-merge Quality #81.

## Local Distribution Verification

- [x] Wheel/sdist content policy is verified.
- [x] Isolated wheel install passed in a fresh external virtual environment.
- [x] Installed package import, metadata, entry point, and source-tree isolation are verified.
- [x] Installed `ai-engineering project create` is verified.
- [x] Installed `ai-engineering project bootstrap` is verified.
- [x] Installed `ai-engineering project docs check/plan/apply` is verified.
- [x] Exact 0.2.0 candidate distribution test passed on Windows.
- [x] Verified 0.2.0 wheel: `ai_engineering-0.2.0-py3-none-any.whl`.
- [x] Verified 0.2.0 sdist: `ai_engineering-0.2.0.tar.gz`.
- [x] Current verification may use package-index access for isolated build dependency resolution; offline support is not claimed.

## Publication Verification

### v0.1.0

- [x] Git tag `v0.1.0` targets `73929bd15fa7637db8162aac199697582bb25e67`.
- [x] GitHub Release `AI-Engineering 0.1.0` was published.

### v0.2.0

- [x] Version `0.2.0` was explicitly approved before publication.
- [x] Exact artifact/tag candidate SHA was frozen as `1faf14c121b7b5da7c8781e3de4e836f85838a76`.
- [x] Tag `v0.2.0` was created and points exactly to the approved candidate SHA.
- [x] GitHub Release `AI-Engineering 0.2.0` was published.
- [x] Release is not draft and not prerelease.
- [x] Wheel asset uploaded: `ai_engineering-0.2.0-py3-none-any.whl`.
- [x] Wheel SHA-256: `5b86945e861cd22c6e67306e533bb7d446f6bc35207b209c96aa27b4928897bb`.
- [x] Sdist asset uploaded: `ai_engineering-0.2.0.tar.gz`.
- [x] Sdist SHA-256: `6594377eda9324aeec82f5db7c7874f68d8cca3dbbbe2ef7f97532a0f341a9b2`.
- [x] Release notes preserve bounded client-compatibility and security claims.
- [x] PyPI was not published.

## CI Verification

- [x] GitHub Actions quality workflow runs on PRs targeting `master` and pushes to `master`.
- [x] Linux/Python 3.11 uses locked dev dependency synchronization.
- [x] Ruff, mypy, and full pytest execute without `continue-on-error`.
- [x] Distribution verification remains part of the full pytest suite.
- [x] CI-0001 has successful PR and post-merge evidence.

## Workspace Path Safety Verification

- [x] Active MCP Workspace handlers use a service bound to `MCPConfig.workspace_root`.
- [x] Relative/in-root paths are allowed and traversal/outside/link escapes are rejected.
- [x] Workspace-root move/delete and move destination escapes are rejected.
- [x] Linux CI executes link-escape coverage; Windows privilege-dependent skip is classified.
- [x] SAFE-0001 is a path-authorization boundary, not an OS sandbox.

## Git/Python Execution Safety Verification

- [x] Active MCP Git handlers are bounded to `MCPConfig.workspace_root`.
- [x] Parent Git repository discovery above the configured authority root is rejected.
- [x] Python syntax/package/test targets must resolve inside the authority root.
- [x] Traversal, outside-root, and supported link escapes are rejected before execution.
- [x] Authorized pytest uses current interpreter, workspace-root cwd, `shell=False`, `stdin=DEVNULL`, captured output, and bounded timeout.
- [x] SAFE-0002 is an authority-root/subprocess boundary, not an OS sandbox.

## Engineering Bootstrap Verification

- [x] AUTO-0001 V1 accepts exactly the `python-engineering` profile.
- [x] Bootstrap delegates generation to SDK-0001 and performs fail-closed verification.
- [x] Installed-wheel bootstrap works outside the source checkout.

## Documentation Synchronization Verification

- [x] AUTO-0002 inspection, drift detection, and planning are deterministic and read-only.
- [x] Writable scope is exactly `CURRENT_STATUS.md`, `MASTER_INDEX.md`, and `PROJECT_MAP.md`.
- [x] Missing/malformed ownership markers require manual review.
- [x] SHA-256 guards, human-content preservation, LF/CRLF preservation, and post-apply verification are covered.
- [x] AUTO-0002 does not stage, commit, or push Git changes.
- [x] Installed-wheel `project docs check/plan/apply` behavior is verified.

## Documentation

- [x] MCP/SDK/client evidence is documented with bounded claims.
- [x] REL-0001 distribution evidence is recorded.
- [x] REL-0002 v0.1.0 publication evidence is recorded.
- [x] AUTO-0001, AUTO-0002, SAFE-0001, and SAFE-0002 evidence is recorded.
- [x] REL-0003 0.2.0 readiness evidence is recorded.
- [x] REL-0003 post-release publication evidence is recorded in `REL-0003_POST_RELEASE_RECONCILIATION.md`.

## Follow-up Verification

- [x] VS Code 1.132.1 built-in MCP interoperability is recorded as verified for MCP-0002.
- [x] Antigravity interoperability is recorded as verified for MCP-0003.
- [ ] Record client-specific evidence before claiming ChatGPT/OpenAI, Claude Desktop, or other-client interoperability.
- [ ] Any future release/version or PyPI publication requires a new explicit decision and readiness cycle.
