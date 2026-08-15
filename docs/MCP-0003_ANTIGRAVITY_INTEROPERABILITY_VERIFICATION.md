# MCP-0003 — Antigravity Interoperability Verification

**Status:** PLANNED / MANUAL VERIFICATION REQUIRED
**Scope:** client-specific verification of the existing AI-Engineering MCP server

## Objective

MCP-0003 defines a reproducible manual-evidence contract for verifying that Antigravity can use
the current AI-Engineering MCP server through its supported stdio boundary. The first target is
Antigravity only. This milestone captures evidence; it does not redesign the server, its transport,
or its tool registry.

Antigravity is **not verified** until this procedure has been performed and its evidence recorded.
Successful verification applies only to the tested Antigravity version/build and configuration. It
does not establish compatibility with ChatGPT/OpenAI, Claude Desktop, or other MCP clients.

## Preconditions

Before performing this procedure, record and confirm:

- an AI-Engineering checkout at the revision being tested;
- a workspace-local virtual environment with the repository dependencies installed;
- the Antigravity version/build and the MCP configuration mechanism used;
- the workspace directory and the exact working directory supplied to the server; and
- that diagnostics are initially disabled (`AI_ENGINEERING_DEBUG_MCP` unset or not equal to `1`).

The existing repository quality gates do not themselves establish Antigravity interoperability.
They are supporting evidence for the server revision under test.

## Server Configuration Contract

Configure one conceptual MCP server with these values, using the equivalent fields offered by the
Antigravity version under test:

| Setting | Required value |
|---|---|
| Server name | `AI-Engineering` |
| Transport | `stdio` |
| Command | `<python-executable>` |
| Arguments | `-m ai_engineering.stdio` |
| Working directory | `<workspace>` |
| Environment | `PYTHONPATH=<workspace>/src` |
| Preferred interpreter | `<workspace>/.venv` Python |
| Diagnostics for initial attempt | disabled; omit `AI_ENGINEERING_DEBUG_MCP` or set no value of `1` |

`<workspace>` and `<python-executable>` are local placeholders, not repository configuration
values. A machine-specific path may appear in the captured local evidence, but must not be added as
a portable repository configuration example. Do not rely on a global Python installation, OneDrive
location, fixed drive letter, or fixed user-profile path.

## Verification Boundary

The manual verification must establish, to the extent Antigravity exposes the relevant state:

1. Antigravity starts or connects to the AI-Engineering server.
2. MCP initialization/handshake succeeds.
3. Tool discovery succeeds.
4. A safe read-only tool call succeeds.
5. A controlled expected-error call returns without breaking the protocol.
6. The server remains connected/running after both calls.
7. No protocol corruption appears in client-visible MCP output or logs.
8. Stdout remains protocol-safe; no ordinary server output pollutes it.
9. Stderr and logging remain separate from protocol traffic.
10. Diagnostics behavior is captured if diagnostics are enabled in a separately documented retry.

Antigravity UI need not expose raw protocol internals for this contract. Record the visible
connection, tool, result, error, and log evidence that the UI does provide.

## Manual Procedure

Do not perform this procedure as part of MCP-0003-01. A future, explicitly authorized manual
verification performs these steps:

1. Open the AI-Engineering workspace.
2. Register or configure the `AI-Engineering` MCP server in Antigravity using the server
   configuration contract.
3. Start or restart the server.
4. Confirm Antigravity shows a connected/running state and initialization succeeded.
5. Confirm discovered tools are visible.
6. Invoke `python_version` with no input.
7. Invoke `workspace_read_file` with:

   ```json
   {"path":"MCP-0003-antigravity-does-not-exist.txt"}
   ```

8. Confirm the server remains connected/running and a subsequent tool interaction remains
   available.
9. Inspect Antigravity MCP output/logs for startup, discovery, calls, errors, and protocol issues.
10. Record the evidence and final result as VERIFIED, PARTIALLY VERIFIED, or FAILED.

## Safe Successful Call

The required successful call is the MCP tool `python_version` with no arguments. It is the
preferred evidence tool because the registered handler reads and returns the current interpreter
executable and version only. It has no file, workspace, Git, or process-mutating behavior, and is
deterministic enough to confirm an end-to-end result while allowing the exact Python version to be
recorded as environment evidence.

## Controlled Expected-Error Call

The required controlled-error call is the MCP tool `workspace_read_file` with the missing relative
path `MCP-0003-antigravity-does-not-exist.txt`. The tool is read-only and the path is deliberately
absent; do not create it. Capture the client-visible MCP error or error result and confirm that it
does not cause a crash, traceback, stdout corruption, or connection loss. Use the client-visible
MCP tool name; do not substitute an unknown-tool call unless Antigravity exposes only raw name
invocation and the limitation is recorded.

