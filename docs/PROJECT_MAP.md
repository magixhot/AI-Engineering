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
│       ├── project_reconciliation_approval.py
│       ├── project_reconciliation_approval_context.py
│       ├── project_reconciliation_approval_verification.py
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

AUTO-0007 is the permanent read-only planner. AUTO-0008 is the sole guarded one-step apply boundary. AUTO-0009 composes repeated fresh planning and one-step application into bounded orchestration. AUTO-0010 adds restriction-only policy evaluation. AUTO-0011 adds an optional explicit single-candidate approval gate without adding mutation authority.

```text
fresh AUTO-0007 plan
    → canonical candidate
    → optional AUTO-0010 policy evaluation
    → optional AUTO-0011 approval verification
    → if all gates allow: exactly one AUTO-0008 apply
    → fresh AUTO-0007 plan
    → repeat within effective bound
```

Approval model/canonicalization lives in `project_reconciliation_approval.py`. Fresh project/Git/policy binding is assembled in `project_reconciliation_approval_context.py`. Pure deterministic matching is implemented in `project_reconciliation_approval_verification.py`. Public routing remains in `public_cli.py`, while orchestration continues to delegate mutation only through the existing apply boundary.

Verified commands:

```text
ai-engineering project reconcile run --project PATH [--max-steps N]
ai-engineering project reconcile run --project PATH --policy POLICY.toml [--max-steps N]
ai-engineering project reconcile approve --project PATH [--policy POLICY.toml]
ai-engineering project reconcile run --project PATH --approval APPROVAL.json [--policy POLICY.toml] [--max-steps N]
```

Approval is deterministic and scoped to one candidate. It binds authority-relevant candidate inputs, portable project identity, Git HEAD/branch state, and explicit policy context. Malformed/stale/mismatched approval fails closed before that candidate write. Because orchestration replans after a successful write, the same approval cannot authorize the next candidate.

AUTO-0011 cannot create write authority, bypass AUTO-0008 stale-state checks, override AUTO-0010 refusal, execute arbitrary commands, add workflows, mutate Git directly, approve a whole run, publish artifacts, or provide force/stale bypass.

## Implementation State

- AUTO-0007 stages 01–06: COMPLETE / VERIFIED.
- AUTO-0008 stages 01–06: COMPLETE / VERIFIED.
- AUTO-0009 stages 01–06: COMPLETE / VERIFIED.
- AUTO-0010 stages 01–06: COMPLETE / VERIFIED.
- AUTO-0011-01 design: COMPLETE / VERIFIED; PR #113; Quality #228; post-merge #229.
- AUTO-0011-02 typed approval model/canonicalization: COMPLETE / VERIFIED; PR #114; corrected Quality #232; post-merge #233.
- AUTO-0011-03 verification/safety invariants: COMPLETE / VERIFIED; PR #115; corrected Quality #235; post-merge #236.
- AUTO-0011-04 guarded integration: COMPLETE / VERIFIED; PR #116; corrected Quality #238; post-merge #239.
- AUTO-0011-05 installed distribution verification: COMPLETE / VERIFIED; PR #117; Quality #240; post-merge #241.
- AUTO-0011-06 final evidence/documentation reconciliation: IN PROGRESS.

Verified implementation baseline entering closure: `2d181d38d26087bb672eaaa0691b27f071353eb7`.

`tests/release/` verifies installed-wheel behavior outside the source checkout, including AUTO-0011 deterministic approval generation, one-bound-candidate execution, stale approval refusal, malformed approval fail-closed behavior, and preservation of the existing Git safety boundary.
