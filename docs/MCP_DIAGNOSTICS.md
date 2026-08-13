# MCP Diagnostics

The MCP Diagnostics subsystem is a core part of the AI-Engineering infrastructure (M2 Framework). It provides non-invasive, multi-tiered telemetry for the Model Context Protocol (MCP) server, allowing engineers to trace JSON-RPC payloads at the wire level and monitor tool execution at the runtime level.

## Architecture

The diagnostics system is intentionally separated into two distinct layers to avoid buffering issues and to cleanly separate transport logic from business logic.

### 1. Wire Logging Helper (`mcp-wire.log`)
The wire logger is existing diagnostic infrastructure designed to capture raw client/server data when
its stream wrappers are explicitly used.
- **Bypasses `logging` module**: It uses a raw `open().write(..., "a")` append strategy. This guarantees that Python's logging formatters, encodings, or buffering mechanisms do not alter or hide malformed JSON or illegal characters.
- **Stream Wrappers**: `LoggingReadStream`, `LoggingWriteStream`, and `wrap_stdio()` remain
  available helpers. They are not invoked by the current bootstrap, which uses the official SDK
  `stdio_server` directly; MCP-0002 does not treat `mcp-wire.log` as active-path evidence.
- **Format**: Each line includes a timestamp and a directional arrow (`->` for outgoing to client, `<-` for incoming from client) followed by the exact raw payload.

### 2. Runtime Logging (`mcp-runtime.log`)
The runtime logger captures business-level tool execution telemetry using the standard Python `logging` framework (`ai_engineering.mcp.diagnostics.runtime`).
- **Tool Metrics**: Captures the requested tool name, parsed JSON arguments, execution time (in milliseconds), and the byte size of the serialized result.
- **Exception Tracing**: If a tool crashes, the full Python `traceback` is dumped to the runtime log, alongside the execution time leading up to the crash.
- **Return Types**: Validates and logs the Python `type` and `class` of the object returned by the tool handler before it is converted to an MCP `TextContent` block.

## Debug Mode Configuration

Diagnostics are disabled by default for performance and security reasons. To enable the module, you must set the following environment variable:

### Environment Variables

| Variable | Description |
|---|---|
| `AI_ENGINEERING_DEBUG_MCP` | Set to `"1"` to enable the diagnostics subsystem. If missing or `0`, diagnostics are disabled and the server operates with zero overhead. |

**Example (ChatGPT `mcp_config.json`):**
```json
{
  "mcpServers": {
    "ai-engineering": {
      "command": "python",
      "args": ["-m", "ai_engineering.stdio"],
      "env": {
        "AI_ENGINEERING_DEBUG_MCP": "1"
      }
    }
  }
}
```

## Log Format Examples

### `logs/mcp-wire.log` (only if a future explicitly scoped integration invokes the wrappers)
```text
10:43:12.123 <- {"jsonrpc":"2.0","id":0,"method":"initialize", ...}
10:43:12.128 -> {"jsonrpc":"2.0","id":0,"result":{...}}
10:43:15.001 <- {"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"python.version"}}
10:43:15.006 -> {"jsonrpc":"2.0","id":1,"result":{"content":[{"type":"text","text":"Python 3.11.9"}]}}
```

### `logs/mcp-runtime.log`
```text
2026-08-06 10:43:15,001 | INFO | Tool call: python.version
2026-08-06 10:43:15,001 | DEBUG | Arguments: {}
2026-08-06 10:43:15,006 | INFO | Tool result: python.version (5.2 ms)
2026-08-06 10:43:15,006 | DEBUG | Returned type: dict
Returned class: dict
Serialized length: 124 bytes
```

## Troubleshooting

- **Malformed JSON-RPC or client hangs**:
  The active SDK stdio path does not create `mcp-wire.log`. Use MCP client output and
  `mcp-runtime.log` when diagnostics are enabled; introduce wire-wrapper use only through a
  separately approved and tested integration.
- **Logs Not Appearing**:
  Ensure all zombie `python.exe` processes are killed before testing, and confirm `AI_ENGINEERING_DEBUG_MCP=1` is correctly passed in the parent process's environment variables.
