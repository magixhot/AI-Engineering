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

- [x] pytest is recorded as passing for the 0.1.0 release line.
- [x] Ruff is recorded as passing for the 0.1.0 release line.
- [x] mypy is recorded as passing for the 0.1.0 release line.

## Documentation

- [x] MCP diagnostics documentation exists.
- [x] MCP SDK migration report has been synchronized with implemented code and remaining
  interoperability verification.
- [x] Root README records the 0.1.0 release line and current status.

## Follow-up Verification

- [ ] Record conclusive end-to-end MCP client interoperability evidence.
- [ ] Maintain the migration report as SDK behavior and verification evidence change.
