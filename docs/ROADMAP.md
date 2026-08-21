# AI-Engineering Roadmap

<!-- canonical-project-state
{"schema_version":1,"completed_through":"AUTO-0019","active_milestone":"AUTO-0020","active_stage":"AUTO-0020-05","active_state":"IMPLEMENTATION_ACTIVE"}
-->

## Completed / Verified

The documentation foundation, MCP foundation, SDK-0001, TOOL-0001, REL-0001/REL-0002/REL-0003, CI-0001, SAFE-0001/SAFE-0002, and AUTO-0001 through AUTO-0019 are COMPLETE / VERIFIED for their approved scopes.

Established automation boundaries remain layered and unchanged: AUTO-0007 is the permanent read-only reconciliation planner; AUTO-0008 is the guarded one-step apply boundary; AUTO-0009 is bounded multi-step orchestration; AUTO-0010 is the restrictive policy gate; AUTO-0011 is the optional explicit single-candidate approval gate; AUTO-0012 adds deterministic execution evidence; AUTO-0013 adds bounded read-only remote inspection/control transport; AUTO-0014 adds local worker lifecycle supervision; AUTO-0015 adds exact post-merge Quality verification; AUTO-0016 adds portable workstation bootstrap/doctor behavior plus the narrow read-only Quality relay; AUTO-0017 reconciles canonical project state/roadmap documentation with the verified implementation state; AUTO-0018 hardens reliability/observability of the existing read-only control plane; and AUTO-0019 adds bounded terminal recovery for aged unresolved claims without replaying their requests.

## AUTO-0014 — Local Control Worker Service / Lifecycle

**Status:** COMPLETE / VERIFIED

AUTO-0014 removed manual worker startup through local user-service lifecycle supervision around the existing AUTO-0013 read-only worker. Installed verification covered restart, single-instance, repository invariants, and successful read-only request behavior. AUTO-0014 final reconciliation is complete.

## AUTO-0015 — Exact Post-Merge Quality Verifier

**Status:** COMPLETE / VERIFIED

AUTO-0015 added deterministic read-only verification of the exact merged `master` Quality run. It requires workflow `.github/workflows/quality.yml`, branch `master`, event `push`, the exact target `head_sha`, terminal `completed` status, and successful conclusion. It fails closed when evidence is missing, ambiguous, incomplete, or inconsistent.

## AUTO-0016 — Workstation Bootstrap / Doctor

**Status:** COMPLETE / VERIFIED

AUTO-0016 delivered a portable workstation bootstrap contract, discovery-before-action rules, canonical worker identity `ai-engineering-worker.service`, a typed read-only workstation doctor with deterministic `READY` / `NOT_READY` semantics, a read-only doctor runtime/CLI, installed negative-path and isolated positive-path evidence, and a narrow read-only Quality relay that publishes typed exact post-merge evidence through the existing GitHub control channel.

## AUTO-0017 — Project State / Roadmap Reconciliation

**Status:** COMPLETE / VERIFIED

AUTO-0017 reconciled canonical project-state documentation with the verified implementation state through AUTO-0016 and completed a fresh post-reconciliation hardening audit. All five delivery stages are COMPLETE / VERIFIED, with exact post-merge Quality success on final merged `master` SHA `8a4375257882fd846bbb605c8791c04a6d602478`.

AUTO-0017 remained documentation-only in authority and did not expand runtime or execution behavior.

## AUTO-0018 — Read-Only Control Plane Reliability / Observability Hardening

**Status:** COMPLETE / VERIFIED

AUTO-0018 implemented and verified the approved reliability/observability hardening of the existing read-only control plane while preserving all prior authority boundaries.

Delivered stages:

1. AUTO-0018-01 — design/contract.
2. AUTO-0018-02 — typed protocol-rejection/failure taxonomy primitives.
3. AUTO-0018-03 — bounded control-channel read retry/backoff and low-noise transport observability.
4. AUTO-0018-04 — non-mutating expected-head mismatch diagnostics and deterministic operator guidance.
5. AUTO-0018-05 — installed/E2E stale-workspace and exact-Quality evidence plus cross-boundary audit.
6. AUTO-0018-06 — final reconciliation and hardening evidence.

