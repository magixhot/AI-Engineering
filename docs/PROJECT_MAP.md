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
│       ├── opencode_service_config.py
│       ├── opencode_worker_lifecycle.py
│       ├── opencode_user_service.py
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

AUTO-0013 is separate from the reconciliation write path and adds only bounded read-only remote inspection/control transport.

AUTO-0014 adds local lifecycle supervision around the existing AUTO-0013 worker:

```text
GitHub control issue
    -> installed user-scoped worker service
    -> AUTO-0013 control worker
    -> localhost OpenCode
    -> dedicated read-only agent
    -> repository inspection
    -> typed AUTO-0013 result
```

The strict runtime configuration lives in `opencode_service_config.py`. Single-instance worker lifecycle and polling entrypoint live in `opencode_worker_lifecycle.py`. User-scoped service rendering lives in `opencode_user_service.py`. AUTO-0013 protocol, adapter, worker, and project-local OpenCode permissions remain unchanged authority boundaries.

## AUTO-0014 Safety Boundary

The installed service may supervise only the existing read-only worker. It does not add task classes, repository write authority, remote service-control commands, request replay, public OpenCode ingress, or inbound workstation listeners.

The user-service integration remains explicit and per-user, with hardened service settings including `ProtectSystem=strict`, `ProtectHome=read-only`, `NoNewPrivileges=yes`, and a validated per-user runtime directory.

The worker remains restricted to `status`, `inspect`, `plan`, and `diff`. Adapter success still requires before/after repository snapshot equality.

## Implementation State

- AUTO-0007 stages 01–06: COMPLETE / VERIFIED.
- AUTO-0008 stages 01–06: COMPLETE / VERIFIED.
- AUTO-0009 stages 01–06: COMPLETE / VERIFIED.
- AUTO-0010 stages 01–06: COMPLETE / VERIFIED.
- AUTO-0011 stages 01–06: COMPLETE / VERIFIED.
- AUTO-0012 stages 01–06: COMPLETE / VERIFIED.
- AUTO-0013 stages 01–06: COMPLETE / VERIFIED.
- AUTO-0014 stages 01–05: COMPLETE / VERIFIED.
- AUTO-0014-06 final evidence/documentation reconciliation: ACTIVE.

AUTO-0014-05 evidence merged via PR #143 as exact master `58e0b3c6cd5393386ad97871aa34f6fd9e4fef47` after Quality #302 SUCCESS and then passed exact post-merge Quality.

The verified successful installed-service request id is `sha256:593eff3b7e76a65ec2399ea3988ae0895ea01c2bc608bb690bc62be46fe9baf7`. Its terminal result recorded `SUCCEEDED`, exact expected/observed HEAD `5b5b3b0ec1922685a594679ddebc199f28b6b8d5`, and `pre_clean=true` / `post_clean=true`.

After AUTO-0014 closure, the approved next design direction is a read-only exact post-merge Quality verifier.
