# AI-Engineering — Current Status

**Snapshot date:** 2026-08-15
**Status:** ACTIVE
**Release line:** 0.1.0
**Current phase:** AUTO-0001 Complete / Verified — Engineering Project Bootstrap

## State by Delivery Area

| Area | State | Evidence in repository |
|---|---|---|
| Sprint 0 — Documentation Foundation | COMPLETED | Core project documents exist and are maintained. |
| Sprint 1 — MCP Foundation | IMPLEMENTED / VERIFIED | MCP bootstrap, SDK adapter, registry integration, STDIO entry point, and diagnostics are covered by MCP-0002 evidence. |
| Official Python MCP SDK migration | COMPLETE | `mcp` is a project dependency; the SDK bootstrap and adapter are implemented and verified by MCP-0002. |
| Workspace, Git, and Python tools | IMPLEMENTED / VERIFIED | All 15 registered operations have isolated service/registry/representative SDK-session verification. |
| Client interoperability | VS CODE AND ANTIGRAVITY VERIFIED | VS Code 1.132.1 and Antigravity are specifically verified for their recorded contracts; other client categories remain unverified and are not claimed. |
| MCP-0003 Antigravity interoperability | VERIFIED | The current stdio server completed connection, 15-tool discovery, successful safe/workspace calls, and a controlled missing-file error after the snake_case dispatch fix. |
| SDK-0001 Project Templates V1 | COMPLETE / VERIFIED | The document-first standalone template API and Git safety behavior are covered by template tests. |
| SDK-0001.1 Standalone Python Project Scaffold | COMPLETE / VERIFIED | The opt-in scaffold generates packaging, source, and smoke-test files while preserving V1 output by default. |
| SDK-0001.2 Project Template CLI | COMPLETE / VERIFIED | `ai-engineering project create` is an installed console-script frontend over the public template API, with V1/scaffold, stdout/stderr, and exit-code behavior verified. |
| TOOL-0001 Core Tool Operation Verification | COMPLETE / VERIFIED | All 15 existing Workspace, Git, and Python operations have isolated service/registry/representative SDK-session verification. |
| REL-0001 Local Distribution Verification | COMPLETE / VERIFIED | Wheel and sdist artifact policy, isolated wheel install, installed metadata/import, and installed CLI smoke are verified. |
| CI-0001 Quality Gate Automation | COMPLETE / VERIFIED | GitHub Actions covers Ruff, mypy, full pytest, and REL-0001 on Linux/Python 3.11 with successful PR and post-merge runs. |
| SAFE-0001 Workspace Path Safety Boundary | COMPLETE / VERIFIED | Active MCP Workspace handlers enforce `MCPConfig.workspace_root`; outside traversal/absolute/link escapes are rejected; Linux CI and Windows-local verification are recorded. |
| REL-0002 Release Publication | COMPLETE / VERIFIED | Tag `v0.1.0` points to approved commit `73929bd15fa7637db8162aac199697582bb25e67`; GitHub Release `AI-Engineering 0.1.0` is published. PyPI remains not approved/not published. |
| AUTO-0001 Engineering Project Bootstrap | COMPLETE / VERIFIED | Typed `python-engineering` bootstrap API, fail-closed verification, additive installed CLI command, and isolated-wheel bootstrap smoke are verified. |
| Quality gates | PASS | Current Linux CI: pytest 112 passed, Ruff 0, mypy 0 in 71 source files. Windows-local SAFE evidence remains pytest 98 passed / 1 permitted symlink-fixture skip, Ruff 0, mypy 0. |

## Current Priorities

1. Preserve the verified AUTO-0001 API/CLI and installed-distribution contract without changing SDK-0001 default behavior.
2. Preserve the published `v0.1.0` release evidence and the verified SAFE-0001, CI-0001, REL-0001/0002, MCP-0002/0003, and SDK-0001 contracts.
3. Keep PyPI and future release publication behind separate explicit approval decisions.
4. Preserve the verified MCP Workspace root boundary without expanding it implicitly to Git/Python subprocess semantics.
5. Select the next engineering milestone from a fresh post-AUTO-0001 roadmap audit.

## Implemented Baseline

The current `master` baseline includes the official Python MCP SDK boundary, 15 registered tool operations, SDK project template/scaffold/create CLI, AUTO-0001 engineering bootstrap API and CLI, local wheel/sdist verification, automated GitHub Actions quality gates, and a fail-closed MCP Workspace path boundary rooted at `MCPConfig.workspace_root`.

AUTO-0001 V1 has exactly one profile, `python-engineering`. It delegates project creation to the existing SDK-0001 public API, verifies the generated project read-only, and exposes the same workflow through installed `ai-engineering project bootstrap`. The isolated-wheel release test proves the installed command works outside the source checkout with no editable-install or `PYTHONPATH` reliance.

Git tag `v0.1.0` and GitHub Release `AI-Engineering 0.1.0` remain verified historical publication evidence for commit `73929bd15fa7637db8162aac199697582bb25e67`. AUTO-0001 was implemented after that immutable tag and is not retroactively part of the published v0.1.0 artifact. PyPI remains not approved and not published.

## Active Work

MCP-0002, MCP-0003, SDK-0001 V1/1.1/1.2, TOOL-0001, REL-0001, CI-0001, SAFE-0001, REL-0002, and AUTO-0001 are complete and verified for their approved scopes.

## Planned Work

The next milestone is intentionally not preselected. Additional engineering automation, project synchronization/update behavior, additional client/IDE interoperability, PyPI/publication expansion, and future cross-tool security boundaries remain planned until separately scoped and validated.
