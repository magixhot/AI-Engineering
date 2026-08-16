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

## Active Engineering Work

| Area | Status |
|---|---|
| MCP / SDK foundation | COMPLETE / VERIFIED |
| CI quality gates | COMPLETE / VERIFIED |
| Workspace/Git/Python safety | COMPLETE / VERIFIED |
| REL-0003 v0.2.0 publication | COMPLETE / VERIFIED |
| AUTO-0001 through AUTO-0010 | COMPLETE / VERIFIED |
| Diagnostics maintenance | ACTIVE |

## AUTO-0010 Delivery State

| Stage | Status |
|---|---|
| AUTO-0010-01 Reconciliation Policy Design | COMPLETE / VERIFIED — PR #106; Quality #207; post-merge #208 |
| AUTO-0010-02 Typed Policy Parser / Evaluator | COMPLETE / VERIFIED — PR #107; corrected Quality #211; post-merge #212 |
| AUTO-0010-03 Safety / Determinism / Git Invariants | COMPLETE / VERIFIED — PR #108; corrected Quality #214; post-merge #215 |
| AUTO-0010-04 Orchestration + Public CLI Integration | COMPLETE / VERIFIED — PR #109; corrected Quality #220; post-merge #221 |
| AUTO-0010-05 Installed Distribution Verification | COMPLETE / VERIFIED — PR #110; Quality #222; post-merge #223 |
| AUTO-0010-06 Final Evidence / Documentation Reconciliation | COMPLETE / VERIFIED — PR #111; Quality #224; post-merge #225 |

## Current Quality Baseline

Final verified AUTO-0010 baseline:

```text
master = 1abd853da67cfb3954baa04f310837388b60b4f8
```

Post-merge Quality #225 passed on that exact master commit.

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
└── public_cli.py
```

AUTO-0007 stays read-only, AUTO-0008 stays the sole one-step apply authority, AUTO-0009 remains bounded orchestration, and AUTO-0010 policy can only restrict those existing authorities. Any next capability milestone requires a separate approved design/contract.
