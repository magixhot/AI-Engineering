# Stabilization Plan for the 0.1.0 Release Line

**Status:** Historical plan reconciled with the repository on 2026-08-13.

This document preserves the original stabilization intent after migration to the official Python
MCP SDK. It records only repository-supported facts and distinguishes completed work from
verification that remains necessary. The active verification contract is
`docs/MCP-0002_SDK_BOUNDARY_VERIFICATION.md`.

## Active MCP Execution Path

```text
python -m ai_engineering.stdio
  -> ai_engineering.stdio.__main__
  -> ai_engineering.mcp.bootstrap.main()
  -> anyio.run(bootstrap.run)
  -> EngineeringMCPServer / CompositeRegistry / SDKAdapter
  -> mcp.server.stdio.stdio_server
  -> official SDK server handlers
```

`SDKAdapter.list_tools` reads `CompositeRegistry.descriptors()`. `SDKAdapter.call_tool` maps the
MCP name to the internal name and dispatches through `CompositeRegistry.call()`.

`MCPRuntime`, `DiscoveryRegistry`, and the diagnostic `wrap_stdio()` helper are present in the
repository but are not part of this active execution path.

## Completed or Obsolete Items

### SDKAdapter error semantics — COMPLETED

`SDKAdapter.call_tool` catches execution exceptions and returns `CallToolResult` with
`isError=True`. The historical action to change successful error `TextContent` responses is
therefore obsolete. MCP-0002 automated contract coverage verifies this behavior.

### Removed legacy entry point — OBSOLETE

The historical plan referred to `src/ai_engineering/main.py`. That file is not present in the
current repository; the active entry point is `python -m ai_engineering.stdio`.

### `streams.py` removal — NOT IN SCOPE

`src/ai_engineering/mcp/debug/streams.py` still exists and exports `wrap_stdio()`, but the active
bootstrap uses the official `stdio_server` directly and does not call it. This task does not
remove the module solely as cleanup; any future decision requires separate scope and tests.

## MCP-0002 Evidence Recorded

### SDK boundary contract tests — COMPLETED

MCP-0002 verifies SDK tool listing, name mapping, schema generation, successful and failed calls,
unknown tools, invalid arguments, and `CallToolResult(isError=True)` semantics. The matrix and
tests are recorded in `docs/MCP-0002_SDK_BOUNDARY_VERIFICATION.md`.

### STDIO and JSON-RPC verification — COMPLETED

MCP-0002 automated tests verify clean module startup, JSON-RPC initialization, and separation of
protocol stdout from non-protocol logging.

### Diagnostics verification — COMPLETED

MCP-0002 verifies opt-in diagnostics through `AI_ENGINEERING_DEBUG_MCP`: disabled mode creates no
logger or log directory, while enabled mode lazily records runtime events in `logs/mcp-runtime.log`
without writing to protocol stdout or stderr.

### VS Code interoperability — COMPLETED

VS Code 1.132.1 built-in MCP support is manually verified with the workspace stdio configuration,
tool discovery, a successful safe call, and a controlled error; the server remained Running and
MCP Output showed no protocol corruption. Antigravity, ChatGPT/OpenAI, Claude Desktop, and other
clients remain unverified and are not claimed.

## Deferred Improvements

- Review result serialization in `sdk_adapter.py`, including behavior for non-text MCP content.
- Review duplicate diagnostic and standard logging only after contract behavior is covered.
- Consider broader diagnostics architecture only as separately approved work; the current
  `FileHandler`-based runtime logging is intentionally retained for stabilization.

## Architectural Boundaries Retained

- `CompositeRegistry` and `ToolNameMapper` remain the active registry and naming boundary.
- The official Python MCP SDK remains the protocol/server boundary.
- `MCPRuntime`, Registry, Discovery, IDE adapters, and diagnostics are not redesigned by this
  plan.
