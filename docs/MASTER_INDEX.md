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
| MCP-0002_SDK_BOUNDARY_VERIFICATION.md | MCP SDK boundary contract and verification matrix | Complete / Verified |
| MCP-0003_ANTIGRAVITY_INTEROPERABILITY_VERIFICATION.md | Antigravity MCP interoperability evidence | Verified |
| AUTO-0007_ENGINEERING_PROJECT_RECONCILIATION_PLAN_DESIGN.md | Read-only reconciliation planning contract | Complete / Verified |
| AUTO-0008_GUARDED_PROJECT_RECONCILIATION_APPLY_DESIGN.md | Guarded one-step reconciliation execution authority contract | Complete / Verified |
| AUTO-0009_MULTI_STEP_RECONCILIATION_ORCHESTRATION_DESIGN.md | Bounded multi-step orchestration contract | Active / Verified through stage 05 |

## Active Engineering Work

| Area | Status |
|---|---|
| MCP / SDK foundation | COMPLETE / VERIFIED |
| CI quality gates | COMPLETE / VERIFIED |
| Workspace/Git/Python safety | COMPLETE / VERIFIED |
| REL-0003 v0.2.0 publication | COMPLETE / VERIFIED |
| AUTO-0001 through AUTO-0008 | COMPLETE / VERIFIED |
| AUTO-0009 stages 01–05 | COMPLETE / VERIFIED |
| AUTO-0009-06 Final Evidence / Documentation Reconciliation | IN PROGRESS |
| Diagnostics maintenance | ACTIVE |

## AUTO-0009 Delivery State

| Stage | Status |
|---|---|
| AUTO-0009-01 Multi-step Orchestration Design | COMPLETE / VERIFIED — PR #99; Quality #189; post-merge #190 |
| AUTO-0009-02 Guarded Orchestrator Core | COMPLETE / VERIFIED — PR #100; corrected Quality #193; post-merge #194 |
| AUTO-0009-03 Safety / Progress / Failure Invariants | COMPLETE / VERIFIED — PR #101; Quality #195; post-merge #196 |
| AUTO-0009-04 Public CLI | COMPLETE / VERIFIED — PR #102; corrected Quality #199; post-merge #200 |
| AUTO-0009-05 Installed Distribution Verification | COMPLETE / VERIFIED — PR #103; Quality #201; post-merge #202 |
| AUTO-0009-06 Final Evidence / Documentation Reconciliation | IN PROGRESS |

## Current Quality Baseline

Verified implementation baseline entering AUTO-0009-06:

```text
master = 9564f8ffdc869bb0d8058f74c78c1e5138e5a37c
```

Post-merge Quality #202 passed on that exact master commit.

## Published Release

- GitHub Release: `AI-Engineering 0.2.0`
- Tag: `v0.2.0`
- Tag target: `1faf14c121b7b5da7c8781e3de4e836f85838a76`
- PyPI: not approved / not published

## Reconciliation Source Tree

```text
src/ai_engineering/
├── project_reconciliation.py
├── project_reconciliation_cli.py
├── project_reconciliation_apply.py
├── project_reconciliation_apply_cli.py
├── project_reconciliation_orchestration.py
├── project_reconciliation_orchestration_cli.py
└── public_cli.py
```

AUTO-0007 stays read-only, AUTO-0008 stays the sole one-step apply authority, and AUTO-0009 only orchestrates bounded repeated replan/apply cycles. Stage 06 must pass its own Quality and post-merge gates before AUTO-0009 is declared COMPLETE / VERIFIED.
