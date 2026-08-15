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

AI-Engineering has completed and verified the documentation foundation, MCP-0002, MCP-0003, SDK-0001 Project Templates V1, SDK-0001.1 Standalone Python Project Scaffold, SDK-0001.2 Project Template CLI, TOOL-0001 Core Tool Operation Verification, REL-0001 Local Distribution Verification, CI-0001 Quality Gate Automation, SAFE-0001 Workspace Path Safety Boundary, REL-0002 GitHub publication governance, and AUTO-0001 Engineering Project Bootstrap for their approved scopes.

The installed `ai-engineering project create` and `ai-engineering project bootstrap` commands are verified. AUTO-0001 V1 exposes the single exact profile `python-engineering`, delegates generation to the existing SDK-0001 public API, and performs fail-closed read-only post-generation verification. All 15 existing Workspace, Git, and Python operations retain isolated service/registry/representative SDK-session coverage. VS Code 1.132.1 and Antigravity are verified only for their recorded MCP contracts.

Current Linux CI quality baseline is pytest **112 passed**, Ruff **0 findings**, and mypy **0 findings**. The release/distribution test builds the wheel and sdist, installs the wheel into a fresh external virtual environment, verifies package isolation and metadata, and now executes both installed project-create and engineering-bootstrap smoke workflows outside the source checkout.

Windows-local SAFE verification remains pytest **98 passed, 1 skipped**; the single skip is the symlink escape fixture because the Windows process lacked symlink-creation privilege (`WinError 1314`). Ruff and mypy were green for that Windows evidence.

Git tag `v0.1.0` and GitHub Release `AI-Engineering 0.1.0` are published for commit `73929bd15fa7637db8162aac199697582bb25e67`. AUTO-0001 was completed after that immutable tag and must not be described as part of the published v0.1.0 artifact. PyPI remains not approved and not published.

SAFE-0001 is a Workspace path-authorization boundary, not an OS-level sandbox or a Git/Python subprocess sandbox. ChatGPT/OpenAI, Claude Desktop, and other MCP clients remain unverified unless separately recorded.

## Engineering Guardrails

- Preserve originals.
- Extend, never replace.
- Documentation before implementation.
- Keep changes small, testable, and reviewable.
- Do not redesign existing architecture unless explicitly requested.
- Keep environment-specific absolute paths out of project code and documentation contracts.
- Make compatibility and security claims only from recorded evidence.
- Treat published tags/releases as immutable historical evidence; post-release `master` work does not retroactively change them.

## Project Context

AI-Engineering is the Engineering MCP Server and engineering-automation foundation for the AI Infrastructure ecosystem. It uses the official Python MCP SDK at the protocol/server boundary while preserving the internal Runtime and Registry architecture.

Reference project: AI-Archive-Server.
