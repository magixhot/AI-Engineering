# AI-Engineering

## Repository Structure

```text
AI-Engineering/
├── docs/                 Project, MCP, release, SDK, safety, CI, and automation documentation
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
│       ├── cli.py        Installed `ai-engineering project create/bootstrap` frontend
│       ├── engineering_bootstrap.py  AUTO-0001 typed bootstrap and verification API
│       ├── project_templates.py      SDK-0001 standalone template/scaffold API
│       └── server.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── release/          Bounded distribution/artifact and installed-CLI verification
├── README.md
├── LICENSE
├── pyproject.toml
└── uv.lock
```

`transport/` is not a current source directory and is intentionally not represented above.

## Existing Repository Subsystems

Runtime, Registry, Discovery, diagnostics, IDE adapters, SDK project templates, and engineering
bootstrap are implemented repository subsystems. Their presence does not by itself make each
subsystem part of every MCP request.

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

## Project Creation and Bootstrap Paths

`project_templates.py` owns the SDK-0001 standalone project creation/scaffold contract.
`engineering_bootstrap.py` owns AUTO-0001's additive `python-engineering` orchestration and
read-only fail-closed verification while delegating creation to SDK-0001. `cli.py` exposes both
installed frontends: `ai-engineering project create` and `ai-engineering project bootstrap`.

## Implementation State

- Sprint 0 — Documentation Foundation: completed.
- Sprint 1 — MCP Foundation: implemented and verified by MCP-0002.
- Workspace, Git, Python, Runtime, Registry, Discovery, STDIO, diagnostics, and IDE modules are
  implemented repository subsystems.
- SDK-0001 Project Templates V1, SDK-0001.1 Python scaffold, and SDK-0001.2 installed create CLI are
  complete / verified.
- AUTO-0001 Engineering Project Bootstrap core API, installed CLI adapter, fail-closed verification,
  and isolated-wheel bootstrap smoke are complete / verified.
- `tests/release/` contains bounded local distribution verification for wheel/sdist artifacts and
  isolated wheel installation, including installed create/bootstrap CLI behavior; it is not the
  ordinary unit-test layer.
- AUTO-0002 Project Documentation Synchronization is planned and requires a separate design
  contract before implementation.
