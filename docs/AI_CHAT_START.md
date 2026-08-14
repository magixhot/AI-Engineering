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

AI-Engineering has completed the documentation foundation, MCP-0002, SDK-0001 Project Templates
V1, the optional SDK-0001.1 Standalone Python Project Scaffold, and SDK-0001.2 Project Template
CLI. The `ai-engineering project create` console command is implemented and verified. The official
MCP SDK migration and VS Code 1.132.1 interoperability verification are complete. Current quality
gates are green: pytest has 54 passing tests, and Ruff and mypy have no findings. The next milestone
requires explicit selection; quality and documentation claims must remain evidence-based. Other MCP
clients are not verified or claimed compatible.

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
