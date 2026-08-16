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
│       ├── project_reconciliation_policy.py
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

AUTO-0007 is the permanent read-only planner. AUTO-0008 is the sole guarded one-step apply boundary. AUTO-0009 composes repeated fresh planning and one-step application into bounded orchestration.

AUTO-0010 adds a restriction-only policy gate before each AUTO-0008 delegation:

```text
fresh AUTO-0007 plan
    → canonical candidate
    → optional explicit AUTO-0010 policy evaluation
    → if allowed: exactly one AUTO-0008 apply
    → fresh AUTO-0007 plan
    → repeat within effective bound
```

Public adapters are `project_reconciliation_orchestration_cli.py` and `public_cli.py`. Policy parsing/evaluation is implemented in `project_reconciliation_policy.py`.

Verified commands:

```text
ai-engineering project reconcile run --project PATH [--max-steps N]
ai-engineering project reconcile run --project PATH --policy POLICY.toml [--max-steps N]
```

AUTO-0010 policy can restrict known workflow identities, progress limits, and approved observable Git/root conditions. It cannot create write authority, bypass AUTO-0008 stale-state checks, execute arbitrary commands, discover remote policy, add migration edges, mutate Git directly, publish artifacts, or provide force/stale bypass.

## Implementation State

- AUTO-0007 stages 01–06: COMPLETE / VERIFIED.
- AUTO-0008 stages 01–06: COMPLETE / VERIFIED.
- AUTO-0009 stages 01–06: COMPLETE / VERIFIED.
- AUTO-0010-01 design: COMPLETE / VERIFIED; PR #106; Quality #207; post-merge #208.
- AUTO-0010-02 typed policy core: COMPLETE / VERIFIED; PR #107; corrected Quality #211; post-merge #212.
- AUTO-0010-03 safety/determinism/Git invariants: COMPLETE / VERIFIED; PR #108; corrected Quality #214; post-merge #215.
- AUTO-0010-04 orchestration/public CLI integration: COMPLETE / VERIFIED; PR #109; corrected Quality #220; post-merge #221.
- AUTO-0010-05 installed distribution verification: COMPLETE / VERIFIED; PR #110; Quality #222; post-merge #223.
- AUTO-0010-06 final evidence/documentation reconciliation: IN PROGRESS.

Verified implementation baseline entering AUTO-0010-06: `272b9328a819f9a4fc281f41aed9970cd05e208f`.

`tests/release/` verifies installed-wheel behavior outside the source checkout, including AUTO-0010 policy refusal, policy progress limits, malformed-policy fail-closed behavior, and Git safety evidence.
