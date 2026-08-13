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

AI-Engineering is beyond Sprint 0. The documentation foundation is complete; the Engineering MCP
Server and its MCP Foundation are implemented and are in SDK migration and stabilization work.
The current priority is documentation and architecture-state synchronization, followed by evidence-
based MCP client interoperability verification.

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
