# AI-Engineering 0.1.0 — Draft Release Notes

**Status:** DRAFT / NOT PUBLISHED

AI-Engineering 0.1.0 establishes the first verified engineering baseline for the repository.

## Highlights

- Official Python MCP SDK integration for the stdio/server boundary.
- Registered Workspace, Git, and Python engineering tools with verified dispatch and operation coverage.
- Project Templates V1 with an optional standalone Python scaffold.
- Installed `ai-engineering project create` CLI.
- Verified local wheel and sdist distribution artifacts with isolated wheel installation.
- GitHub Actions quality gates for Ruff, mypy, and the full pytest suite.
- MCP Workspace path-safety boundary rooted at `MCPConfig.workspace_root`.

## MCP and Tooling

The server uses the official Python MCP SDK for the active stdio path while preserving the internal
registry/runtime architecture. VS Code 1.132.1 and Antigravity are verified for their specifically
recorded interoperability contracts.

All 15 current Workspace, Git, and Python tools have isolated operation coverage plus registry and
representative SDK-session verification. The release line also includes repairs for snake_case MCP
tool dispatch and Git porcelain status-column preservation.

## Project Bootstrap

SDK-0001 provides a document-first project-template API. The optional SDK-0001.1 scaffold adds a
generic Python package/test baseline without changing the default V1 output. SDK-0001.2 exposes the
same public API through the installed `ai-engineering project create` command.

## Distribution

REL-0001 verifies:

- wheel and sdist construction;
- artifact-content policy;
- isolated wheel installation outside the source checkout;
- installed package metadata and version;
- the `ai-engineering` console entry point;
- installed project-create smoke behavior.

Expected 0.1.0 artifacts are the `ai_engineering-0.1.0` wheel and sdist produced from the approved
release commit.

## Quality and Safety

CI-0001 runs the repository quality gates on Linux/Python 3.11. The current candidate baseline has
99 passing tests with Ruff and mypy passing.

SAFE-0001 bounds MCP-exposed Workspace operations to `MCPConfig.workspace_root`. Relative and
absolute in-root access remain supported while traversal, outside-root targets, link-based escapes,
and root move/delete attempts are rejected according to the documented contract.

## Compatibility Scope

Verified MCP clients are limited to the recorded VS Code 1.132.1 and Antigravity contracts.
Compatibility with ChatGPT/OpenAI, Claude Desktop, and other clients is not claimed by this release.

SAFE-0001 is a Workspace path-authorization boundary, not an operating-system sandbox and not a
sandbox for Git/Python subprocess behavior.

## Publication Scope

This draft is prepared for a possible GitHub tag/release only. PyPI publication is not approved.

Candidate tag: `v0.1.0`

Candidate commit: `73929bd15fa7637db8162aac199697582bb25e67`
