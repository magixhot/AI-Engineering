# AI-Engineering — Current Status

<!-- canonical-project-state
{"schema_version":2,"completed_through":"AUTO-0020","active_milestone":null,"active_stage":null,"active_state":"QUIESCENT","release_line":"v0.2.0"}
-->

**Snapshot date:** 2026-08-21

**Status:** QUIESCENT

**Release line:** v0.2.0 (immutable historical release boundary)

**Completed through:** AUTO-0020

**Current milestone:** None

**Active stage:** None

## Authoritative State

The MCP/SDK/tooling/release/safety foundations and AUTO-0001 through AUTO-0020
are COMPLETE / VERIFIED for their approved scopes. No successor milestone or
stage is approved or active.

AUTO-0019 closed on exact `master`
`c287e5cceef4e72148de7674f4095fedb78bd302`. Push-triggered Quality #394
(run id `32484748127`) completed successfully for that exact SHA.

## AUTO-0020 Delivery State

| Stage | State | Evidence |
|---|---|---|
| AUTO-0020-01 Design / Contract | COMPLETE / VERIFIED | PR #191; Quality #395/#396; merged `84a8019457720554831e71d05e0b8ade7ca2d0db`. |
| AUTO-0020-02 Typed Manifest / Strict Parser | COMPLETE / VERIFIED | PR #192; Quality #397/#398; merged `85597fcc8e9acc0240330f31f6d9a904175d0e44`. |
| AUTO-0020-03 Read-Only Cross-Document Validator | COMPLETE / VERIFIED | PR #193; Quality #399/#400; merged `a9abe654ee3f2b42bab3fd2684ac27be463dbb73`. |
| AUTO-0020-04 Quality Integration / Failure Coverage | COMPLETE / VERIFIED | PR #194; Quality #401/#402; merged `e62f69d4db2f288bb072cfa38108d5872d5ebdb4`. |
| AUTO-0020-05 Canonical Document Reconciliation / Repository-Wide Evidence | COMPLETE / VERIFIED | PR #195; Quality #403/#404; merged `6e19e5f7ee35ee818a9b0ea1c8257d7f2609e364`. |
| AUTO-0020-06 Final Reconciliation / Next-Milestone Audit | COMPLETE / VERIFIED | PR #196; Quality #405/#406; merged `143ccdcbd9b39e89188cbad63577b0dc1e353941`. |

## Coherence Contract

The typed source of current project state is
`docs/CANONICAL_PROJECT_STATE.json`. It governs exactly:

- `docs/AI_CHAT_START.md`
- `docs/PROJECT_CONTEXT.md`
- `docs/PROJECT_MAP.md`
- `docs/CURRENT_STATUS.md`
- `docs/ROADMAP.md`
- `docs/MASTER_INDEX.md`

Each document contains exactly one strict document-specific
`canonical-project-state` marker. The offline validator rejects missing,
duplicate, malformed, unknown, stale, or contradictory marker claims and emits
only bounded repository-relative diagnostics. Quality runs it before Ruff,
mypy, and pytest.

The manifest/parser, validator, and Quality gate are read-only. They do not
edit documentation, repair repositories, call GitHub, control services, or
expand any execution authority.

## Preserved Control-Plane Boundaries

AUTO-0018 reliability and observability remain fail-closed and non-mutating.
AUTO-0019 recovery preserves the visible claim as an execution fence. An aged
unresolved claim may receive a separate terminal `claim_recovery_required`
envelope only after immediate reinspection. Recovery never invokes
executor/OpenCode/`quality_verify` and never executes or re-executes the
claimed request.

Remote task classes remain bounded to `status`, `inspect`, `plan`,
`diff`, and `quality_verify`. No automatic repository synchronization,
workflow mutation, credential mutation, service-control mutation,
deployment/publication/release change, or broader OpenCode authority is
authorized.

## Release Boundary

Git tag `v0.2.0` and GitHub Release `AI-Engineering 0.2.0` remain the
published historical boundary at exact candidate
`1faf14c121b7b5da7c8781e3de4e836f85838a76`. Later AUTO milestones exist on
`master` and are not retroactively inserted into that release. PyPI remains
not approved and not published.

## Current Priority

Maintain schema v2 `QUIESCENT` state until a concrete successor milestone is
separately designed and approved. Do not infer or start AUTO-0021 from
numbering alone.
