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
| MCP_SDK_AUDIT.md | SDK integration audit record | Active / stabilization update needed |
| MCP_SDK_MIGRATION_REPORT.md | SDK migration evidence and open verification | Active |
| MCP_DIAGNOSTICS.md | MCP diagnostics operation | Active |
| STABILIZATION_PLAN.md | Historical stabilization plan | Active / historical context |
| RELEASE_CHECKLIST.md | 0.1.0 release checklist | Active |
| SDK-0001_TEMPLATE_DESIGN.md | SDK-0001 authoritative template design | Active |
| SDK-0001_PROJECT_TEMPLATES.md | SDK-0001 framework reference | Active |

## Active Engineering Work

| Area | Status |
|---|---|
| Documentation and architecture-state synchronization | CURRENT PRIORITY |
| Official Python MCP SDK migration | ACTIVE / STABILIZATION |
| MCP client interoperability verification | PLANNED / VERIFICATION |
| Diagnostics maintenance | ACTIVE |

## Delivery State

| Sprint / Area | Status |
|---|---|
| Sprint 0 — Documentation Foundation | COMPLETED |
| Sprint 1 — MCP Foundation | IMPLEMENTED / STABILIZATION |
| Workspace, Git, and Python tool subsystems | IMPLEMENTED |
| Engineering automation | PLANNED |
| Additional client and IDE interoperability | PLANNED |

## Source Tree

```text
src/ai_engineering/
├── discovery/   ├── git/       ├── ide/adapters/  ├── mcp/debug/
├── python/      ├── registry/  ├── runtime/       ├── shared/
├── stdio/       ├── tools/     └── workspace/
```

The repository has no `transport/` package.
