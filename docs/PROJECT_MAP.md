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
│       ├── cli.py        Installed project create/bootstrap/docs frontend
│       ├── engineering_bootstrap.py  AUTO-0001 typed bootstrap and verification API
│       ├── project_inspection.py     AUTO-0002 read-only project-state inspection
│       ├── documentation_sync.py     AUTO-0002 drift detection and deterministic planning
│       ├── documentation_apply.py    AUTO-0002 guarded apply and post-write verification
│       ├── project_templates.py      SDK-0001 standalone template/scaffold API
│       └── server.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── release/          Distribution/artifact and installed-CLI verification
├── README.md
├── LICENSE
├── pyproject.toml
└── uv.lock
```

`transport/` is not a current source directory and is intentionally not represented above.

## Existing Repository Subsystems

Runtime, Registry, Discovery, diagnostics, IDE adapters, SDK project templates, engineering bootstrap,
and bounded documentation synchronization are implemented repository subsystems. Their presence does
not by itself make each subsystem part of every MCP request.

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
`engineering_bootstrap.py` owns AUTO-0001's additive `python-engineering` orchestration and read-only
fail-closed verification while delegating creation to SDK-0001.

## Documentation Synchronization Path

AUTO-0002 is intentionally separate from project generation:

```text
project root
    → `project_inspection.py`
    → `documentation_sync.py` drift report
    → deterministic sync plan + original SHA-256 digests
    → `documentation_apply.py` guarded apply
    → post-apply reinspection and drift verification
```

The installed `cli.py` adapter exposes `ai-engineering project docs check`, `plan`, and `apply` over
those public boundaries. `check` and `plan` are read-only. V1 writes only machine-owned marked
sections of `CURRENT_STATUS.md`, `MASTER_INDEX.md`, and `PROJECT_MAP.md`; missing/malformed markers
require manual review.

## Implementation State

- Sprint 0 — Documentation Foundation: completed.
- Sprint 1 — MCP Foundation: implemented and verified by MCP-0002.
- SDK-0001 and AUTO-0001 project creation/bootstrap contracts: complete / verified.
- AUTO-0002 Project Documentation Synchronization: complete / verified, including installed-wheel
  `project docs check/plan/apply` behavior.
- `tests/release/` verifies wheel/sdist artifacts, isolated wheel installation, and installed
  create/bootstrap/documentation CLI behavior outside the source checkout.
- AUTO-0002 does not initialize ownership markers, stage/commit Git changes, execute project code,
  install project dependencies, or contact remote services.
