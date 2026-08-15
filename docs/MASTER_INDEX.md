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
| CI-0001_QUALITY_GATE_AUTOMATION_DESIGN.md | GitHub Actions quality-gate automation contract | Complete / Verified |
| SAFE-0001_WORKSPACE_PATH_SAFETY_DESIGN.md | Workspace root, containment, link-escape, and controlled-error security contract/evidence | Complete / Verified |
| SAFE-0001_VERIFICATION_EVIDENCE.md | Compact Linux/Windows SAFE-0001 verification record | Complete / Verified |
| AUTO-0001_ENGINEERING_PROJECT_BOOTSTRAP_DESIGN.md | Additive engineering bootstrap API/profile/verification/CLI contract over SDK-0001 | Complete / Verified |
| AUTO-0001_VERIFICATION_EVIDENCE.md | Core API, CLI, installed-wheel, CI, and publication-boundary evidence | Complete / Verified |
| AUTO-0002_PROJECT_DOCUMENTATION_SYNCHRONIZATION_DESIGN.md | Bounded project-state inspection, documentation drift, deterministic planning, guarded apply, and verification contract | Design / Proposed |

## Active Engineering Work

| Area | Status |
|---|---|
| MCP-0002 evidence maintenance | COMPLETE |
| MCP-0003 Antigravity interoperability | VERIFIED |
| Official Python MCP SDK migration | COMPLETE |
| REL-0001 local distribution verification | COMPLETE / VERIFIED |
| CI-0001 quality gate automation | COMPLETE / VERIFIED |
| SAFE-0001 workspace path safety | COMPLETE / VERIFIED |
| REL-0002 v0.1.0 GitHub publication | COMPLETE / VERIFIED |
| AUTO-0001 engineering project bootstrap | COMPLETE / VERIFIED |
| AUTO-0002 project documentation synchronization | DESIGN / CURRENT PRIORITY |
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
| REL-0002 release publication governance and v0.1.0 GitHub publication | COMPLETE / VERIFIED |
| M3 / AUTO-0001 Engineering Project Bootstrap | COMPLETE / VERIFIED |
| M3 / AUTO-0002 Project Documentation Synchronization | DESIGN |
| Additional client and IDE interoperability | PLANNED |

## Published Release

- GitHub Release: `AI-Engineering 0.1.0`
- Tag: `v0.1.0`
- Tagged commit: `73929bd15fa7637db8162aac199697582bb25e67`
- AUTO-0001: completed after the immutable v0.1.0 tag; not part of that published artifact
- PyPI: not approved / not published

## Current Quality Baseline

- Current Linux GitHub Actions / Python 3.11: pytest 112 passed, Ruff 0 findings, mypy 0 findings in 71 source files.
- Installed-wheel verification covers both `ai-engineering project create` and `ai-engineering project bootstrap` outside the source checkout.
- Windows-local SAFE evidence: pytest 98 passed, 1 permitted symlink-fixture skip due to `WinError 1314`; Ruff 0; mypy 0.

## Source Tree

```text
src/ai_engineering/
├── discovery/   ├── git/       ├── ide/adapters/  ├── mcp/debug/
├── python/      ├── registry/  ├── runtime/       ├── shared/
├── stdio/       ├── tools/     └── workspace/
```

The repository has no `transport/` package.
