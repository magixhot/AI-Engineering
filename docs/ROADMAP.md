# AI-Engineering Roadmap

## Completed

### Sprint 0 — Documentation Foundation

**Status:** COMPLETED

The core project documentation foundation has been established.

## Implemented / Verified

### Sprint 1 — MCP Foundation

**Status:** IMPLEMENTED / VERIFIED

Implemented repository components include MCP bootstrap, the official SDK adapter, Composite
Registry, Runtime, Discovery, STDIO, diagnostics, and registered Workspace/Git/Python tool
subsystems. Runtime and Discovery remain repository subsystems, not steps in the active SDK request
path.

### Official Python MCP SDK Migration

**Status:** COMPLETE

The official Python MCP SDK is integrated as the protocol/server boundary. The active path is
`python -m ai_engineering.stdio` through bootstrap, `EngineeringMCPServer`,
`CompositeRegistry`/`SDKAdapter`, and the official `mcp.server.stdio.stdio_server`. MCP-0002
automated contracts and VS Code 1.132.1 manual interoperability are verified. This does not
replace the internal Runtime, Registry, or Discovery subsystems.

### SDK-0001 Project Templates V1, SDK-0001.1 Python Scaffold, and SDK-0001.2 CLI

**Status:** COMPLETE / VERIFIED

The document-first standalone project template, its optional generic Python scaffold, and its CLI
frontend are implemented and verified. SDK-0001.1 adds portable packaging metadata, a Python
package, a smoke test, and a generic `.gitignore` while preserving V1 output by default. SDK-0001.2
adds the installed `ai-engineering project create` command over the public API, with approved
stdout/stderr and exit-code behavior.

## Current Priority

Maintain the verified MCP-0002 implementation and the SDK-0001 V1/SDK-0001.1 project-template
baseline. Record additional client interoperability only when supported by separately captured
evidence; it is not a blocker for completed MCP-0002.

## Planned

### Engineering Automation

Project bootstrap, documentation generation, and future engineering automation require separate
scope and validation. The SDK-0001.1 scaffold is complete; no broader automation is implied.

### Client and IDE Interoperability

Validate interoperability with additional MCP clients and IDE integration surfaces, including
Antigravity. VS Code 1.132.1 is already verified for the MCP-0002 scope.

### Future Engineering Capabilities

Additional tools and automation are planned only after their design, implementation, and test scope
are approved. Existing Workspace, Git, and Python subsystems are implemented and are not returned
to a future-placeholder state.
