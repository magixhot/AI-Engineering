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
| MCP_SDK_AUDIT.md | SDK integration audit record | Complete / VS Code verified |
| MCP_SDK_MIGRATION_REPORT.md | SDK migration evidence and client verification record | Complete / VS Code verified |
| MCP-0002_SDK_BOUNDARY_VERIFICATION.md | MCP SDK boundary contract and verification matrix | Complete / VS Code and Antigravity verified |
| MCP-0003_ANTIGRAVITY_INTEROPERABILITY_VERIFICATION.md | Antigravity MCP interoperability verification evidence | Verified |
| MCP_DIAGNOSTICS.md | MCP diagnostics operation | Active |
| STABILIZATION_PLAN.md | Historical stabilization plan | Active / historical context |
| RELEASE_CHECKLIST.md | Release-line verification checklist and evidence | Active |
| SDK-0001_TEMPLATE_DESIGN.md | SDK-0001 V1 authoritative template design | Implemented / verified |
| SDK-0001_PROJECT_TEMPLATES.md | SDK-0001 V1 framework reference | Implemented / verified |
| SDK-0001_1_PYTHON_SCAFFOLD_DESIGN.md | SDK-0001.1 Python scaffold contract | Implemented / verified |
| SDK-0001_2_PROJECT_TEMPLATE_CLI_DESIGN.md | SDK-0001.2 Project Template CLI contract | Implemented / verified |
| TOOL-0001_CORE_TOOL_OPERATION_VERIFICATION_DESIGN.md | Core Workspace, Git, and Python tool-operation verification contract | Complete / Verified |
| REL-0001_DISTRIBUTION_AND_RELEASE_VERIFICATION_DESIGN.md | Distribution and release verification contract | Complete / Verified |
| REL-0002_RELEASE_PUBLICATION_DECISION_CONTRACT.md | Git tag, GitHub Release, PyPI, evidence, and publication-approval governance | Complete / Verified for v0.1.0 GitHub scope |
| REL-0002_POST_RELEASE_RECONCILIATION.md | Actual v0.1.0 tag/release publication evidence and post-release scope reconciliation | Complete / Verified |
| REL-0003_NEXT_RELEASE_LINE_DESIGN.md | 0.2.0 release-line decision, candidate freeze, artifact/evidence, and publication contract | Complete / Verified |
| REL-0003_0.2.0_RELEASE_READINESS.md | Exact 0.2.0 candidate SHA and Linux/Windows/distribution readiness evidence | Complete / Verified |
| REL-0003_0.2.0_RELEASE_NOTES.md | Prepared 0.2.0 GitHub Release notes | Published basis |
| REL-0003_POST_RELEASE_RECONCILIATION.md | Actual v0.2.0 tag, GitHub Release, assets, digests, and publication-boundary evidence | Complete / Verified |
| CI-0001_QUALITY_GATE_AUTOMATION_DESIGN.md | GitHub Actions quality-gate automation contract | Complete / Verified |
| SAFE-0001_WORKSPACE_PATH_SAFETY_DESIGN.md | Workspace root, containment, link-escape, and controlled-error security contract/evidence | Complete / Verified |
| SAFE-0001_VERIFICATION_EVIDENCE.md | Compact Linux/Windows SAFE-0001 verification record | Complete / Verified |
| SAFE-0002_GIT_PYTHON_EXECUTION_SAFETY_DESIGN.md | Active MCP Git/Python authority-root, subprocess, path, and compatibility security contract | Implemented / Verified |
| SAFE-0002_VERIFICATION_EVIDENCE.md | Linux/Windows Git/Python boundary, link-escape, subprocess, and regression evidence | Complete / Verified |
| AUTO-0001_ENGINEERING_PROJECT_BOOTSTRAP_DESIGN.md | Additive engineering bootstrap API/profile/verification/CLI contract over SDK-0001 | Complete / Verified |
| AUTO-0001_VERIFICATION_EVIDENCE.md | Core API, CLI, installed-wheel, CI, and publication-boundary evidence | Complete / Verified |
| AUTO-0002_PROJECT_DOCUMENTATION_SYNCHRONIZATION_DESIGN.md | Bounded inspection, drift, deterministic planning, guarded apply, and ownership contract | Implemented / Verified |
| AUTO-0002_4_CLI_AND_DISTRIBUTION_VERIFICATION.md | Exact installed `project docs check/plan/apply` CLI and isolated-distribution contract | Implemented / Verified |
| AUTO-0002_VERIFICATION_EVIDENCE.md | Inspection, drift, apply, CLI, installed-wheel, and CI evidence | Complete / Verified |
| AUTO-0003_DOCUMENTATION_OWNERSHIP_INITIALIZATION_DESIGN.md | Safe deterministic initialization of AUTO-0002 ownership markers and managed sections | Design / Proposed |

