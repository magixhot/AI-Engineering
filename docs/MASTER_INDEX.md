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
| RELEASE_CHECKLIST.md | 0.1.0 release checklist | Active |
| SDK-0001_TEMPLATE_DESIGN.md | SDK-0001 V1 authoritative template design | Implemented / verified |
| SDK-0001_PROJECT_TEMPLATES.md | SDK-0001 V1 framework reference | Implemented / verified |
| SDK-0001_1_PYTHON_SCAFFOLD_DESIGN.md | SDK-0001.1 Python scaffold contract | Implemented / verified |
| SDK-0001_2_PROJECT_TEMPLATE_CLI_DESIGN.md | SDK-0001.2 Project Template CLI contract | Implemented / verified |
| TOOL-0001_CORE_TOOL_OPERATION_VERIFICATION_DESIGN.md | Core Workspace, Git, and Python tool-operation verification contract | Complete / Verified |
| REL-0001_DISTRIBUTION_AND_RELEASE_VERIFICATION_DESIGN.md | Distribution and release verification contract | Complete / Verified |
| CI-0001_QUALITY_GATE_AUTOMATION_DESIGN.md | GitHub Actions quality-gate automation contract | Complete / Verified |

## Active Engineering Work

| Area | Status |
|---|---|
| MCP-0002 evidence maintenance | COMPLETE |
| MCP-0003 Antigravity interoperability | VERIFIED |
| Official Python MCP SDK migration | COMPLETE |
| REL-0001 local distribution verification | COMPLETE / VERIFIED |
| CI-0001 quality gate automation | COMPLETE / VERIFIED |
| Next engineering milestone preparation | CURRENT PRIORITY |
| Additional MCP client interoperability | OPTIONAL / FUTURE EVIDENCE |
| Diagnostics maintenance | ACTIVE |

## Delivery State

| Sprint / Area | Status |
|---|---|
| Sprint 0 — Documentation Foundation | COMPLETED |
| Sprint 1 — MCP Foundation | IMPLEMENTED / VERIFIED |
| Workspace, Git, and Python tool subsystems | IMPLEMENTED |
| SDK-0001 Project Templates V1 | IMPLEMENTED / VERIFIED |
| SDK-0001.1 Standalone Python Project Scaffold | COMPLETE / VERIFIED |
| SDK-0001.2 Project Template CLI | COMPLETE / VERIFIED |
| Antigravity MCP interoperability | VERIFIED |
| REL-0001 local distribution verification | COMPLETE / VERIFIED |
| CI-0001 quality gate automation | COMPLETE / VERIFIED |
| Additional client and IDE interoperability | PLANNED |

## Source Tree

```text
src/ai_engineering/
├── discovery/   ├── git/       ├── ide/adapters/  ├── mcp/debug/
├── python/      ├── registry/  ├── runtime/       ├── shared/
├── stdio/       ├── tools/     └── workspace/
```

The repository has no `transport/` package.
