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
| AUTO-0012_RECONCILIATION_EXECUTION_EVIDENCE_DESIGN.md | Deterministic reconciliation execution receipt contract | Complete / Verified |
| AUTO-0012_FINAL_EVIDENCE.md | AUTO-0012 staged delivery and closure evidence | Complete / Verified |

## Active Engineering Work

| Area | Status |
|---|---|
| MCP / SDK foundation | COMPLETE / VERIFIED |
| CI quality gates | COMPLETE / VERIFIED |
| Workspace/Git/Python safety | COMPLETE / VERIFIED |
| Release line 0.2.0 | VERIFIED HISTORICAL LINE |
| AUTO-0001 through AUTO-0012 | COMPLETE / VERIFIED |
| Diagnostics maintenance | ACTIVE |

## AUTO-0012 Delivery State

| Stage | Status |
|---|---|
| AUTO-0012-01 Execution Evidence Design / Contract | COMPLETE / VERIFIED — PR #121; Quality #248; post-merge #249 |
| AUTO-0012-02 Typed Receipt Model / Canonicalization | COMPLETE / VERIFIED — PR #122; corrected Quality #251; post-merge #252 |
| AUTO-0012-03 Evidence Projection / Safety Invariants | COMPLETE / VERIFIED — PR #123; Quality #253; post-merge #254 |
| AUTO-0012-04 Public CLI Integration | COMPLETE / VERIFIED — PR #124; corrected Quality #257; post-merge #258 |
| AUTO-0012-05 Installed Distribution Verification | COMPLETE / VERIFIED — PR #125; corrected Quality #260; post-merge #261 |
| AUTO-0012-06 Final Evidence / Documentation Reconciliation | DOCUMENTATION CLOSURE — no authority expansion |

## Verified Closure Evidence

AUTO-0012 verified implementation baseline before final documentation reconciliation:

```text
2268f4c8278f3c81b5735e26337984aebd300c6b
```

Exact post-merge Quality #261 succeeded on that commit. This baseline is historical evidence only and is not a claim that later `master` must equal that SHA.

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
├── project_reconciliation_receipt.py
├── project_reconciliation_receipt_projection.py
├── project_reconciliation_receipt_cli.py
└── public_cli.py
```

AUTO-0007 stays read-only, AUTO-0008 stays the sole one-step apply authority, AUTO-0009 remains bounded orchestration, AUTO-0010 policy can only restrict those existing authorities, AUTO-0011 approval remains an additional single-candidate fail-closed gate, and AUTO-0012 receipts remain deterministic evidence only. No later capability milestone is active until a separate design/contract is approved and started.
