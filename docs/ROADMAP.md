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
automated contracts, VS Code 1.132.1 manual interoperability, and the separately recorded
Antigravity contract are verified. This does not replace the internal Runtime, Registry, or
Discovery subsystems.

### SDK-0001 Project Templates V1, SDK-0001.1 Python Scaffold, and SDK-0001.2 CLI

**Status:** COMPLETE / VERIFIED

The document-first standalone project template, its optional generic Python scaffold, and its CLI
frontend are implemented and verified. SDK-0001.1 adds portable packaging metadata, a Python
package, a smoke test, and a generic `.gitignore` while preserving V1 output by default. SDK-0001.2
adds the installed `ai-engineering project create` command over the public API, with approved
stdout/stderr and exit-code behavior.

### AUTO-0001 Engineering Project Bootstrap

**Status:** COMPLETE / VERIFIED

AUTO-0001 adds the bounded `python-engineering` bootstrap workflow over SDK-0001. The typed core API
delegates creation to the existing template API, performs fail-closed read-only verification, and
is exposed through the additive installed `ai-engineering project bootstrap` command. Isolated-wheel
verification proves the installed command outside the source checkout. AUTO-0001 was completed
after the immutable `v0.1.0` tag and is not part of that published artifact.

## Current Priority

Preserve the verified MCP, SDK-0001, SAFE-0001, CI-0001, release, and AUTO-0001 contracts while
scoping the next engineering automation milestone. The next recommended milestone is AUTO-0002,
Project Documentation Synchronization, beginning with a documentation-first design contract rather
than implementation.

## Planned

### AUTO-0002 — Project Documentation Synchronization

**Status:** PLANNED / DESIGN REQUIRED

Define a bounded mechanism for inspecting an engineering project's current state, detecting drift in
approved project documentation, and producing deterministic synchronization changes. The design
must preserve originals and prohibit uncontrolled or destructive rewriting. Implementation, CLI
surface, writable document set, and verification behavior require explicit contract approval before
source changes begin.

### Client and IDE Interoperability

Validate interoperability with additional MCP clients and IDE integration surfaces. VS Code 1.132.1
and Antigravity are already verified for their recorded contracts; ChatGPT/OpenAI, Claude Desktop,
and other clients remain unverified.

### Future Engineering Capabilities

Additional bootstrap profiles, broader project update/synchronization behavior, Git/Python execution
safety boundaries, publication expansion, and other automation are planned only after their design,
implementation, and test scope are approved. Existing Workspace, Git, Python, bootstrap, Runtime,
Registry, and Discovery subsystems are implemented and are not returned to a future-placeholder
state.
