# AI-Engineering

<!-- canonical-project-state
{"schema_version":1,"completed_through":"AUTO-0019","active_milestone":"AUTO-0020","active_stage":"AUTO-0020-05","active_state":"IMPLEMENTATION_ACTIVE"}
-->

## Chat Bootstrap

For a new or continued session, restore context in this order:

1. `README.md`
2. `PROJECT_CONTEXT.md`
3. `PROJECT_MAP.md`
4. `CURRENT_STATUS.md`
5. `ROADMAP.md`
6. `DECISIONS.md`
7. `CODING_STANDARDS.md`
8. `MASTER_INDEX.md`
9. The design/evidence document for the active milestone listed in `MASTER_INDEX.md`

Continue from `CURRENT_STATUS.md`; its marker and current-state section are authoritative.

## Current Working State

The foundations and AUTO-0001 through AUTO-0019 are COMPLETE / VERIFIED for
their approved scopes. AUTO-0020 stages 01 through 04 are COMPLETE / VERIFIED.
AUTO-0020-05 canonical document reconciliation and repository-wide evidence is
the only active stage.

The verified AUTO-0019 closure baseline is exact `master`
`c287e5cceef4e72148de7674f4095fedb78bd302`, confirmed by push-triggered
Quality #394 (run id `32484748127`).

AUTO-0020-04 merged through PR #194 as exact `master`
`e62f69d4db2f288bb072cfa38108d5872d5ebdb4` after pre-merge Quality #401.
Push-triggered Quality #402 is the exact post-merge gate for that SHA.

## Active Gate

```text
AUTO-0020-01 design/contract                         COMPLETE / VERIFIED
AUTO-0020-02 typed manifest and strict parser        COMPLETE / VERIFIED
AUTO-0020-03 deterministic read-only validator       COMPLETE / VERIFIED
AUTO-0020-04 Quality integration/failure coverage    COMPLETE / VERIFIED
AUTO-0020-05 canonical document reconciliation       ACTIVE
AUTO-0020-06 final reconciliation/next audit          PENDING
```

Read `AUTO-0020_CANONICAL_PROJECT_STATE_DOCUMENTATION_COHERENCE_GATE_DESIGN.md`,
`CANONICAL_PROJECT_STATE.json`, and the six governed canonical documents.
Quality runs the coherence validator offline before Ruff, mypy, and pytest.

## Permanent Authority Boundaries

- AUTO-0007 is permanently read-only.
- AUTO-0008 remains the sole guarded one-step apply boundary.
- AUTO-0009 is bounded orchestration over that existing boundary.
- AUTO-0010 policy can only restrict existing authority.
- AUTO-0011 approval cannot grant new mutation authority.
- AUTO-0012 receipts are deterministic evidence only.
- AUTO-0013 remains bounded remote read-only control transport.
- AUTO-0014 adds only local lifecycle supervision for that worker.
- AUTO-0015 exact post-merge verification is read-only and fail-closed.
- AUTO-0016 bootstrap/doctor and the narrow Quality relay do not repair state.
- AUTO-0018 adds reliability and diagnostics without hidden repository repair.
- AUTO-0019 may terminalize aged unresolved claims but never replay them.
- AUTO-0020 validates canonical documentation but never edits or repairs it.

Remote task classes remain `status`, `inspect`, `plan`, `diff`, and
`quality_verify`. Recovery does not invoke executor/OpenCode/`quality_verify`
and does not execute or re-execute a claimed request.

## Current Priority

Reconcile the six governed documents with verified AUTO-0019 closure and active
AUTO-0020-05, prove the tracked document set coherent, then pass exact PR-head
Quality, expected-head-protected merge, and exact post-merge `master` Quality.

Do not start AUTO-0020-06 before that gate succeeds.

## General Engineering Guardrails

- Preserve originals; extend rather than replace public contracts.
- Documentation before implementation.
- Keep changes small, deterministic, testable, and reviewable.
- Make compatibility and security claims only from recorded evidence.
- Treat published tags/releases as immutable historical evidence.
