# MCP-0002: SDK Boundary Verification

**Status:** ACTIVE / TEST PLAN
**Scope:** Official Python MCP SDK boundary stabilization.

## Purpose

MCP-0002 defines the verification contract for the official Python `mcp` SDK boundary. It turns
the implemented bootstrap, `SDKAdapter`, and `CompositeRegistry` behavior into explicit automated
and manual evidence without redesigning the existing architecture.

## A. Scope

MCP-0002 verifies the active execution path:

```text
python -m ai_engineering.stdio
  -> bootstrap.main() -> bootstrap.run()
  -> EngineeringMCPServer
  -> CompositeRegistry + SDKAdapter
  -> mcp.server.stdio.stdio_server
  -> official SDK list_tools and call_tool handlers
```

The contract covers SDKAdapter behavior, tool listing, MCP/internal name mapping, input-schema
generation, successful and failed calls, `CallToolResult(isError=True)` semantics,
`CompositeRegistry` dispatch, the STDIO entry point, JSON-RPC initialization, stdout/stderr
separation, diagnostics behavior, and separately recorded client interoperability evidence.

`MCPRuntime`, `DiscoveryRegistry`, and diagnostic `wrap_stdio()` are repository components but are
not asserted as participants in this active path.

## B. Automated Verification Matrix

| Area | Behavior | Evidence type | Automated test | Expected result | Status |
|---|---|---|---|---|---|
| Tool listing | SDK handler returns descriptors registered by `CompositeRegistry` | Unit | `test_mcp_sdk_adapter.py` list-tools contract | MCP tools match registered descriptors | IMPLEMENTED / VERIFIED |
| Name mapping | Internal dotted names map to MCP underscore names and back | Unit | `test_mcp_sdk_adapter.py` mapped call contract | `demo.echo` is exposed and invoked as `demo_echo` | IMPLEMENTED / VERIFIED |
| Input schemas | Descriptor annotations produce usable MCP input schemas | Unit | `test_mcp_sdk_adapter.py` schema contract | Required, optional, and primitive parameters are represented as expected | IMPLEMENTED / VERIFIED |
| Successful call | Registered handler result becomes MCP text content | Unit | `test_mcp_sdk_adapter.py` success-call contract | Result is returned as expected `TextContent` | IMPLEMENTED / VERIFIED |
| Failed call | Handler exception returns an SDK error result | Unit | `test_mcp_sdk_adapter.py` failure contract | `CallToolResult.isError` is `True` and content is readable | IMPLEMENTED / VERIFIED |
| Unknown tool | Unknown MCP name is handled through the error contract | Unit | `test_mcp_sdk_adapter.py` unknown-tool contract | `CallToolResult.isError` is `True`; no server crash | IMPLEMENTED / VERIFIED |
| Invalid arguments | Invalid handler arguments are handled through the error contract | Unit | `test_mcp_sdk_adapter.py` invalid-arguments contract | `CallToolResult.isError` is `True`; no server crash | IMPLEMENTED / VERIFIED |
| Registry dispatch | Adapter dispatches through the composite legacy execution registry | Unit | `test_mcp_sdk_adapter.py` dispatch contract | Registered handler receives mapped name and arguments | IMPLEMENTED / VERIFIED |
| STDIO entry point | `python -m ai_engineering.stdio` starts the official SDK bootstrap | Integration / subprocess | STDIO startup test | Process starts without non-protocol stdout output | IMPLEMENTED / TEST MISSING |
| JSON-RPC initialize | Server accepts MCP initialization over STDIO | Integration / subprocess | JSON-RPC handshake test | Valid initialization response is returned | MANUAL RECORD EXISTS / TEST MISSING |
| Protocol stdout | stdout carries only protocol messages during a session | Integration / subprocess | stdout separation test | No ordinary logs or diagnostics pollute stdout | IMPLEMENTED / TEST MISSING |
| stderr and logging | Non-protocol logging does not enter stdout | Integration / subprocess | stderr/logging capture test | stderr or configured logs contain non-protocol output; stdout remains protocol-only | TEST MISSING |
| Diagnostics disabled | Debug mode is opt-in | Unit | Diagnostics default test | `AI_ENGINEERING_DEBUG_MCP` unset yields no runtime logger and no log directory creation | IMPLEMENTED / TEST MISSING |
| Diagnostics enabled | Debug mode records runtime events explicitly | Unit / integration | Diagnostics enabled test | `AI_ENGINEERING_DEBUG_MCP=1` creates the configured runtime log during a tool call | IMPLEMENTED / TEST MISSING |

The 0.1.0 release checklist records prior manual verification of initialization, tool listing, and
stdout/stderr protection. Those records do not replace the automated evidence required by
MCP-0002.

## C. Manual Interoperability Matrix

Manual client checks are separate from automated SDK boundary tests. No client is verified until
the required evidence is captured and referenced from the SDK audit and migration report.

| Target | Evidence required before verification | Status |
|---|---|---|
| Antigravity | Client configuration, successful initialize/list-tools/call-tool transcript, client version, diagnostics or stderr capture, and observed error behavior | MANUAL VERIFICATION REQUIRED |
| VS Code MCP client | Client configuration, successful initialize/list-tools/call-tool transcript, client version, diagnostics or stderr capture, and observed error behavior | MANUAL VERIFICATION REQUIRED |
| Other MCP-compatible client | Identified client/version, reproducible configuration, successful initialize/list-tools/call-tool transcript, and observed error behavior | MANUAL VERIFICATION REQUIRED |

## D. Non-goals

MCP-0002 does not include:

- MCPRuntime redesign;
- Registry or CompositeRegistry redesign;
- IDE adapter redesign;
- SDK-0001 work or template expansion;
- transport redesign or a custom MCP protocol implementation;
- removal of historical modules solely for cleanup; or
- client interoperability execution without separately approved client access and evidence.

## E. Completion Criteria

MCP-0002 is complete only when:

1. the automated contract tests in the matrix exist and pass;
2. STDIO startup and JSON-RPC initialization are tested;
3. successful, failed, unknown-tool, and invalid-argument error semantics are covered;
4. diagnostics-off and diagnostics-on behavior are covered; and
5. manual client interoperability evidence is recorded separately for every client claimed as
   verified.

Passing repository tests do not by themselves establish compatibility with a specific MCP client.
