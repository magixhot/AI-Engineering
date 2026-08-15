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

AI-Engineering has completed and verified the documentation foundation, MCP-0002, MCP-0003, SDK-0001 Project Templates V1, SDK-0001.1 Standalone Python Project Scaffold, SDK-0001.2 Project Template CLI, TOOL-0001 Core Tool Operation Verification, REL-0001 Local Distribution Verification, CI-0001 Quality Gate Automation, and SAFE-0001 Workspace Path Safety Boundary for their approved scopes.

The installed `ai-engineering project create` command is verified. All 15 existing Workspace, Git, and Python operations have isolated service/registry/representative SDK-session coverage. VS Code 1.132.1 and Antigravity are verified only for their recorded MCP contracts.

Current Linux CI quality baseline is pytest **99 passed**, Ruff **0 findings**, and mypy **0 findings**. Windows-local SAFE verification recorded pytest **98 passed, 1 skipped**; the single skip is the symlink escape fixture because the Windows process lacked symlink-creation privilege (`WinError 1314`). Ruff and mypy are green on Windows as well.

REL-0001 verifies local wheel/sdist artifacts and isolated installed CLI behavior for release line 0.1.0. CI-0001 runs the full quality gates on GitHub Actions. SAFE-0001 enforces `MCPConfig.workspace_root` for active MCP Workspace handlers and rejects outside traversal, absolute-path escape, and link escape where the platform permits link-fixture verification.

GitHub Release creation and PyPI publishing remain unperformed and unclaimed. SAFE-0001 is a Workspace path-authorization boundary, not an OS-level sandbox or a Git/Python subprocess sandbox. ChatGPT/OpenAI, Claude Desktop, and other MCP clients remain unverified unless separately recorded.

## Engineering Guardrails

- Preserve originals.
- Extend, never replace.
- Documentation before implementation.
- Keep changes small, testable, and reviewable.
- Do not redesign existing architecture unless explicitly requested.
- Keep environment-specific absolute paths out of project code and documentation contracts.
- Make compatibility and security claims only from recorded evidence.

## Project Context

AI-Engineering is the Engineering MCP Server for the AI Infrastructure ecosystem. It uses the official Python MCP SDK at the protocol/server boundary while preserving the internal Runtime and Registry architecture.

Reference project: AI-Archive-Server.
