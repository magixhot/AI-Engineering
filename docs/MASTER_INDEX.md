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
| AUTO-0009_FINAL_EVIDENCE.md | AUTO-0009 final verified evidence | Complete / Verified |
| AUTO-0010_RECONCILIATION_POLICY_DESIGN.md | Restriction-only reconciliation policy contract | Complete / Verified |
| AUTO-0010_FINAL_EVIDENCE.md | AUTO-0010 final verified evidence | Complete / Verified |
| AUTO-0011_RECONCILIATION_APPROVAL_DESIGN.md | Single-candidate reconciliation approval contract | Complete / Verified |
| AUTO-0011_FINAL_EVIDENCE.md | AUTO-0011 staged delivery and closure evidence | Complete / Verified |

## Active Engineering Work

| Area | Status |
|---|---|
| MCP / SDK foundation | COMPLETE / VERIFIED |
| CI quality gates | COMPLETE / VERIFIED |
| Workspace/Git/Python safety | COMPLETE / VERIFIED |
| REL-0003 v0.2.0 publication | COMPLETE / VERIFIED |
| AUTO-0001 through AUTO-0011 | COMPLETE / VERIFIED |
| Diagnostics maintenance | ACTIVE |

## AUTO-0011 Delivery State

| Stage | Status |
|---|---|
| AUTO-0011-01 Reconciliation Approval Design | COMPLETE / VERIFIED — PR #113; Quality #228; post-merge #229 |
| AUTO-0011-02 Typed Approval Model / Canonicalization | COMPLETE / VERIFIED — PR #114; corrected Quality #232; post-merge #233 |
| AUTO-0011-03 Approval Verification / Safety Invariants | COMPLETE / VERIFIED — PR #115; corrected Quality #235; post-merge #236 |
| AUTO-0011-04 Guarded Integration | COMPLETE / VERIFIED — PR #116; corrected Quality #238; post-merge #239 |
| AUTO-0011-05 Installed Distribution Verification | COMPLETE / VERIFIED — PR #117; Quality #240; post-merge #241 |
| AUTO-0011-06 Final Evidence / Documentation Reconciliation | COMPLETE / VERIFIED — PR #118; Quality #242; post-merge #243 |

Administrative closure record PR #119 passed Quality #244 and exact post-merge Quality #245.

## Verified Closure Evidence

AUTO-0011 stage-06 capability/documentation baseline:

```text
94449b8754bb0bd803b5d60f38292e1530b82b1e
```

Administrative closure verification commit `b3d3d2f20cb3827f129ef1e6479f89bf015ae1f8` is historical evidence only. It is not a claim that later `master` must equal that SHA.

## Reconciliation Source Tree

```text
src/ai_engineering/
├── project_reconciliation.py
├── project_reconciliation_cli.py
├── project_reconciliation_apply.py
├── project_reconciliation_apply_cli.py
├── project_reconciliation_orchestration.py
├── project_reconciliation_orchestration_cli.py
├── project_reconciliation_policy.py
├── project_reconciliation_approval.py
├── project_reconciliation_approval_context.py
├── project_reconciliation_approval_verification.py
└── public_cli.py
```

AUTO-0007 stays read-only, AUTO-0008 stays the sole one-step apply authority, AUTO-0009 remains bounded orchestration, AUTO-0010 policy can only restrict those existing authorities, and AUTO-0011 approval is an additional single-candidate fail-closed gate. No later capability milestone is active until a separate design/contract is approved and started.
