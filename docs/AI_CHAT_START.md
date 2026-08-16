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

AI-Engineering has completed and verified the documentation foundation, MCP-0002, MCP-0003, SDK-0001 Project Templates V1, SDK-0001.1 Standalone Python Project Scaffold, SDK-0001.2 Project Template CLI, TOOL-0001 Core Tool Operation Verification, REL-0001 Local Distribution Verification, CI-0001 Quality Gate Automation, SAFE-0001 Workspace Path Safety Boundary, SAFE-0002 Git/Python Execution Safety, REL-0002 publication governance, REL-0003 v0.2.0 GitHub publication, AUTO-0001 Engineering Project Bootstrap, AUTO-0002 Project Documentation Synchronization, and AUTO-0003 Documentation Ownership Initialization for their approved scopes.

The installed `ai-engineering` console script provides bounded project creation/bootstrap plus two separate documentation workflows. AUTO-0002 exposes `project docs check/plan/apply` for deterministic synchronization of the machine-owned sections in exactly `CURRENT_STATUS.md`, `MASTER_INDEX.md`, and `PROJECT_MAP.md`. AUTO-0003 exposes `project docs ownership check/plan/apply` to initialize those ownership sections only when the approved marker pair is completely absent and deterministic initialization is safe.

AUTO-0003 preserves human-authored content outside the insertion boundary, preserves LF/CRLF convention, uses SHA-256 stale-plan guards, verifies AUTO-0002 handoff and idempotency, and leaves Git HEAD/index unchanged. Partial, duplicate, malformed, unsupported, missing-document, mixed-newline, and stale-plan states fail closed. AUTO-0002 itself still never initializes markers implicitly.

SAFE-0002 makes `MCPConfig.workspace_root` the active MCP authority root for Git and path-taking Python operations. Git operations require the configured root to be the repository top level; Python syntax/package/test targets must remain inside the resolved root. Authorized pytest execution uses the current interpreter, workspace-root cwd, no shell, closed stdin, captured output, and a bounded timeout. SAFE-0002 does not sandbox malicious code already authorized to execute inside the workspace.

Current Linux CI baseline after AUTO-0003 is Quality #94 on `master` commit `a3a8716f861e568d0444f49aebc5c0ea6c7c4fc9`: pytest **174 passed**, Ruff **0 findings**, and mypy **0 issues in 83 source files**. Distribution verification builds wheel and sdist, installs the wheel into fresh external virtual environments, and executes installed create, bootstrap, AUTO-0002 synchronization, and AUTO-0003 ownership workflows outside the source checkout.

The published release is `v0.2.0` / `AI-Engineering 0.2.0`, targeting immutable candidate `1faf14c121b7b5da7c8781e3de4e836f85838a76` with approved wheel/sdist assets. AUTO-0003 was completed later on `master` and is not retroactively part of the published v0.2.0 artifact. Historical `v0.1.0` remains preserved. PyPI remains not approved and not published.

SAFE-0001 is a Workspace path-authorization boundary. SAFE-0002 is an active-MCP Git/Python authority-root and subprocess-construction boundary. Neither is an OS-level sandbox. ChatGPT/OpenAI, Claude Desktop, and other MCP clients remain unverified unless separately recorded.

## Engineering Guardrails

- Preserve originals.
- Extend, never replace.
- Documentation before implementation.
- Keep changes small, testable, and reviewable.
- Do not redesign existing architecture without a separate approved contract.
- Keep environment-specific absolute paths out of project code and documentation contracts.
- Make compatibility and security claims only from recorded evidence.
- Treat published tags/releases as immutable historical evidence; post-release `master` work does not retroactively change them.
- Do not expand AUTO-0002/AUTO-0003 writable documents or ownership semantics without a separate approved contract.
- Do not expand SAFE-0002 claims to OS sandboxing, arbitrary-command containment, or future Git/Python tools without a separate contract and evidence.

## Project Context

AI-Engineering is the Engineering MCP Server and engineering-automation foundation for the AI Infrastructure ecosystem. It uses the official Python MCP SDK at the protocol/server boundary while preserving the internal Runtime and Registry architecture.

Reference project: AI-Archive-Server.