## Active Engineering Work

| Area | Status |
|---|---|
| MCP-0002 evidence maintenance | COMPLETE |
| MCP-0003 Antigravity interoperability | VERIFIED |
| Official Python MCP SDK migration | COMPLETE |
| REL-0001 local distribution verification | COMPLETE / VERIFIED |
| CI-0001 quality gate automation | COMPLETE / VERIFIED |
| SAFE-0001 workspace path safety | COMPLETE / VERIFIED |
| SAFE-0002 Git/Python execution safety | COMPLETE / VERIFIED |
| REL-0002 v0.1.0 GitHub publication | COMPLETE / VERIFIED |
| REL-0003 v0.2.0 GitHub publication | COMPLETE / VERIFIED |
| AUTO-0001 engineering project bootstrap | COMPLETE / VERIFIED |
| AUTO-0002 project documentation synchronization | COMPLETE / VERIFIED |
| AUTO-0003 documentation ownership initialization | DESIGN / PROPOSED |
| Additional MCP client interoperability | OPTIONAL / FUTURE EVIDENCE |
| Diagnostics maintenance | ACTIVE |

## Delivery State

| Sprint / Area | Status |
|---|---|
| Sprint 0 — Documentation Foundation | COMPLETED |
| Sprint 1 — MCP Foundation | IMPLEMENTED / VERIFIED |
| Workspace, Git, and Python tool subsystems | IMPLEMENTED / VERIFIED |
| SDK-0001 Project Templates V1 | IMPLEMENTED / VERIFIED |
| SDK-0001.1 Standalone Python Project Scaffold | COMPLETE / VERIFIED |
| SDK-0001.2 Project Template CLI | COMPLETE / VERIFIED |
| Antigravity MCP interoperability | VERIFIED |
| TOOL-0001 core tool operations | COMPLETE / VERIFIED |
| REL-0001 local distribution verification | COMPLETE / VERIFIED |
| CI-0001 quality gate automation | COMPLETE / VERIFIED |
| SAFE-0001 workspace path safety | COMPLETE / VERIFIED |
| SAFE-0002 Git/Python execution safety | COMPLETE / VERIFIED |
| REL-0002 v0.1.0 publication | COMPLETE / VERIFIED |
| REL-0003 v0.2.0 publication | COMPLETE / VERIFIED |
| M3 / AUTO-0001 Engineering Project Bootstrap | COMPLETE / VERIFIED |
| M3 / AUTO-0002 Project Documentation Synchronization | COMPLETE / VERIFIED |
| M3 / AUTO-0003 Documentation Ownership Initialization | DESIGN |
| Additional client and IDE interoperability | PLANNED |

## Published Release

- Current GitHub Release: `AI-Engineering 0.2.0`
- Current tag: `v0.2.0`
- Tag target: `1faf14c121b7b5da7c8781e3de4e836f85838a76`
- Assets: `ai_engineering-0.2.0-py3-none-any.whl`, `ai_engineering-0.2.0.tar.gz`
- Historical release: `v0.1.0` at `73929bd15fa7637db8162aac199697582bb25e67`
- PyPI: not approved / not published

## Current Quality Baseline

- Exact 0.2.0 candidate passed post-merge GitHub Actions Quality #79 on Linux/Python 3.11.
- Readiness documentation passed PR Quality #80 and post-merge Quality #81.
- Post-v0.2.0 reconciliation passed PR Quality #82 and post-merge Quality #83.
- Windows candidate evidence: pytest 153 passed, 2 permitted symlink-fixture skips due to `WinError 1314`; Ruff 0; mypy 0 in 79 source files; focused release distribution test 1 passed; `git diff --check` passed; working tree clean.
- Installed-wheel verification covers `ai-engineering project create`, `project bootstrap`, and `project docs check/plan/apply` outside the source checkout.

## Source Tree

```text
src/ai_engineering/
├── discovery/   ├── git/       ├── ide/adapters/  ├── mcp/debug/
├── python/      ├── registry/  ├── runtime/       ├── shared/
├── stdio/       ├── tools/     ├── workspace/
├── project_inspection.py
├── documentation_sync.py
└── documentation_apply.py
```

The repository has no `transport/` package.
