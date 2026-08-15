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

AI-Engineering has completed and verified the documentation foundation, MCP-0002, MCP-0003, SDK-0001 Project Templates V1, SDK-0001.1 Standalone Python Project Scaffold, SDK-0001.2 Project Template CLI, TOOL-0001 Core Tool Operation Verification, REL-0001 Local Distribution Verification, CI-0001 Quality Gate Automation, SAFE-0001 Workspace Path Safety Boundary, REL-0002 GitHub publication governance, AUTO-0001 Engineering Project Bootstrap, AUTO-0002 Project Documentation Synchronization, and SAFE-0002 Git/Python Execution Safety for their approved scopes.

The installed `ai-engineering` console script verifies three bounded project workflows: `project create`, `project bootstrap`, and AUTO-0002 `project docs check/plan/apply`. AUTO-0002 V1 inspects project state locally, detects drift only for `CURRENT_STATUS.md`, `MASTER_INDEX.md`, and `PROJECT_MAP.md`, builds deterministic plans with SHA-256 original-content guards, and applies only valid machine-owned marked sections. Missing or malformed markers require manual review; marker initialization is not part of V1.

SAFE-0002 makes `MCPConfig.workspace_root` the active MCP authority root for Git and path-taking Python operations. Git operations require the configured root to be the repository top level; Python syntax/package/test targets must remain inside the resolved root. Authorized pytest execution uses the current interpreter, workspace-root cwd, no shell, closed stdin, captured output, and a bounded timeout. SAFE-0002 does not sandbox malicious code already authorized to execute inside the workspace.

Current Linux CI quality baseline is pytest **155 passed**, Ruff **0 findings**, and mypy **0 findings in 79 source files**. The release/distribution test builds wheel and sdist, installs the wheel into a fresh external virtual environment, verifies package isolation and metadata, and executes installed create, bootstrap, and documentation synchronization workflows outside the source checkout.

Final Windows-local SAFE-0002 evidence is pytest **153 passed, 2 skipped**; both skips are symlink fixtures that the Windows process could not create because of `WinError 1314`. Ruff and mypy were green, `git diff --check` passed, and the working tree was clean. Equivalent link-escape coverage executes in Linux CI.

The Windows verification also exposed and resolved one AUTO-0002 test-portability defect: a preservation assertion assumed LF even though production intentionally preserves the document's existing LF/CRLF convention. Production behavior was unchanged; the test was made line-ending-neutral while dedicated CRLF-preservation coverage remained.

Git tag `v0.1.0` and GitHub Release `AI-Engineering 0.1.0` are published for commit `73929bd15fa7637db8162aac199697582bb25e67`. AUTO-0001, AUTO-0002, and SAFE-0002 were completed after that immutable tag and must not be described as part of the published v0.1.0 artifact. PyPI remains not approved and not published.

SAFE-0001 is a Workspace path-authorization boundary. SAFE-0002 is an active-MCP Git/Python authority-root and subprocess-construction boundary. Neither is an OS-level sandbox. ChatGPT/OpenAI, Claude Desktop, and other MCP clients remain unverified unless separately recorded.

## Engineering Guardrails

- Preserve originals.
- Extend, never replace.
- Documentation before implementation.
- Keep changes small, testable, and reviewable.
- Do not redesign existing architecture unless explicitly requested.
- Keep environment-specific absolute paths out of project code and documentation contracts.
- Make compatibility and security claims only from recorded evidence.
- Treat published tags/releases as immutable historical evidence; post-release `master` work does not retroactively change them.
- Do not expand AUTO-0002 writable documents or initialize ownership markers without a separate approved contract.
- Do not expand SAFE-0002 claims to OS sandboxing, arbitrary-command containment, or future Git/Python tools without a separate contract and evidence.

## Project Context

AI-Engineering is the Engineering MCP Server and engineering-automation foundation for the AI Infrastructure ecosystem. It uses the official Python MCP SDK at the protocol/server boundary while preserving the internal Runtime and Registry architecture.

Reference project: AI-Archive-Server.
