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
│       ├── project_reconciliation_receipt.py
│       ├── project_reconciliation_receipt_projection.py
│       ├── project_reconciliation_receipt_cli.py
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

AUTO-0007 is the permanent read-only planner. AUTO-0008 is the sole guarded one-step apply boundary. AUTO-0009 composes repeated fresh planning and one-step application into bounded orchestration. AUTO-0010 adds restriction-only policy evaluation. AUTO-0011 adds an optional explicit single-candidate approval gate. AUTO-0012 adds deterministic execution evidence after/beside those existing decisions without adding mutation authority.

```text
fresh AUTO-0007 plan
    → canonical candidate
    → optional AUTO-0010 policy evaluation
    → optional AUTO-0011 approval verification
    → if all gates allow: exactly one AUTO-0008 apply
    → fresh AUTO-0007 plan
    → repeat within effective bound
    → AUTO-0012 projects observed run evidence into canonical receipt JSON
```

Approval model/canonicalization lives in `project_reconciliation_approval.py`. Fresh project/Git/policy binding is assembled in `project_reconciliation_approval_context.py`. Pure deterministic approval matching is implemented in `project_reconciliation_approval_verification.py`.

Receipt v1 model/canonicalization and strict parsing live in `project_reconciliation_receipt.py`. Pure projection from observed orchestration evidence plus bounded read-only context lives in `project_reconciliation_receipt_projection.py`. Explicit receipt-mode execution/output lives in `project_reconciliation_receipt_cli.py`; public routing remains in `public_cli.py`.

Verified commands include:

```text
ai-engineering project reconcile run --project PATH [--max-steps N]
ai-engineering project reconcile run --project PATH --policy POLICY.toml [--max-steps N]
ai-engineering project reconcile approve --project PATH [--policy POLICY.toml]
ai-engineering project reconcile run --project PATH --approval APPROVAL.json [--policy POLICY.toml] [--max-steps N]
ai-engineering project reconcile run --project PATH [--max-steps N] [--policy POLICY.toml] [--approval APPROVAL.json] --receipt-json
```

AUTO-0012 receipts are deterministic evidence only. They can describe policy decisions, approval verification outcomes, delegated apply attempts, terminal state, final plan and remaining work, but cannot authorize execution, override policy/approval, choose candidates, retry/resume, rollback, or mutate Git/project state.

## Implementation State

- AUTO-0007 stages 01–06: COMPLETE / VERIFIED.
- AUTO-0008 stages 01–06: COMPLETE / VERIFIED.
- AUTO-0009 stages 01–06: COMPLETE / VERIFIED.
- AUTO-0010 stages 01–06: COMPLETE / VERIFIED.
- AUTO-0011 stages 01–06: COMPLETE / VERIFIED.
- AUTO-0012-01 design/contract: COMPLETE / VERIFIED; PR #121; Quality #248; post-merge #249.
- AUTO-0012-02 typed receipt model/canonicalization: COMPLETE / VERIFIED; PR #122; corrected Quality #251; post-merge #252.
- AUTO-0012-03 evidence projection/safety invariants: COMPLETE / VERIFIED; PR #123; Quality #253; post-merge #254.
- AUTO-0012-04 public CLI integration: COMPLETE / VERIFIED; PR #124; corrected Quality #257; post-merge #258.
- AUTO-0012-05 installed distribution verification: COMPLETE / VERIFIED; PR #125; corrected Quality #260; post-merge #261.
- AUTO-0012-06 final evidence/documentation reconciliation: documentation closure only.

The verified implementation baseline `2268f4c8278f3c81b5735e26337984aebd300c6b` and exact post-merge Quality #261 are historical evidence. Later repository progress does not invalidate them.

`tests/release/` verifies installed-wheel behavior outside the source checkout, including AUTO-0012 canonical receipt/digest behavior, real delegated execution evidence, deterministic no-change evidence, policy refusal, stale approval refusal, malformed approval terminal evidence, and zero-write Git invariants for refusal/error cases.
