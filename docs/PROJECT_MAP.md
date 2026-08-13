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

## Architecture Boundaries

```text
MCP client
    │ STDIO / official Python MCP SDK boundary
    ▼
MCP bootstrap → SDKAdapter → Composite Registry → Runtime and tool subsystems
                                      ├── Workspace
                                      ├── Git
                                      ├── Python
                                      └── Discovery metadata
```

The official SDK owns protocol/server handling. The internal Runtime and Registry remain the
AI-Engineering execution and registration architecture. MCP diagnostics are a separate supporting
subsystem; IDE adapters represent integration surfaces, not confirmed client interoperability.

## Implementation State

- Sprint 0 — Documentation Foundation: completed.
- Sprint 1 — MCP Foundation: implemented; in SDK migration and stabilization.
- Workspace, Git, Python, Runtime, Registry, Discovery, STDIO, diagnostics, and IDE modules are
  implemented repository subsystems.
- Engineering automation and additional validated client interoperability are future work.
