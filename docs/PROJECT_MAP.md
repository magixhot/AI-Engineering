# AI-Engineering

## Repository Structure

```text
AI-Engineering/
├── .opencode/
│   └── agents/
│       └── auto-0013-readonly.md
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
│       ├── opencode_control_protocol.py
│       ├── opencode_readonly_adapter.py
│       ├── opencode_control_worker.py
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

AUTO-0007 is the permanent read-only planner. AUTO-0008 is the sole guarded one-step apply boundary. AUTO-0009 composes repeated fresh planning and one-step application into bounded orchestration. AUTO-0010 adds restriction-only policy evaluation. AUTO-0011 adds an optional explicit single-candidate approval gate. AUTO-0012 adds deterministic execution evidence without adding mutation authority.

AUTO-0013 is separate from the reconciliation write path. It adds only a bounded read-only remote inspection/control transport:

```text
GitHub control issue
    -> typed AUTO-0013 request
    -> local control worker
    -> localhost OpenCode
    -> dedicated read-only agent
    -> repository inspection
    -> typed AUTO-0013 result
```

The AUTO-0013 protocol lives in `opencode_control_protocol.py`. The localhost read-only adapter and repository snapshot invariants live in `opencode_readonly_adapter.py`. The dedicated GitHub polling/claim/result worker lives in `opencode_control_worker.py`. Project-local OpenCode permissions live in `.opencode/agents/auto-0013-readonly.md`.

## AUTO-0013 Safety Boundary

Allowed remote task classes are `status`, `inspect`, `plan`, and `diff`. The worker does not execute request text as shell code. The OpenCode agent denies edit authority, external-directory access, and arbitrary shell commands, with only a narrow read-only Git allowlist.

Adapter success requires before/after repository snapshot equality covering branch, HEAD, status, index state, worktree diff, cached diff, local Git configuration, and remotes.

AUTO-0013 does not authorize reconciliation apply/run mutation, commit/push/reset/checkout/clean/stash mutation, package publication, deployment, public OpenCode ingress, arbitrary remote shell execution, or any second repository write path.

## Implementation State

- AUTO-0007 stages 01–06: COMPLETE / VERIFIED.
- AUTO-0008 stages 01–06: COMPLETE / VERIFIED.
- AUTO-0009 stages 01–06: COMPLETE / VERIFIED.
- AUTO-0010 stages 01–06: COMPLETE / VERIFIED.
- AUTO-0011 stages 01–06: COMPLETE / VERIFIED.
- AUTO-0012 stages 01–06: COMPLETE / VERIFIED.
- AUTO-0013 stages 01–06: COMPLETE / VERIFIED.
- AUTO-0013-06 closure: PR #135; Quality #282 SUCCESS; merged master `0aaa95e8119e79fca3a2a100f6d629887c3fb5a6`; exact post-merge Quality #283 SUCCESS.

The verified successful live request id is `sha256:dcdfcd976fff8c7afd16352fdc63e2781c7067c6492c4e43733abd4bd6efeb2c`. Its terminal result recorded `SUCCEEDED`, exact expected/observed HEAD `2d03f9e37e373def6b0f705b6f2b5da751279427`, and `pre_clean=true` / `post_clean=true`.

No AUTO capability milestone is currently active.
