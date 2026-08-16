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
│       ├── cli.py        Installed project create/bootstrap/docs/health/reconciliation frontend
│       ├── engineering_bootstrap.py  AUTO-0001 typed bootstrap and verification API
│       ├── project_inspection.py     AUTO-0002 read-only project-state inspection
│       ├── documentation_sync.py    AUTO-0002 drift detection and deterministic planning
│       ├── documentation_apply.py   AUTO-0002 guarded apply and post-write verification
│       ├── documentation_ownership.py AUTO-0003 ownership classification and guarded initialization
│       ├── project_migration.py      AUTO-0004 migration identity, registry, and planning
│       ├── project_migration_apply.py AUTO-0004 guarded migration application/rollback
│       ├── python_engineering_baseline.py AUTO-0005 V2 engineering baseline
│       ├── project_git_readiness.py AUTO-0006 bounded Git readiness observations
│       ├── project_health.py         AUTO-0006 deterministic read-only health aggregation
│       ├── project_reconciliation.py AUTO-0007 deterministic read-only reconciliation planner
│       ├── project_reconciliation_cli.py AUTO-0007-04 public reconciliation CLI adapter
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
documentation synchronization/ownership, project migration, project health, and project reconciliation
are implemented repository subsystems. Their presence does not by itself make each subsystem part of
every MCP request.

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

## Reconciliation Path

AUTO-0007 is a separate read-only planning layer over the established project inspection,
documentation, migration, and Git contracts:

```text
project root
    → project inspection / identity
    → documentation ownership + synchronization state
    → migration readiness
    → bounded Git observations / invariants
    → `project_reconciliation.py`
    → deterministic reconciliation plan
    → `project_reconciliation_cli.py`
    → `ai-engineering project reconcile plan --project PATH`
```

The reconciliation planner has no apply/write authority. AUTO-0007-03 verifies fail-closed
manual-review/unsupported states, deterministic output, ordering, project-byte preservation, and
Git invariants. AUTO-0007-04 exposes the planner through the public CLI without changing those
boundaries.

## Implementation State

- Sprint 0 — Documentation Foundation: completed and continuously reconciled at milestone boundaries.
- Sprint 1 — MCP Foundation: implemented and verified by MCP-0002.
- SDK-0001 and AUTO-0001 project creation/bootstrap contracts: complete / verified.
- AUTO-0002 Project Documentation Synchronization: complete / verified, including installed-wheel
  `project docs check/plan/apply` behavior.
- AUTO-0003 Documentation Ownership Initialization: complete / verified.
- AUTO-0004 Project Update/Migration Framework: complete / verified.
- AUTO-0005 Python Engineering V2 / first production migration: complete / verified.
- AUTO-0006 Project Health/Readiness Audit: complete / verified.
- AUTO-0007-01 design, AUTO-0007-02 planner, and AUTO-0007-03 invariants: complete / verified.
- AUTO-0007-04 public reconciliation CLI: in progress in PR #85; Quality #150 is in progress.
- AUTO-0007-05 installed distribution verification and AUTO-0007-06 final documentation reconciliation:
  planned and gated on successful completion of the current stage.

`tests/release/` verifies wheel/sdist artifacts, isolated wheel installation, and installed CLI behavior
outside the source checkout.
