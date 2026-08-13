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
therefore obsolete. Automated contract coverage for this behavior is still required.

### Removed legacy entry point — OBSOLETE

The historical plan referred to `src/ai_engineering/main.py`. That file is not present in the
current repository; the active entry point is `python -m ai_engineering.stdio`.

### `streams.py` removal — NOT IN SCOPE

`src/ai_engineering/mcp/debug/streams.py` still exists and exports `wrap_stdio()`, but the active
bootstrap uses the official `stdio_server` directly and does not call it. This task does not
remove the module solely as cleanup; any future decision requires separate scope and tests.

## Still Required for Stabilization

### SDK boundary contract tests — PENDING

Add automated evidence for SDK tool listing, name mapping, schema generation, successful and
failed calls, unknown tools, invalid arguments, and `CallToolResult(isError=True)` semantics.
The required matrix is defined in `docs/MCP-0002_SDK_BOUNDARY_VERIFICATION.md`.

### STDIO and JSON-RPC verification — PENDING

The current bootstrap runs the official SDK through `mcp.server.stdio.stdio_server`. Add automated
evidence that the module entry point starts cleanly, accepts initialization, and keeps protocol
output separate from non-protocol logging.

### Diagnostics verification — PENDING

Runtime diagnostics are opt-in through `AI_ENGINEERING_DEBUG_MCP`. When enabled, the current
runtime logger writes tool-call information to `logs/mcp-runtime.log`; when disabled it returns no
runtime logger. Verify both modes without redesigning diagnostics or transport.

### Client interoperability — MANUAL VERIFICATION REQUIRED

No repository evidence conclusively verifies Antigravity, VS Code, ChatGPT/OpenAI, Claude
Desktop, or other MCP-compatible clients. Record client-specific evidence separately after the
automated SDK boundary contract is in place.

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
