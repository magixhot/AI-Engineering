# AI-Engineering

<!-- canonical-project-state
{"schema_version":2,"completed_through":"AUTO-0020","active_milestone":"AUTO-0021"}
-->

## Repository Structure

```text
AI-Engineering/
├── .github/workflows/quality.yml
├── .opencode/agents/auto-0013-readonly.md
├── docs/
│   ├── CANONICAL_PROJECT_STATE.json
│   ├── AI_CHAT_START.md
│   ├── PROJECT_CONTEXT.md
│   ├── PROJECT_MAP.md
│   ├── CURRENT_STATUS.md
│   ├── ROADMAP.md
│   └── MASTER_INDEX.md
├── src/ai_engineering/
│   ├── discovery/
│   ├── git/
│   ├── ide/
│   ├── mcp/
│   ├── python/
│   ├── registry/
│   ├── runtime/
│   ├── shared/
│   ├── stdio/
│   ├── tools/
│   ├── workspace/
│   ├── project_reconciliation*.py
│   ├── opencode_control_protocol.py
│   ├── opencode_control_worker.py
│   ├── opencode_service_config.py
│   ├── opencode_worker_lifecycle.py
│   ├── opencode_user_service.py
│   ├── quality_verification.py
│   ├── quality_verifier.py
│   ├── quality_actions_transport.py
│   ├── quality_gate_relay.py
│   ├── workstation_doctor_model.py
│   ├── workstation_doctor_runtime.py
│   ├── project_state_manifest.py
│   └── project_state_coherence.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── release/
├── README.md
├── LICENSE
├── pyproject.toml
└── uv.lock
```

## Layered Automation Boundaries

AUTO-0007 is the permanent read-only reconciliation planner. AUTO-0008 is the
sole guarded one-step apply boundary. AUTO-0009 composes fresh planning and
one-step application into bounded orchestration. AUTO-0010 can only restrict
that authority. AUTO-0011 adds an optional explicit approval fence. AUTO-0012
adds receipts without new mutation authority.

AUTO-0013 through AUTO-0019 form a separate bounded control plane:

```text
GitHub control issue
  -> user-scoped worker service
  -> read-only control worker
  -> localhost OpenCode when required
  -> typed result/evidence
```

Remote task classes are `status`, `inspect`, `plan`, `diff`, and
`quality_verify`. AUTO-0018 adds typed failure handling, bounded read retry,
observability, and stale-workspace diagnosis without repair. AUTO-0019 recovery
may publish a separate terminal envelope for an aged unresolved claim only
after immediate reinspection; it never invokes executor/OpenCode/
`quality_verify` and never replays the request.

## Canonical Project-State Gate

`project_state_manifest.py` loads the strict typed manifest from
`docs/CANONICAL_PROJECT_STATE.json`. `project_state_coherence.py` validates
exactly the six declared document projections and emits bounded deterministic
diagnostics. It does not parse historical/free-form prose.

Quality runs the validator offline with Python bytecode disabled before Ruff,
mypy, and pytest:

```text
manifest + six document markers
  -> strict parser
  -> deterministic read-only validator
  -> coherent=true or non-zero failure
```

The gate does not edit documentation, repair Git state, call GitHub, control
services, or expand reconciliation/OpenCode authority.

## Implementation State

- AUTO-0001 through AUTO-0019: COMPLETE / VERIFIED.
- AUTO-0020-01 design/contract: COMPLETE / VERIFIED.
- AUTO-0020-02 typed manifest/parser: COMPLETE / VERIFIED.
- AUTO-0020-03 deterministic validator: COMPLETE / VERIFIED.
- AUTO-0020-04 Quality integration/failure coverage: COMPLETE / VERIFIED.
- AUTO-0020-05 canonical document reconciliation/repository-wide evidence:
  COMPLETE / VERIFIED.
- AUTO-0020-06 final reconciliation/next-milestone audit:
  COMPLETE / VERIFIED.
- AUTO-0021-01 repository landing-state coherence design:
  COMPLETE / VERIFIED.
- AUTO-0021-02 document-set v2 / README marker: COMPLETE / VERIFIED.
- AUTO-0021-03 README narrative reconciliation: ACTIVE.
- AUTO-0021-04 final audit: PENDING.

AUTO-0019 closed at exact `master`
`c287e5cceef4e72148de7674f4095fedb78bd302` through Quality #394.
AUTO-0020-06 audit merged at exact `master`
`143ccdcbd9b39e89188cbad63577b0dc1e353941` through Quality #405/#406.

Schema v2 adds the narrow `QUIESCENT` terminal representation while retaining
schema v1 active-manifest compatibility. That terminal state remains the
verified AUTO-0020 baseline.

AUTO-0021 now has an explicit design identity. Its approved target is the
repository-root `README.md`. Document-set v2 governs it first in deterministic
order; no glob or generic Markdown policy is added.
