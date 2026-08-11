# MCP SDK Migration Report

## 1. Goal
The primary objective of this migration was to replace the custom-built, legacy MCP transport and server implementation in the AI-Engineering project with the official `mcp` Python SDK (version `1.27.x`).
This ensures full compliance with the Model Context Protocol, better stability, long-term maintainability, and seamless integration with official MCP clients (such as the ChatGPT desktop app).

## 2. What was Replaced
- The legacy custom JSON-RPC parsing and transport mechanisms were entirely removed.
- The `std_server.py` implementation was replaced.
- The tool registration and execution lifecycle were bridged to the official SDK using a custom adapter.

## 3. Modules Deleted
* *(Note: Actual file deletions were performed in earlier stages of this branch, primarily legacy transport and protocol parsing modules that duplicated the official SDK's functionality).*

## 4. Modules Added
- `src/ai_engineering/mcp/bootstrap.py`: Replaces the legacy entry point. Integrates `anyio` and the official SDK's `stdio_server`, safely isolating `sys.stdout` to prevent JSON-RPC corruption.
- `src/ai_engineering/mcp/sdk_adapter.py`: A thin adapter layer (`SDKAdapter`) bridging the internal `CompositeRegistry` with the official SDK's `@server.call_tool()` and `@server.list_tools()` decorators.
- `src/ai_engineering/mcp/debug/`: A completely new, non-invasive **MCP Diagnostics** subsystem.
  - `config.py`: Environment variable `AI_ENGINEERING_DEBUG_MCP` handling.
  - `logger.py`: Runtime metrics and traceback logging (`mcp-runtime.log`).
  - `streams.py`: Raw byte-level wire interception for `stdin`/`stdout` (`mcp-wire.log`).
- `docs/MCP_DIAGNOSTICS.md`: Documentation for the new telemetry subsystem.

## 5. Testing Results
* **SDK Initialization**: `python -m ai_engineering.stdio` starts flawlessly without exceptions.
* **Initialize Phase**: Returns valid `{"jsonrpc": "2.0", "result": {...}}` handshakes.
* **ChatGPT Client Integration**:
  - *Pending final verification from logs.*
  - We are currently verifying whether the `invalid character '='` error originates from the AI-Engineering server or the ChatGPT Agent integration, utilizing the new MCP Diagnostics module.

## 6. Known Limitations
- **JSON-RPC Exceptions**: Any exceptions raised during tool execution are caught by `SDKAdapter` and returned as a standard `TextContent` block containing the error message, rather than a JSON-RPC error. This ensures the client receives readable text instead of a hard crash.
- **Diagnostics Overhead**: Wire logging involves synchronous file appends. It is strictly disabled by default and should only be enabled via `AI_ENGINEERING_DEBUG_MCP=1` during active debugging.
