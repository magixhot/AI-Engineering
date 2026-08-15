# Release Checklist v0.1.0

This checklist records the release-line verification state. It does not establish general
production readiness beyond the checks listed here.

## MCP Server Core

- [x] Server initialization and bootstrap path are implemented.
- [x] JSON-RPC initialization is recorded as verified for the 0.1.0 release line.
- [x] SDK tool errors are returned with `isError=True`.
- [x] STDIO protocol output is protected from ordinary stderr logging.

## Tool Registry and Baseline Operations

- [x] `list_tools()` is recorded as returning registered tools.
- [x] Workspace, Git, and Python built-in tools are registered.
- [x] `python.version` is recorded as verified.
- [x] `git.status` is recorded as verified.
- [x] `workspace.read_file` is recorded as verified.

## Quality Checks

- [x] Historical 0.1.0 release evidence recorded pytest, Ruff, and mypy as passing.
- [x] Current DOC-0004 verification: pytest passed (54 tests).
- [x] Current DOC-0004 verification: Ruff passed (0 findings).
- [x] Current DOC-0004 verification: mypy passed (0 findings).
- [x] Current DOC-0004 verification: `git diff --check` passed.
- [x] Current post-MCP-0003 verification: pytest passed (59 tests).
- [x] Current post-MCP-0003 verification: Ruff passed (0 findings).
- [x] Current post-MCP-0003 verification: mypy passed (0 findings).
- [x] Current post-MCP-0003 verification: `git diff --check` passed.
- [x] Current TOOL-0001 verification: pytest passed (89 tests).
- [x] Current TOOL-0001 verification: Ruff passed (0 findings).
- [x] Current TOOL-0001 verification: mypy passed (0 findings).
- [x] Current TOOL-0001 verification: `git diff --check` passed.

## Documentation

- [x] MCP diagnostics documentation exists.
- [x] MCP SDK migration report has been synchronized with implemented code and remaining
  interoperability verification.
- [x] Root README records the 0.1.0 release line and current status.
- [x] SDK-0001.2 `ai-engineering project create` CLI is recorded as implemented and verified.
- [x] MCP-0003 Antigravity interoperability evidence is recorded in
  `MCP-0003_ANTIGRAVITY_INTEROPERABILITY_VERIFICATION.md`.
- [x] TOOL-0001 isolated verification covers all 15 existing Workspace, Git, and Python tool
  operations without changing their public behavior. The Git porcelain parsing repair is separately
  recorded in merged PR #22.

## Follow-up Verification

- [x] VS Code 1.132.1 built-in MCP interoperability is recorded as verified for MCP-0002.
- [x] Antigravity interoperability is recorded as verified for its MCP-0003 stdio contract.
- [ ] Record client-specific evidence before claiming ChatGPT/OpenAI, Claude Desktop, or
  other-client interoperability.
- [ ] Maintain the migration report as SDK behavior and verification evidence change.
