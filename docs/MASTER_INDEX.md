# AI-Engineering — Master Documentation Index

<!-- canonical-project-state
{"schema_version":1,"completed_through":"AUTO-0019","active_milestone":"AUTO-0020","active_stage":"AUTO-0020-04","active_state":"IMPLEMENTATION_ACTIVE"}
-->

## Project Documents

| Document | Purpose | Status |
|---|---|---|
| README.md | Project overview and release-line context | Active |
| AI_CHAT_START.md | Session bootstrap | Active |
| PROJECT_CONTEXT.md | Purpose, objectives, and architecture context | Active |
| PROJECT_MAP.md | Actual repository structure and boundaries | Active |
| CURRENT_STATUS.md | Authoritative implementation snapshot | Active |
| ROADMAP.md | Delivery state and future direction | Active |
| DECISIONS.md | Accepted engineering decisions | Active |
| CODING_STANDARDS.md | Engineering standards | Active |
| AUTO-0007_ENGINEERING_PROJECT_RECONCILIATION_PLAN_DESIGN.md | Read-only reconciliation planning contract | Complete / Verified |
| AUTO-0008_GUARDED_PROJECT_RECONCILIATION_APPLY_DESIGN.md | Guarded one-step apply authority contract | Complete / Verified |
| AUTO-0009_MULTI_STEP_RECONCILIATION_ORCHESTRATION_DESIGN.md | Bounded multi-step orchestration contract | Complete / Verified |
| AUTO-0010_RECONCILIATION_POLICY_DESIGN.md | Restriction-only reconciliation policy contract | Complete / Verified |
| AUTO-0011_RECONCILIATION_APPROVAL_DESIGN.md | Single-candidate reconciliation approval contract | Complete / Verified |
| AUTO-0012_RECONCILIATION_EXECUTION_EVIDENCE_DESIGN.md | Deterministic execution receipt contract | Complete / Verified |
| AUTO-0013_OPENCODE_CONTROL_BRIDGE_DESIGN.md | Bounded read-only OpenCode control bridge contract | Complete / Verified |
| AUTO-0013_05_END_TO_END_VERIFICATION.md | OpenCode bridge E2E verification evidence | Complete / Verified |
| AUTO-0013_FINAL_EVIDENCE.md | AUTO-0013 staged delivery and final closure evidence | Complete / Verified |
| AUTO-0014_LOCAL_CONTROL_WORKER_SERVICE_DESIGN.md | Local read-only worker service/lifecycle contract | Complete / Verified through stage 05; final gate active |
| AUTO-0014_05_INSTALLED_LOCAL_SERVICE_VERIFICATION.md | Installed user-service verification evidence | Complete / Verified |
| AUTO-0014_FINAL_EVIDENCE.md | AUTO-0014 staged delivery and final closure evidence | Final gate active |

## Active Engineering Work

| Area | Status |
|---|---|
| MCP / SDK foundation | COMPLETE / VERIFIED |
| CI quality gates | COMPLETE / VERIFIED |
| Workspace/Git/Python safety | COMPLETE / VERIFIED |
| Release line 0.2.0 | VERIFIED HISTORICAL LINE |
| AUTO-0001 through AUTO-0013 | COMPLETE / VERIFIED |
| AUTO-0014 stages 01 through 05 | COMPLETE / VERIFIED |
| AUTO-0014-06 Final Evidence / Documentation Reconciliation | ACTIVE |
| Diagnostics maintenance | ACTIVE |

## AUTO-0014 Delivery State

| Stage | Status |
|---|---|
| AUTO-0014-01 Local Worker Service Design / Contract | COMPLETE / VERIFIED — PR #137; pre-merge and exact post-merge Quality SUCCESS |
| AUTO-0014-02 Typed Runtime / Service Configuration | COMPLETE / VERIFIED — PR #138; pre-merge and exact post-merge Quality SUCCESS |
| AUTO-0014-03 Single-Instance Worker Lifecycle | COMPLETE / VERIFIED — PR #139; pre-merge and exact post-merge Quality SUCCESS |
| AUTO-0014-04 User Service Integration | COMPLETE / VERIFIED — PR #140; pre-merge and exact post-merge Quality SUCCESS |
| AUTO-0014-05 Installed Local-Service Verification | COMPLETE / VERIFIED — PR #143; Quality #302 SUCCESS; merged `58e0b3c6cd5393386ad97871aa34f6fd9e4fef47`; exact post-merge Quality SUCCESS |
| AUTO-0014-06 Final Evidence / Documentation Reconciliation | ACTIVE — final stage gate required |

Corrective prerequisites for stage 05: PR #141 added hardened `RuntimeDirectory=` handling; PR #142 added safe OpenCode execution-stage diagnostics and merged as exact master `5b5b3b0ec1922685a594679ddebc199f28b6b8d5` before the final installed-service E2E.

## Verified AUTO-0014 Evidence

Successful installed-service request:

```text
sha256:593eff3b7e76a65ec2399ea3988ae0895ea01c2bc608bb690bc62be46fe9baf7
```

Its terminal result recorded `SUCCEEDED`, repository `magixhot/AI-Engineering`, branch `master`, exact HEAD `5b5b3b0ec1922685a594679ddebc199f28b6b8d5`, `pre_clean=true`, and `post_clean=true`.

Lifecycle verification also recorded `restart=PASS`, `single-instance=PASS`, and `repository-invariants=PASS`.

## AUTO-0014 Source Tree

```text
src/ai_engineering/
├── opencode_service_config.py
├── opencode_worker_lifecycle.py
├── opencode_user_service.py
├── opencode_control_protocol.py
├── opencode_readonly_adapter.py
└── opencode_control_worker.py
```

AUTO-0007 stays read-only, AUTO-0008 stays the sole one-step apply authority, AUTO-0009 remains bounded orchestration, AUTO-0010 policy can only restrict those existing authorities, AUTO-0011 approval remains an additional fail-closed gate, AUTO-0012 receipts remain deterministic evidence only, AUTO-0013 remains bounded read-only remote inspection/control transport, and AUTO-0014 adds only local lifecycle supervision for that worker.

After AUTO-0014 closes, the approved next design direction is a read-only exact post-merge Quality verifier. It must remove manual verification without gaining workflow mutation, merge, or repository mutation authority.
