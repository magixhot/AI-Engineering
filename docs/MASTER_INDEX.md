# AI-Engineering — Master Documentation Index

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
| AUTO-0013_05_END_TO_END_VERIFICATION.md | Installed/local-worker E2E verification evidence | Complete / Verified |
| AUTO-0013_FINAL_EVIDENCE.md | AUTO-0013 staged delivery and final closure evidence | Complete / Verified |

## Active Engineering Work

| Area | Status |
|---|---|
| MCP / SDK foundation | COMPLETE / VERIFIED |
| CI quality gates | COMPLETE / VERIFIED |
| Workspace/Git/Python safety | COMPLETE / VERIFIED |
| Release line 0.2.0 | VERIFIED HISTORICAL LINE |
| AUTO-0001 through AUTO-0013 | COMPLETE / VERIFIED |
| Diagnostics maintenance | ACTIVE |

## AUTO-0013 Delivery State

| Stage | Status |
|---|---|
| AUTO-0013-01 Control Bridge Design / Contract | COMPLETE / VERIFIED — PR #127; Quality #265; exact post-merge Quality SUCCESS |
| AUTO-0013-02 Typed Request / Result Protocol | COMPLETE / VERIFIED — PR #128; Quality #268; exact post-merge Quality SUCCESS |
| AUTO-0013-03 Read-Only OpenCode Adapter | COMPLETE / VERIFIED — PR #129; Quality #270; exact post-merge Quality SUCCESS |
| AUTO-0013-04 GitHub Control Worker | COMPLETE / VERIFIED — PR #131; Quality #273; exact post-merge Quality SUCCESS |
| AUTO-0013-04 Corrective Failed-Result Hardening | COMPLETE / VERIFIED — PR #132; Quality #275; exact post-merge Quality SUCCESS |
| AUTO-0013-05 OpenCode Workspace Routing | COMPLETE / VERIFIED prerequisite — PR #133; Quality #278; exact post-merge Quality SUCCESS |
| AUTO-0013-05 End-to-End Verification | COMPLETE / VERIFIED — PR #134; Quality #280; exact post-merge Quality SUCCESS |
| AUTO-0013-06 Final Evidence / Documentation Reconciliation | COMPLETE / VERIFIED — PR #135; Quality #282; exact post-merge Quality #283 SUCCESS on `0aaa95e8119e79fca3a2a100f6d629887c3fb5a6` |

## Verified AUTO-0013 Evidence

Successful live request:

```text
sha256:dcdfcd976fff8c7afd16352fdc63e2781c7067c6492c4e43733abd4bd6efeb2c
```

Its terminal result recorded `SUCCEEDED`, repository `magixhot/AI-Engineering`, branch `master`, exact HEAD `2d03f9e37e373def6b0f705b6f2b5da751279427`, `pre_clean=true`, and `post_clean=true`.

## AUTO-0013 Source Tree

```text
.opencode/agents/
└── auto-0013-readonly.md

src/ai_engineering/
├── opencode_control_protocol.py
├── opencode_readonly_adapter.py
└── opencode_control_worker.py
```

AUTO-0007 stays read-only, AUTO-0008 stays the sole one-step apply authority, AUTO-0009 remains bounded orchestration, AUTO-0010 policy can only restrict those existing authorities, AUTO-0011 approval remains an additional fail-closed gate, AUTO-0012 receipts remain deterministic evidence only, and AUTO-0013 remains bounded read-only remote inspection/control transport only.

No later AUTO capability is active. Automatic local worker startup, altered event delivery, a private control surface, or any write/apply capability requires a separate future design/contract.
