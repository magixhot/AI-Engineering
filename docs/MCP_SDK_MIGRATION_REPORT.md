# MCP SDK Migration Report

**Status:** ACTIVE / STABILIZATION
**Evidence snapshot:** 2026-08-13

## Goal

Migrate the MCP protocol/server boundary to the official Python `mcp` SDK while preserving the
AI-Engineering Runtime and Registry architecture.

## Implemented Integration

- `pyproject.toml` declares `mcp>=1.27,<1.28`.
- `src/ai_engineering/mcp/bootstrap.py` creates the SDK server and runs it through the official
  `stdio_server` transport.
- `src/ai_engineering/mcp/sdk_adapter.py` bridges `CompositeRegistry` to the SDK's
  `list_tools` and `call_tool` handlers.
- Tool execution exceptions are returned as an SDK `CallToolResult` with `isError=True`.
- `src/ai_engineering/stdio/` provides the `python -m ai_engineering.stdio` entry point.
- `src/ai_engineering/mcp/debug/` provides diagnostics configuration, runtime logging, and stream
  helpers; diagnostics are disabled unless explicitly enabled.

## Preserved Internal Architecture

The migration does not replace `runtime/`, `registry/`, `discovery/`, `workspace/`, `git/`, or
`python/`. `SDKAdapter` is the boundary adapter between the official SDK and the existing
`CompositeRegistry`-based execution model.

## Verified Repository Evidence

The 0.1.0 release checklist records successful MCP initialization, JSON-RPC initialization,
stdout/stderr separation, tool listing, and baseline `python.version`, `git.status`, and
`workspace.read_file` operations. The current repository contains unit tests and configured
pytest, Ruff, and mypy tooling.

## Pending Verification

The repository does not provide conclusive evidence that ChatGPT, Antigravity, VS Code, Claude
Desktop, or other clients have completed interoperability validation. These remain pending until
tested sessions and diagnostic evidence are recorded.

## Known Operational Notes

- Tool failures are represented as readable SDK error results rather than unhandled server crashes.
- Diagnostics can add synchronous logging overhead when enabled and are intended for active
  investigation.
- This report documents repository evidence; it does not claim broad production readiness.
