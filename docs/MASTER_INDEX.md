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
| RELEASE_CHECKLIST.md | Release-line verification checklist and evidence | Active |
| SDK-0001_TEMPLATE_DESIGN.md | SDK-0001 V1 template design | Implemented / Verified |
| SDK-0001_PROJECT_TEMPLATES.md | SDK-0001 V1 framework reference | Implemented / Verified |
| SDK-0001_1_PYTHON_SCAFFOLD_DESIGN.md | Python scaffold contract | Implemented / Verified |
| SDK-0001_2_PROJECT_TEMPLATE_CLI_DESIGN.md | Project Template CLI contract | Implemented / Verified |
| TOOL-0001_CORE_TOOL_OPERATION_VERIFICATION_DESIGN.md | Core tool verification contract | Complete / Verified |
| REL-0001_DISTRIBUTION_AND_RELEASE_VERIFICATION_DESIGN.md | Distribution/release verification contract | Complete / Verified |
| CI-0001_QUALITY_GATE_AUTOMATION_DESIGN.md | GitHub Actions quality-gate contract | Complete / Verified |
| SAFE-0001_WORKSPACE_PATH_SAFETY_DESIGN.md | Workspace safety contract | Complete / Verified |
| SAFE-0001_VERIFICATION_EVIDENCE.md | SAFE-0001 evidence | Complete / Verified |
| SAFE-0002_GIT_PYTHON_EXECUTION_SAFETY_DESIGN.md | Git/Python execution safety contract | Complete / Verified |
| SAFE-0002_VERIFICATION_EVIDENCE.md | SAFE-0002 evidence | Complete / Verified |
| AUTO-0001_ENGINEERING_PROJECT_BOOTSTRAP_DESIGN.md | Engineering bootstrap contract | Complete / Verified |
| AUTO-0001_VERIFICATION_EVIDENCE.md | AUTO-0001 evidence | Complete / Verified |
| AUTO-0002_PROJECT_DOCUMENTATION_SYNCHRONIZATION_DESIGN.md | Documentation synchronization contract | Complete / Verified |
| AUTO-0002_VERIFICATION_EVIDENCE.md | AUTO-0002 evidence | Complete / Verified |
| AUTO-0003_DOCUMENTATION_OWNERSHIP_INITIALIZATION_DESIGN.md | Documentation ownership contract | Complete / Verified |
| AUTO-0003_VERIFICATION_EVIDENCE.md | AUTO-0003 evidence | Complete / Verified |
| AUTO-0004_PROJECT_UPDATE_MIGRATION_DESIGN.md | Project migration contract | Complete / Verified |
| AUTO-0004_VERIFICATION_EVIDENCE.md | AUTO-0004 evidence | Complete / Verified |
| AUTO-0005_PYTHON_ENGINEERING_V2_DESIGN.md | V2 baseline / migration contract | Complete / Verified |
| AUTO-0005_VERIFICATION_EVIDENCE.md | AUTO-0005 evidence | Complete / Verified |
| AUTO-0006_ENGINEERING_PROJECT_HEALTH_READINESS_AUDIT_DESIGN.md | Health/readiness contract | Complete / Verified |
| AUTO-0006_VERIFICATION_EVIDENCE.md | AUTO-0006 evidence | Complete / Verified |
| AUTO-0007_ENGINEERING_PROJECT_RECONCILIATION_PLAN_DESIGN.md | AUTO-0007 reconciliation contract and staged delivery | Complete / Verified after stages 01–05 |

## Active Engineering Work

| Area | Status |
|---|---|
| MCP / SDK foundation | COMPLETE / VERIFIED |
| CI quality gates | COMPLETE / VERIFIED |
| Workspace/Git/Python safety | COMPLETE / VERIFIED |
| REL-0003 v0.2.0 publication | COMPLETE / VERIFIED |
| AUTO-0001 | COMPLETE / VERIFIED |
| AUTO-0002 | COMPLETE / VERIFIED |
| AUTO-0003 | COMPLETE / VERIFIED |
| AUTO-0004 | COMPLETE / VERIFIED |
| AUTO-0005 | COMPLETE / VERIFIED |
| AUTO-0006 | COMPLETE / VERIFIED |
| AUTO-0007 stages 01–05 | COMPLETE / VERIFIED |
| AUTO-0007-06 final documentation reconciliation | IN PROGRESS / CLOSING |
| Additional MCP client interoperability | OPTIONAL / FUTURE EVIDENCE |
| Diagnostics maintenance | ACTIVE |

## Delivery State

| Area | Status |
|---|---|
| Sprint 0 — Documentation Foundation | COMPLETED |
| Sprint 1 — MCP Foundation | IMPLEMENTED / VERIFIED |
| SDK-0001 / SDK-0001.1 / SDK-0001.2 | COMPLETE / VERIFIED |
| TOOL-0001 | COMPLETE / VERIFIED |
| REL-0001 / REL-0002 / REL-0003 | COMPLETE / VERIFIED |
| CI-0001 | COMPLETE / VERIFIED |
| SAFE-0001 / SAFE-0002 | COMPLETE / VERIFIED |
| AUTO-0001 through AUTO-0006 | COMPLETE / VERIFIED |
| AUTO-0007-01 Design | COMPLETE / VERIFIED |
| AUTO-0007-02 Planner | COMPLETE / VERIFIED — PR #83 / Quality #147 |
| AUTO-0007-03 Invariants | COMPLETE / VERIFIED — PR #84 / Quality #148 + #149 |
| AUTO-0007-04 Public CLI | COMPLETE / VERIFIED — PR #85 / Quality #157 + #160 |
| AUTO-0007-05 Installed Distribution Verification | COMPLETE / VERIFIED — PR #86 / Quality #161 + #162 |
| AUTO-0007-06 Final Reconciliation / Documentation | IN PROGRESS / CLOSING |

## Current Quality Baseline

- AUTO-0007-02: Quality #147 passed.
- AUTO-0007-03: Quality #148 and post-merge #149 passed.
- AUTO-0007-04: corrected Quality #157 and post-merge #160 passed.
- AUTO-0007-05: Quality #161 and post-merge #162 passed.
- The AUTO-0007-04 formatting-only failure #150 is historical evidence and is superseded by the corrected passing run #157.

## Published Release

- GitHub Release: `AI-Engineering 0.2.0`
- Tag: `v0.2.0`
- Tag target: `1faf14c121b7b5da7c8781e3de4e836f85838a76`
- PyPI: not approved / not published

## Source Tree

```text
src/ai_engineering/
├── discovery/   ├── git/       ├── ide/adapters/  ├── mcp/debug/
├── python/      ├── registry/  ├── runtime/       ├── shared/
├── stdio/       ├── tools/     ├── workspace/
├── project_inspection.py
├── project_git_readiness.py
├── project_health.py
├── project_reconciliation.py
├── project_reconciliation_cli.py
├── documentation_sync.py
├── documentation_apply.py
├── documentation_ownership.py
├── project_migration.py
├── project_migration_apply.py
└── python_engineering_baseline.py
```

The repository has no `transport/` package.