Final exact post-merge verification succeeded on `master` `bfce3e267ddd16b355ca0ac668138f8ccfa20bae` with the required `.github/workflows/quality.yml`, `master` / `push`, exact-head, `completed/success`, `satisfies_gate=true`, and clean pre/post evidence.

AUTO-0018 did not add remote write/apply authority, automatic repository repair, workflow rerun/cancel/dispatch, service-control mutation, credential mutation, deployment/publication/release scope, or expanded OpenCode authority.

## AUTO-0019 — Read-Only Control Request Recovery / Terminalization

**Status:** COMPLETE / VERIFIED

AUTO-0019 implemented and verified the approved no-replay recovery contract. A visible claim remains an execution fence; an aged unresolved claim may be terminalized with bounded `claim_recovery_required` evidence, but recovery never executes or re-executes the claimed request.

Delivered stages:

1. AUTO-0019-01 — design/contract.
2. AUTO-0019-02 — typed unresolved-claim lifecycle primitives.
3. AUTO-0019-03 — deterministic aged-claim discovery, immediate reinspection, and terminalization.
4. AUTO-0019-04 — ambiguous-publication/concurrency hardening and focused failure-mode tests.
5. AUTO-0019-05 — installed/E2E stranded-claim evidence, distinct liveness verification, and cross-boundary audit.
6. AUTO-0019-06 — final reconciliation and hardening evidence.

Final exact post-merge verification succeeded on `master` `c287e5cceef4e72148de7674f4095fedb78bd302` through push-triggered Quality #394 (run id `32484748127`).

AUTO-0019 preserves the existing task-class and authority boundaries. It does not add remote write/apply authority, automatic repository synchronization/repair, workflow mutation, service-control mutation, credentials, deployment/publication/release scope, or broader OpenCode authority.

## AUTO-0020 — Canonical Project-State Documentation Coherence Gate

**Status:** IMPLEMENTATION ACTIVE

The fresh post-AUTO-0019 audit found that the six canonical bootstrap/state
documents disagreed about the completed and active milestone state. At the
milestone start, several identified AUTO-0014-06 as active,
`PROJECT_CONTEXT.md` identified AUTO-0018-06, and this roadmap identified
AUTO-0019-01 as current.

AUTO-0020 defines a narrow machine-readable canonical-state contract, deterministic offline/read-only cross-document validation, and Quality integration that rejects stale or ambiguous current-state claims. It will then reconcile the governed documents through exact verified AUTO-0019 evidence.

AUTO-0020 does not authorize automatic documentation edits, reconciliation apply/run, repository repair, workflow mutation, service control, credentials, deployment/publication/release changes, or broader OpenCode authority.

Delivery state:

1. AUTO-0020-01 — design/contract: COMPLETE / VERIFIED.
2. AUTO-0020-02 — typed canonical-state manifest and strict parser: COMPLETE / VERIFIED.
3. AUTO-0020-03 — deterministic read-only cross-document validator: COMPLETE / VERIFIED.
4. AUTO-0020-04 — Quality integration and failure-mode coverage: COMPLETE / VERIFIED.
5. AUTO-0020-05 — canonical document reconciliation and repository-wide evidence: ACTIVE.
6. AUTO-0020-06 — final reconciliation / next-milestone audit: PENDING.

AUTO-0020-04 merged through PR #194 as exact `master`
`e62f69d4db2f288bb072cfa38108d5872d5ebdb4` after Quality #401/#402.

## Current Priority

Complete AUTO-0020-05 canonical document reconciliation and repository-wide
coherence evidence through the normal exact PR-head Quality gate,
expected-head-protected merge, and exact post-merge `master` push Quality
gate.

Do not start AUTO-0020-06 before that gate succeeds.
