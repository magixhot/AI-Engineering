# AI-Engineering — Master Documentation Index

<!-- canonical-project-state
{"schema_version":2,"completed_through":"AUTO-0022","active_milestone":null,"active_stage":null,"active_state":"QUIESCENT"}
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
| AUTO-0021_REPOSITORY_LANDING_STATE_COHERENCE_DESIGN.md | Exact README extension of the canonical document set | Current contract |
| AUTO-0021_03_README_NARRATIVE_RECONCILIATION_EVIDENCE.md | README landing claims and preserved boundaries | Complete / Verified |
| AUTO-0021_04_FINAL_RECONCILIATION_NEXT_SURFACE_AUDIT.md | Repository-byte closure and external next-surface audit | Complete / Verified |
| AUTO-0021_TERMINAL_QUIESCENT_CLOSURE.md | Schema v2/document-set v2 terminal state without a successor | Current contract |
| AUTO-0022_GITHUB_CONTROL_SURFACE_COHERENCE_DESIGN.md | Exact issue #130 body reconciliation without authority expansion | Current contract |
| AUTO-0022_ISSUE_130_DESIRED_BODY.md | Exact approved future body bytes for issue #130 | Approved artifact |
| AUTO-0022_02_GUARDED_ISSUE_BODY_UPDATE_PLAN.md | Hash-guarded, single-attempt body-only update procedure | Complete / Verified |
| AUTO-0022_03_ISSUE_BODY_UPDATE_EVIDENCE.md | Exact issue #130 body-only update and independent post-read evidence | Complete / Verified |
| AUTO-0022_04_FINAL_CROSS_SURFACE_AUDIT.md | Exact cross-surface equality audit and terminal closure decision | Current terminal audit |
| REL-0004_POST_AUTO_0022_RELEASE_LINE_DECISION_DESIGN.md | Exact post-v0.2.0 delta, compatibility decision, readiness gates, and publication boundaries | Current contract / design |
| REL-0004_02_COMPATIBILITY_INVENTORY_VERSION_DECISION.md | Exact compatibility inventory, 0.3.0 decision, candidate scope, and pre-candidate blockers | Current decision / evidence |

## Engineering State

| Area | Status |
|---|---|
| MCP / SDK / tooling foundations | COMPLETE / VERIFIED |
| Release line v0.2.0 | VERIFIED HISTORICAL LINE |
| AUTO-0001 through AUTO-0022 | COMPLETE / VERIFIED |
| AUTO-0021-01 Repository Landing State Coherence Design | COMPLETE / VERIFIED |
| AUTO-0021-02 Document-Set v2 / README Marker | COMPLETE / VERIFIED |
| AUTO-0021-03 README Narrative Reconciliation | COMPLETE / VERIFIED |
| AUTO-0021-04 Final Reconciliation / Next-Surface Audit | COMPLETE / VERIFIED |
| AUTO-0022-01 GitHub Control Surface Coherence Design | COMPLETE / VERIFIED |
| AUTO-0022-02 Exact Desired Body / Guarded Plan | COMPLETE / VERIFIED |
| AUTO-0022-03 Body-Only Update / Post-Write Evidence | COMPLETE / VERIFIED |
| AUTO-0022-04 Final Cross-Surface Audit / Closure | COMPLETE / TERMINAL CLOSURE |
| REL-0004-01 Release-Line Decision / Readiness Design | COMPLETE / DESIGN-ONLY TRANSITION |
| REL-0004-02 Compatibility Inventory / Version Decision | COMPLETE / `0.3.0` SELECTED / CANDIDATE NOT PREPARED |
| REL-0004-03 Candidate Preparation | NOT APPROVED |

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

Document-set v2 governs README plus the historical six canonical Markdown
documents; document-set v1 retains its exact six-document compatibility.
Quality executes the validator offline before Ruff, mypy, and pytest.

## Preserved Boundaries

AUTO-0007 remains read-only; AUTO-0008 remains the sole one-step apply
authority; AUTO-0009 through AUTO-0012 only orchestrate, restrict, approve, or
record that existing authority. AUTO-0013 through AUTO-0019 retain their
bounded read-only control-plane contracts. AUTO-0019 recovery never replays a
claimed request. AUTO-0020 validates documentation but does not edit or repair
it and grants no workflow, service, credential, deployment, publication, or
repository mutation authority.

## Current Continuation Point

AUTO-0021-01 is COMPLETE / VERIFIED through PR #198 and Quality #409/#410.
AUTO-0021-02 is COMPLETE / VERIFIED through PR #199 and Quality #411/#412.
AUTO-0021-03 is COMPLETE / VERIFIED through PR #200 and Quality #413/#414.
AUTO-0021-04 is COMPLETE / VERIFIED through PR #201 and Quality #415/#416.
AUTO-0021 terminal closure is verified through PR #202 and Quality #417/#418.
AUTO-0022-01 is COMPLETE / VERIFIED through PR #203 and Quality #419/#420.
AUTO-0022-02 is COMPLETE / VERIFIED through PR #204 and Quality #421/#422.
AUTO-0022-03 is COMPLETE / VERIFIED through PR #205 and Quality #423/#424.
AUTO-0022 is terminally reconciled and the canonical AUTO state remains
`QUIESCENT`. REL-0004-02 selects intended `0.3.0` from exact baseline
`113e848d950629d501b5fef6e0ccdf1279d9e7f8`; package metadata and the
published line remain v0.2.0. REL-0004-03 requires separate approval. No
candidate, tag, asset, registry, or publication action is authorized.
