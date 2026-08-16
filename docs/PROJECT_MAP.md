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
│       ├── project_reconciliation_cli.py AUTO-0007 public reconciliation plan CLI adapter
│       ├── project_reconciliation_apply.py AUTO-0008 guarded one-step reconciliation executor
│       ├── project_reconciliation_apply_cli.py AUTO-0008 public guarded apply CLI adapter
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
documentation synchronization/ownership, project migration, project health, project reconciliation
planning, and guarded reconciliation execution are implemented repository subsystems. Their presence
does not by itself make each subsystem part of every MCP request.

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

## Reconciliation Paths

AUTO-0007 is the permanent read-only planning layer:

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

AUTO-0008 is a separate guarded execution boundary over that plan:

```text
reconciliation plan + exact step sequence
    → `project_reconciliation_apply.py`
    → pre-write reinspection / stale-plan and eligibility gate
    → one allow-listed existing subsystem apply primitive
    → post-apply reconciliation reinspection
    → bounded apply result
    → `project_reconciliation_apply_cli.py`
    → `ai-engineering project reconcile apply --project PATH --step SEQUENCE`
```

AUTO-0007 gains no apply/write authority. AUTO-0008 does not introduce arbitrary writes, arbitrary
commands, new migration edges, `apply all`, `force`, stale-plan bypasses, or publication behavior.
Its mutation authority is restricted to one exact eligible step delegated to the subsystem that
already owns the approved write primitive.

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
- AUTO-0007 stages 01–06: COMPLETE / VERIFIED; final/post-completion evidence closed through PR #91 / Quality #171 / post-merge #172.
- AUTO-0008-01 design/authority contract: COMPLETE / VERIFIED; PR #92; Quality #173; post-merge #174.
- AUTO-0008-02 guarded executor core: COMPLETE / VERIFIED; PR #93; corrected Quality #176; post-merge #177.
- AUTO-0008-03 safety/failure invariants: COMPLETE / VERIFIED; PR #94; Quality #178; post-merge #179.
- AUTO-0008-04 public guarded apply CLI: COMPLETE / VERIFIED; PR #95; corrected Quality #181; post-merge #182.
- AUTO-0008-05 installed distribution verification: COMPLETE / VERIFIED; PR #96; Quality #183; post-merge #184.
- AUTO-0008-06 final evidence/documentation reconciliation: IN PROGRESS, documentation-only.

`tests/release/` verifies wheel/sdist artifacts, isolated wheel installation, and installed CLI behavior
outside the source checkout, including AUTO-0007 read-only planning and AUTO-0008 guarded one-step
apply behavior.
