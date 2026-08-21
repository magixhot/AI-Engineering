# AI-Engineering

<!-- canonical-project-state
{"schema_version":2,"completed_through":"AUTO-0021","active_milestone":"AUTO-0022","active_stage":"AUTO-0022-03","active_state":"IMPLEMENTATION_ACTIVE"}
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

The foundations and AUTO-0001 through AUTO-0021 are COMPLETE / VERIFIED for
their approved scopes. AUTO-0022-01 and AUTO-0022-02 are COMPLETE / VERIFIED;
AUTO-0022-03 body-only update and post-write evidence is the only active stage.

The verified AUTO-0019 closure baseline is exact `master`
`c287e5cceef4e72148de7674f4095fedb78bd302`, confirmed by push-triggered
Quality #394 (run id `32484748127`).

AUTO-0020 terminal state merged through PR #197 as exact `master`
`c72c79a477de630f50532a454e11d513e9727a79` after pre-merge Quality #407
and push-triggered Quality #408.

AUTO-0021-02 merged through PR #199 as exact `master`
`8363f50e86470092cdccf116e8dc00dcc8f9d43c` after pre-merge Quality #411
and push-triggered Quality #412.

AUTO-0021-03 merged through PR #200 as exact `master`
`ad30d3155ee1561e0c6e37c3e4ffd5996b55dd72` after pre-merge Quality #413
and push-triggered Quality #414.

AUTO-0021-04 merged through PR #201 as exact `master`
`965e2722ee9d232d526e716edbdabd6d9f8a0197` after pre-merge Quality #415
and push-triggered Quality #416.

AUTO-0021 terminal closure merged through PR #202 as exact `master`
`3e3c2b32d0caf677d55be9f090d4a1d236716e42` after pre-merge Quality #417
and push-triggered Quality #418.

AUTO-0022-01 merged through PR #203 as exact `master`
`3efd7714b1302f13c371f81e6b8894f08b517c6f` after pre-merge Quality #419
and push-triggered Quality #420.

AUTO-0022-02 merged through PR #204 as exact `master`
`39c9933fa3ec5bde0ab62bc89fc0a4c6b300b838` after pre-merge Quality #421
and push-triggered Quality #422.

## Milestone State

```text
AUTO-0020-01 design/contract                         COMPLETE / VERIFIED
AUTO-0020-02 typed manifest and strict parser        COMPLETE / VERIFIED
AUTO-0020-03 deterministic read-only validator       COMPLETE / VERIFIED
AUTO-0020-04 Quality integration/failure coverage    COMPLETE / VERIFIED
AUTO-0020-05 canonical document reconciliation       COMPLETE / VERIFIED
AUTO-0020-06 final reconciliation/next audit          COMPLETE / VERIFIED
AUTO-0021-01 landing coherence design                 COMPLETE / VERIFIED
AUTO-0021-02 document-set v2 / README marker          COMPLETE / VERIFIED
AUTO-0021-03 README narrative reconciliation          COMPLETE / VERIFIED
AUTO-0021-04 final audit                              COMPLETE / VERIFIED
AUTO-0022-01 control-surface coherence design         COMPLETE / VERIFIED
AUTO-0022-02 exact issue-body artifact/plan           COMPLETE / VERIFIED
AUTO-0022-03 guarded issue-body update/evidence       ACTIVE
AUTO-0022-04 final audit                              PENDING
```

Read `AUTO-0020_CANONICAL_PROJECT_STATE_DOCUMENTATION_COHERENCE_GATE_DESIGN.md`,
`CANONICAL_PROJECT_STATE.json`, `README.md`, and the six governed documents
under `docs/`.
Quality runs the coherence validator offline before Ruff, mypy, and pytest.
For current work, also read
`AUTO-0022_GITHUB_CONTROL_SURFACE_COHERENCE_DESIGN.md`,
`AUTO-0022_ISSUE_130_DESIRED_BODY.md`, and
`AUTO-0022_02_GUARDED_ISSUE_BODY_UPDATE_PLAN.md`, and
`AUTO-0022_03_ISSUE_BODY_UPDATE_EVIDENCE.md`.

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

Complete AUTO-0022-03 evidence through exact PR-head Quality,
expected-head-protected merge, and exact post-merge `master` Quality. Then
continue only with the separately gated AUTO-0022-04 final audit.

## General Engineering Guardrails

- Preserve originals; extend rather than replace public contracts.
- Documentation before implementation.
- Keep changes small, deterministic, testable, and reviewable.
- Make compatibility and security claims only from recorded evidence.
- Treat published tags/releases as immutable historical evidence.
