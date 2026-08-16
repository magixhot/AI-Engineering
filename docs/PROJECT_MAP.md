# AI-Engineering

## Repository Structure

```text
AI-Engineering/
├── docs/
├── src/
│   └── ai_engineering/
│       ├── discovery/
│       ├── git/
│       ├── ide/
│       ├── mcp/
│       ├── python/
│       ├── registry/
│       ├── runtime/
│       ├── shared/
│       ├── stdio/
│       ├── tools/
│       ├── workspace/
│       ├── cli.py
│       ├── public_cli.py
│       ├── engineering_bootstrap.py
│       ├── project_inspection.py
│       ├── documentation_sync.py
│       ├── documentation_apply.py
│       ├── documentation_ownership.py
│       ├── project_migration.py
│       ├── project_migration_apply.py
│       ├── project_git_readiness.py
│       ├── project_health.py
│       ├── project_reconciliation.py
│       ├── project_reconciliation_cli.py
│       ├── project_reconciliation_apply.py
│       ├── project_reconciliation_apply_cli.py
│       ├── project_reconciliation_orchestration.py
│       ├── project_reconciliation_orchestration_cli.py
│       └── server.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── release/
├── README.md
├── LICENSE
├── pyproject.toml
└── uv.lock
```

## Reconciliation Architecture

AUTO-0007 is the permanent read-only planner:

```text
project state → project_reconciliation.py → deterministic plan
```

AUTO-0008 is the sole guarded one-step apply boundary:

```text
fresh plan + exact eligible step
    → project_reconciliation_apply.py
    → one allow-listed subsystem write
    → fresh reinspection
```

AUTO-0009 composes those existing boundaries into bounded multi-step orchestration:

```text
fresh AUTO-0007 plan
    → select canonical next eligible step
    → exactly one AUTO-0008 apply
    → fresh AUTO-0007 plan
    → repeat until terminal state or bounded limit
```

Public orchestration adapter: `project_reconciliation_orchestration_cli.py`.
Installed public dispatcher: `public_cli.py`.

Verified command:

```text
ai-engineering project reconcile run --project PATH [--max-steps N]
```

AUTO-0009 owns no direct mutation primitive. It does not bypass AUTO-0008 stale-state validation and does not add arbitrary writes, new migration edges, parallel apply, force/stale bypass, publication, or direct Git mutation authority.

## Implementation State

- AUTO-0007 stages 01–06: COMPLETE / VERIFIED.
- AUTO-0008 stages 01–06: COMPLETE / VERIFIED.
- AUTO-0009-01 design: COMPLETE / VERIFIED; PR #99; Quality #189; post-merge #190.
- AUTO-0009-02 guarded orchestrator core: COMPLETE / VERIFIED; PR #100; corrected Quality #193; post-merge #194.
- AUTO-0009-03 safety/progress/failure invariants: COMPLETE / VERIFIED; PR #101; Quality #195; post-merge #196.
- AUTO-0009-04 public CLI: COMPLETE / VERIFIED; PR #102; corrected Quality #199; post-merge #200.
- AUTO-0009-05 installed distribution verification: COMPLETE / VERIFIED; PR #103; Quality #201; post-merge #202.
- AUTO-0009-06 final evidence/documentation reconciliation: COMPLETE / VERIFIED; PR #104; Quality #203; post-merge #204.

Final verified AUTO-0009 baseline: `87419229713c93e869d596ffcfabafb12aec4c00`.

`tests/release/` verifies wheel/sdist artifacts and installed CLI behavior outside the source checkout, including AUTO-0007 planning, AUTO-0008 guarded one-step apply, and AUTO-0009 bounded orchestration.
