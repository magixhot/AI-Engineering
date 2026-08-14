# AI-Engineering

## Repository Structure

```text
AI-Engineering/
├── docs/                 Project, MCP, release, and SDK-0001 documentation
├── src/
│   └── ai_engineering/
│       ├── discovery/    Built-in tool metadata and discovery registry
│       ├── git/          Git service, models, exceptions, and tools
│       ├── ide/          IDE models, protocol, sessions, projects, and adapters/
│       │   └── adapters/ Antigravity and VS Code adapters
│       ├── mcp/          Official SDK integration, bootstrap, configuration, and debug/
│       │   └── debug/    MCP diagnostics configuration, logging, and stream helpers
│       ├── python/       Python service, models, exceptions, and tools
│       ├── registry/     Composite registry, descriptors, and server integration
│       ├── runtime/      Runtime context, dispatcher, events, and lifecycle
│       ├── shared/       Shared package boundary
│       ├── stdio/        `python -m ai_engineering.stdio` entry point
│       ├── tools/        Shared tool package boundary
│       ├── workspace/    Workspace service, models, exceptions, and tools
│       ├── project_templates.py
│       └── server.py
├── tests/
│   ├── unit/
│   └── integration/
├── README.md
├── LICENSE
├── pyproject.toml
└── uv.lock
```

`transport/` is not a current source directory and is intentionally not represented above.

## Existing Repository Subsystems

Runtime, Registry, Discovery, diagnostics, and IDE adapters are implemented repository subsystems.
Their presence does not by itself make each subsystem part of every MCP request.

## Active MCP SDK Execution Path

```text
MCP client
    │ STDIO / official Python MCP SDK boundary
    ▼
`python -m ai_engineering.stdio`
    → `ai_engineering.mcp.bootstrap`
    → `EngineeringMCPServer`
    → `CompositeRegistry` + `SDKAdapter`
    → official `mcp.server.stdio.stdio_server`
    → official SDK handlers
```

The official SDK owns protocol/server handling. `MCPRuntime`, `DiscoveryRegistry`, and diagnostic
`wrap_stdio()` exist but are not invoked by this active path. MCP diagnostics are a separate
supporting subsystem; IDE adapters represent integration surfaces, not confirmed client
interoperability.

## Implementation State

- Sprint 0 — Documentation Foundation: completed.
- Sprint 1 — MCP Foundation: implemented and verified by MCP-0002.
- Workspace, Git, Python, Runtime, Registry, Discovery, STDIO, diagnostics, and IDE modules are
  implemented repository subsystems.
- SDK-0001 Project Templates V1 and the optional SDK-0001.1 Python scaffold are implemented
  through `project_templates.py`; a CLI is not present. Broader automation and additional validated
  client interoperability remain future work.
