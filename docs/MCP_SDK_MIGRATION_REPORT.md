# MCP SDK Migration Report

**Status:** COMPLETE / VS CODE AND ANTIGRAVITY VERIFIED
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

## Client Interoperability Evidence

VS Code 1.132.1 built-in MCP support was manually verified on 2026-08-13 using the workspace
stdio server configuration. The server started, reached Running, discovered 15 tools, returned the
safe `python_version` result, and handled a missing-path `workspace_read_file` call as a controlled
failure without a traceback or server crash. `AI_ENGINEERING_DEBUG_MCP` was not set, and VS Code MCP
Output showed no protocol corruption or unexpected AI-Engineering MCP server error.

Antigravity is separately verified for the recorded MCP-0003 stdio contract. Its initial manual
verification exposed a server-side snake_case reverse-dispatch defect; PR #18 (`c08bb16`) repaired
the mapper, and the post-fix Antigravity re-test succeeded. This is client-specific evidence and
does not alter the original VS Code migration evidence.

MCP-0002 is complete because its criteria require evidence for every client claimed as verified,
not all client categories. VS Code and Antigravity are verified for their recorded contracts.
ChatGPT/OpenAI, Claude Desktop, and other-client interoperability remain unverified and are not
claimed.

## Known Operational Notes

- Tool failures are represented as readable SDK error results rather than unhandled server crashes.
- Diagnostics can add synchronous logging overhead when enabled and are intended for active
  investigation.
- This report documents repository evidence; it does not claim broad production readiness.
