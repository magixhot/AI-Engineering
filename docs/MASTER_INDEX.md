# AI-Engineering — Master Documentation Index

<!-- canonical-project-state
{"schema_version":2,"completed_through":"AUTO-0020","active_milestone":"AUTO-0021","active_stage":"AUTO-0021-01","active_state":"DESIGN_ACTIVE"}
-->

## Canonical Project Documents

| Document | Purpose | Status |
|---|---|---|
| README.md | Project overview and release-line context | Active |
| AI_CHAT_START.md | Session bootstrap and canonical milestone state | Active / governed |
| PROJECT_CONTEXT.md | Purpose, architecture, objectives, and baselines | Active / governed |
| PROJECT_MAP.md | Repository structure and system boundaries | Active / governed |
| CURRENT_STATUS.md | Authoritative implementation snapshot | Active / governed |
| ROADMAP.md | Delivery state and current priority | Active / governed |
| MASTER_INDEX.md | Documentation inventory and active evidence | Active / governed |
| CANONICAL_PROJECT_STATE.json | Typed source for governed current-state projections | Active / authoritative |
| DECISIONS.md | Accepted engineering decisions | Active |
| CODING_STANDARDS.md | Engineering standards | Active |

## Automation Design and Evidence

| Milestone documents | Scope | Status |
|---|---|---|
| AUTO-0007 through AUTO-0012 design/evidence | Reconciliation planning, guarded execution, policy, approval, receipts | Complete / Verified |
| AUTO-0013 design/E2E/final evidence | Bounded read-only GitHub/OpenCode control bridge | Complete / Verified |
| AUTO-0014 design/installed/final evidence | User-scoped worker lifecycle supervision | Complete / Verified |
| AUTO-0015 design/live/final evidence | Exact post-merge Quality verifier | Complete / Verified |
| AUTO-0016 bootstrap/doctor/relay/final evidence | Portable workstation readiness and read-only relay | Complete / Verified |
| AUTO-0017 design/final evidence | Canonical state/roadmap reconciliation | Complete / Verified |
| AUTO-0018 design/installed/final evidence | Control-plane reliability and observability | Complete / Verified |
| AUTO-0019 design/recovery/installed/final evidence | Aged unresolved-claim terminalization without replay | Complete / Verified |
| AUTO-0020_CANONICAL_PROJECT_STATE_DOCUMENTATION_COHERENCE_GATE_DESIGN.md | Manifest, validator, Quality gate, and reconciliation contract | Complete / Verified |
| AUTO-0020_05_CANONICAL_DOCUMENT_RECONCILIATION_EVIDENCE.md | Six-document reconciliation and repository-wide coherence evidence | Complete / Verified |
| AUTO-0020_06_FINAL_RECONCILIATION_NEXT_MILESTONE_AUDIT.md | Final coherence closure and terminal-state modeling audit | Complete / Verified |
| AUTO-0020_TERMINAL_QUIESCENT_STATE_EXTENSION.md | Schema v2 terminal state without an active successor | Current contract |
| AUTO-0021_REPOSITORY_LANDING_STATE_COHERENCE_DESIGN.md | Exact README extension of the canonical document set | Active |

## Engineering State

| Area | Status |
|---|---|
| MCP / SDK / tooling foundations | COMPLETE / VERIFIED |
| Release line v0.2.0 | VERIFIED HISTORICAL LINE |
| AUTO-0001 through AUTO-0020 | COMPLETE / VERIFIED |
| AUTO-0021-01 Repository Landing State Coherence Design | ACTIVE |

## AUTO-0020 Delivery Evidence

| Stage | Evidence |
|---|---|
| AUTO-0020-01 Design / Contract | PR #191; Quality #395/#396; exact merge `84a8019457720554831e71d05e0b8ade7ca2d0db` |
| AUTO-0020-02 Typed Manifest / Strict Parser | PR #192; Quality #397/#398; exact merge `85597fcc8e9acc0240330f31f6d9a904175d0e44` |
| AUTO-0020-03 Read-Only Validator | PR #193; Quality #399/#400; exact merge `a9abe654ee3f2b42bab3fd2684ac27be463dbb73` |
| AUTO-0020-04 Quality Integration / Failure Coverage | PR #194; Quality #401/#402; exact merge `e62f69d4db2f288bb072cfa38108d5872d5ebdb4` |
| AUTO-0020-05 Canonical Reconciliation / Repository-Wide Evidence | PR #195; Quality #403/#404; exact merge `6e19e5f7ee35ee818a9b0ea1c8257d7f2609e364` |
| AUTO-0020-06 Final Reconciliation / Next Audit | PR #196; Quality #405/#406; exact merge `143ccdcbd9b39e89188cbad63577b0dc1e353941` |

## Coherence Source and Tests

```text
docs/CANONICAL_PROJECT_STATE.json
src/ai_engineering/project_state_manifest.py
src/ai_engineering/project_state_coherence.py
tests/unit/test_project_state_manifest.py
tests/unit/test_project_state_coherence.py
.github/workflows/quality.yml
```

The validator governs exactly the six canonical Markdown documents listed in
the manifest. Quality executes it offline before Ruff, mypy, and pytest.

## Preserved Boundaries

AUTO-0007 remains read-only; AUTO-0008 remains the sole one-step apply
authority; AUTO-0009 through AUTO-0012 only orchestrate, restrict, approve, or
record that existing authority. AUTO-0013 through AUTO-0019 retain their
bounded read-only control-plane contracts. AUTO-0019 recovery never replays a
claimed request. AUTO-0020 validates documentation but does not edit or repair
it and grants no workflow, service, credential, deployment, publication, or
repository mutation authority.

## Current Continuation Point

AUTO-0021-01 is the approved active design stage. Complete its exact gates,
then continue only with the approved README/document-set-v2 scope.
