# AI-Engineering — Current Status

<!-- canonical-project-state
{"schema_version":2,"completed_through":"AUTO-0022","active_milestone":null,"active_stage":null,"active_state":"QUIESCENT","release_line":"v0.2.0"}
-->

**Snapshot date:** 2026-08-21

**Status:** QUIESCENT

**Release line:** v0.2.0 (immutable historical release boundary)

**Completed through:** AUTO-0022

**Current milestone:** None

**Active stage:** None

## Authoritative State

The MCP/SDK/tooling/release/safety foundations and AUTO-0001 through AUTO-0022
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

The terminal quiescent-state correction merged through PR #197 as exact
`master` `c72c79a477de630f50532a454e11d513e9727a79` after Quality #407/#408.

## AUTO-0021 Audit and Delivery State

The fresh audit found that root `README.md` is the first bootstrap document
and public GitHub landing page but was outside the six-document coherence
manifest. AUTO-0021-02 advances the exact document set to v2, adds README
first, and enforces its strict state marker. AUTO-0021-03 reconciles the
landing narrative while preserving the rule that prose is not parsed as
current state.

| Stage | State |
|---|---|
| AUTO-0021-01 Design / Contract | COMPLETE / VERIFIED — PR #198; Quality #409/#410; merged `8121e3d1b2b38c4088e32a7128c58686e459542a`. |
| AUTO-0021-02 Document-Set v2 / README Marker | COMPLETE / VERIFIED — PR #199; Quality #411/#412; merged `8363f50e86470092cdccf116e8dc00dcc8f9d43c`. |
| AUTO-0021-03 README Narrative Reconciliation | COMPLETE / VERIFIED — PR #200; Quality #413/#414; merged `ad30d3155ee1561e0c6e37c3e4ffd5996b55dd72`. |
| AUTO-0021-04 Final Audit | COMPLETE / VERIFIED — PR #201; Quality #415/#416; merged `965e2722ee9d232d526e716edbdabd6d9f8a0197`. |

AUTO-0021 final audit found no remaining repository-byte landing
contradiction. Its next-surface finding identified issue #130 body drift;
AUTO-0022 reconciled that exact external surface without expanding authority.

## AUTO-0022 Audit and Delivery State

| Stage | State |
|---|---|
| AUTO-0022-01 Design / Exact Drift Audit | COMPLETE / VERIFIED — PR #203; Quality #419/#420; merged `3efd7714b1302f13c371f81e6b8894f08b517c6f`. |
| AUTO-0022-02 Exact Desired Body / Guarded Plan | COMPLETE / VERIFIED — PR #204; Quality #421/#422; merged `39c9933fa3ec5bde0ab62bc89fc0a4c6b300b838`. |
| AUTO-0022-03 Body-Only Update / Post-Write Evidence | COMPLETE / VERIFIED — PR #205; Quality #423/#424; merged `d541d751828d9d95a828799b4e3f0345c396b103`; exact post-read matched `c99ffa0b885926a64db30c451eeb910ad5dc9b6449f1c4833908d94c43dc859e`. |
| AUTO-0022-04 Final Audit / Closure | COMPLETE / TERMINAL CLOSURE |

## Coherence Contract

The typed source of current project state is
`docs/CANONICAL_PROJECT_STATE.json`. It governs exactly:

- `README.md`
- `docs/AI_CHAT_START.md`
- `docs/PROJECT_CONTEXT.md`
- `docs/PROJECT_MAP.md`
- `docs/CURRENT_STATUS.md`
- `docs/ROADMAP.md`
- `docs/MASTER_INDEX.md`

Document-set v2 validates that exact seven-document order with README first;
document-set v1 preserves the historical exact six-document set. Each
document contains exactly one strict document-specific
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

Preserve schema v2/document-set v2 `QUIESCENT` state until a successor is
separately designed and approved. No AUTO-0023 identity is inferred.