## Evidence Requirements

For each attempt, capture textual evidence where possible (screenshots may supplement it):

- date/time and the AI-Engineering revision tested;
- Antigravity version/build and MCP configuration mechanism;
- exact local server configuration, including command, arguments, working directory, and supplied
  environment variables;
- Python executable and `python_version` result/version;
- startup/connect and initialization evidence;
- tool-discovery evidence, including the visible tool count/list if available;
- successful call name, input, and returned output;
- controlled-error call name, input, and returned error/result;
- connection state after both calls;
- relevant Antigravity MCP output/logs, including stdout/protocol and stderr/logging observations;
- diagnostics state and, if used, its observed output location/behavior;
- explicit protocol-corruption observation; and
- final outcome: VERIFIED, PARTIALLY VERIFIED, or FAILED.

## Diagnostics Policy

The initial verification runs with diagnostics off. If a failure is ambiguous, a separately recorded
retry may set `AI_ENGINEERING_DEBUG_MCP=1`. That retry must retain the same server configuration
except for the recorded debug setting and must capture the resulting diagnostics behavior.

Diagnostics are opt-in supporting evidence only. They must not alter or pollute stdout protocol
traffic. The active SDK stdio bootstrap does not invoke the historical `wrap_stdio()` helpers;
client MCP output and any enabled runtime diagnostics are the relevant observations.

## Failure Classification

Classify a failed or incomplete attempt before considering code changes. Capture the listed evidence
for the first applicable category; use **G** when the available evidence cannot establish a cause.

| Class | Meaning | Evidence required before code changes are considered |
|---|---|---|
| A. CLIENT CONFIGURATION | Antigravity configuration, server registration, command, arguments, or working directory is incorrect or unsupported. | Exact client configuration, Antigravity version/build, visible validation/startup message, and comparison to this contract. |
| B. ENVIRONMENT | Interpreter, virtual environment, `PYTHONPATH`, dependencies, filesystem access, or process environment prevents startup. | Command/environment as launched, Python executable/version, working directory, dependency/startup error, and relevant client output. |
| C. MCP TRANSPORT | Stdio startup, handshake, framing, connection lifecycle, or stdout/stderr separation fails. | Startup/initialize transcript or visible state, client MCP output, stderr/log observations, and protocol-corruption observation. |
| D. TOOL REGISTRY / ADAPTER | Initialization succeeds but expected tools are absent, undiscoverable, wrongly named, or cannot be dispatched. | Discovered tool list/count, requested MCP tool name/input, returned result/error, and client/server output. |
| E. TOOL EXECUTION | A discovered tool call produces an unexpected success/error behavior while transport remains intact. | Tool name/input/output, expected behavior, connection state after the call, and relevant logs. |
| F. DIAGNOSTICS / LOGGING | Diagnostics or logging changes observable behavior, creates ambiguity, or appears to affect protocol separation. | Debug setting, diagnostics artifacts/output, stdout/stderr/client MCP observations with diagnostics off and, if retried, on. |
| G. UNKNOWN / NEEDS INVESTIGATION | Evidence does not isolate a category. | Complete evidence set, timestamps, client output/logs, and a concise statement of what remains unobservable or ambiguous. |

This task prescribes no fixes. Any code, transport, configuration, or adapter change requires a new
separately approved scope after the captured evidence is reviewed.

## Acceptance Criteria

Antigravity interoperability is **VERIFIED** only when all of the following are evidenced:

- connection initializes successfully;
- tools are discoverable;
- `python_version` succeeds;
- the controlled `workspace_read_file` missing-file call is handled without a crash or protocol
  breakage;
- the server remains usable after the calls; and
- no unexpected protocol errors appear.

If evidence for one or more criteria is missing but no contradictory failure is observed, the result
is **PARTIALLY VERIFIED**. If a required behavior fails, classify the failure and record the result
as **FAILED**. Never generalize the result to another MCP client.

## Non-Goals

MCP-0003 excludes Antigravity plugin development, a custom Antigravity adapter, MCP transport
changes, server refactoring, multi-client claims, ChatGPT/OpenAI verification, Claude verification,
VS Code re-verification, production-code changes, and automated GUI testing.

## Completion Criteria

MCP-0003-01 is complete when this contract is reviewed and indexed. MCP-0003 Antigravity
interoperability is complete only after a separately authorized manual execution captures the
required evidence and records a VERIFIED, PARTIALLY VERIFIED, or FAILED outcome without extending
the claim beyond Antigravity.
