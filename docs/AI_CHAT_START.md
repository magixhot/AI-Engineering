# AI-Engineering

## Chat Bootstrap

For a new or continued session, restore context in this order:

1. README.md
2. PROJECT_CONTEXT.md
3. PROJECT_MAP.md
4. CURRENT_STATUS.md
5. ROADMAP.md
6. DECISIONS.md
7. CODING_STANDARDS.md
8. MASTER_INDEX.md

After reading them, continue from `CURRENT_STATUS.md` and the current roadmap.

## Current Working State

AI-Engineering has completed the documentation foundation, MCP-0002, MCP-0003, SDK-0001 Project
Templates V1, the optional SDK-0001.1 Standalone Python Project Scaffold, SDK-0001.2 Project
Template CLI, and TOOL-0001 Core Tool Operation Verification. The `ai-engineering project create`
console command is implemented and verified, and TOOL-0001 has verified all 15 existing Workspace,
Git, and Python operations. The official MCP SDK migration, VS Code 1.132.1 interoperability
verification, and the recorded Antigravity stdio interoperability verification are complete. Current
quality gates are green: pytest has 89 passing tests, Ruff has 0 findings, and mypy has 0 findings.
The canonical project state is ready for next-milestone selection and REL planning; no
release-hardening implementation has started. Quality and documentation claims must remain
evidence-based. ChatGPT/OpenAI, Claude Desktop, and other MCP clients are not verified or claimed
compatible.

## Engineering Guardrails

- Preserve originals.
- Extend, never replace.
- Documentation before implementation.
- Keep changes small, testable, and reviewable.
- Do not redesign existing architecture unless explicitly requested.

## Project Context

AI-Engineering is the Engineering MCP Server for the AI Infrastructure ecosystem. It uses the
official Python MCP SDK at the protocol/server boundary while preserving the internal Runtime and
Registry architecture.

Reference project: AI-Archive-Server.
