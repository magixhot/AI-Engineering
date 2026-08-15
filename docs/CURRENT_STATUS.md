# AI-Engineering — Current Status

**Snapshot date:** 2026-08-15
**Status:** ACTIVE
**Release line:** 0.2.0 candidate / ready for publication approval / not published
**Current phase:** REL-0003-02 — Release Readiness Complete

## State by Delivery Area

| Area | State | Evidence in repository |
|---|---|---|
| Sprint 0 — Documentation Foundation | COMPLETED | Core project documents exist and are maintained. |
| Sprint 1 — MCP Foundation | IMPLEMENTED / VERIFIED | MCP bootstrap, SDK adapter, registry integration, STDIO entry point, and diagnostics are covered by MCP-0002 evidence. |
| Official Python MCP SDK migration | COMPLETE | `mcp` is a project dependency; the SDK bootstrap and adapter are implemented and verified by MCP-0002. |
| Workspace, Git, and Python tools | IMPLEMENTED / VERIFIED | All 15 registered operations have isolated service/registry/representative SDK-session verification. |
| Client interoperability | VS CODE AND ANTIGRAVITY VERIFIED | VS Code 1.132.1 and Antigravity are specifically verified for their recorded contracts; other client categories remain unverified and are not claimed. |
| SDK-0001 Project Templates V1 / Python Scaffold / CLI | COMPLETE / VERIFIED | Standalone templates, optional Python scaffold, and installed `ai-engineering project create` behavior are verified. |
| TOOL-0001 Core Tool Operation Verification | COMPLETE / VERIFIED | All 15 existing Workspace, Git, and Python operations have isolated service/registry/representative SDK-session verification. |
| REL-0001 Local Distribution Verification | COMPLETE / VERIFIED | Wheel/sdist contents, isolated wheel install, installed metadata/import, and installed CLI behavior are verified. |
| CI-0001 Quality Gate Automation | COMPLETE / VERIFIED | GitHub Actions covers Ruff, mypy, full pytest, and REL-0001 on Linux/Python 3.11. |
| SAFE-0001 Workspace Path Safety Boundary | COMPLETE / VERIFIED | Active MCP Workspace handlers enforce `MCPConfig.workspace_root` with verified traversal/absolute/link escape rejection. |
| SAFE-0002 Git/Python Execution Safety | COMPLETE / VERIFIED | Active MCP Git and path-taking Python operations are bound to `MCPConfig.workspace_root`; Git parent-repository escape, Python outside/traversal/link escape, and unsafe pytest target execution are rejected under the approved V1 contract. |
| REL-0002 Release Publication | COMPLETE / VERIFIED | Tag `v0.1.0` and GitHub Release `AI-Engineering 0.1.0` are published for approved commit `73929bd15fa7637db8162aac199697582bb25e67`; PyPI is not published. |
| REL-0003 Next Release Line | READY FOR PUBLICATION APPROVAL / NOT PUBLISHED | Version `0.2.0` is approved; exact candidate SHA `1faf14c121b7b5da7c8781e3de4e836f85838a76` has fresh Linux CI, Windows, and distribution evidence. No `v0.2.0` tag, GitHub Release, asset upload, or PyPI publication has occurred. |
| AUTO-0001 Engineering Project Bootstrap | COMPLETE / VERIFIED | Typed bootstrap API, fail-closed verification, installed bootstrap CLI, and isolated-wheel smoke are verified. |
| AUTO-0002 Project Documentation Synchronization | COMPLETE / VERIFIED | Read-only inspection, bounded drift detection/planning, SHA-256 guarded apply, ownership preservation, installed `project docs check/plan/apply`, and isolated-wheel verification are complete. |
| Quality gates | PASS / FRESH 0.2.0 CANDIDATE EVIDENCE | Exact candidate passed GitHub Actions Quality #79. Windows-local candidate evidence: pytest 153 passed / 2 permitted symlink-fixture skips, Ruff 0, mypy 0 in 79 source files, release test 1 passed, `git diff --check` passed, working tree clean. |

## Current Priorities

1. Preserve exact 0.2.0 artifact/tag candidate SHA `1faf14c121b7b5da7c8781e3de4e836f85838a76` unless a release-affecting change explicitly invalidates it.
2. Preserve SAFE-0002 and AUTO-0002 boundaries exactly; release publication must not add functionality.
3. Use `docs/REL-0003_0.2.0_RELEASE_READINESS.md` and `docs/REL-0003_0.2.0_RELEASE_NOTES.md` as the publication preparation record.
4. Stop for explicit approval before creating `v0.2.0`, creating a GitHub Release, or uploading release assets.
5. Keep PyPI explicitly not approved/not published.

## Implemented Baseline

The 0.2.0 candidate includes the official Python MCP SDK boundary, 15 registered tool operations, SDK project creation/scaffold CLI, AUTO-0001 project bootstrap, AUTO-0002 deterministic documentation synchronization, local wheel/sdist verification, automated GitHub Actions quality gates, SAFE-0001 Workspace path authorization, and SAFE-0002 active-MCP Git/Python execution safety.

SAFE-0002 makes `MCPConfig.workspace_root` the authority root for active MCP Git and path-taking Python operations. Bounded Git requires the configured root to be the Git repository top level. Bounded Python authorizes syntax/package/test targets by resolved ancestry before outside inspection or execution; pytest uses the current interpreter, workspace-root cwd, no shell, closed stdin, captured output, and a bounded timeout. The boundary does not sandbox malicious code already authorized to run inside the workspace.

AUTO-0002 V1 inspects local project state, reports drift for exactly `CURRENT_STATUS.md`, `MASTER_INDEX.md`, and `PROJECT_MAP.md`, builds deterministic replacement plans with SHA-256 original-content guards, and applies only ownership-marker-bounded changes. Missing or malformed markers require manual review. The installed CLI exposes `ai-engineering project docs check`, `plan`, and `apply`; `check` and `plan` are read-only, while `apply` refuses partial mutation when manual review is required.

REL-0003 selected version `0.2.0` and froze exact artifact/tag candidate SHA `1faf14c121b7b5da7c8781e3de4e836f85838a76` after the version-consistent changes were merged to canonical `master`. Candidate preparation PR #55 passed Quality #78; the exact candidate passed post-merge Quality #79. Fresh Windows-local verification passed with 153 tests and two previously classified privilege-dependent symlink fixture skips; the release distribution test also passed separately.

Git tag `v0.1.0` and GitHub Release `AI-Engineering 0.1.0` remain immutable historical publication evidence for commit `73929bd15fa7637db8162aac199697582bb25e67`. The 0.2.0 candidate is not published until separately approved. PyPI remains not approved and not published.

## Active Work

REL-0003-02 readiness verification is complete. The only remaining REL-0003 action is a separate publication decision/action for the approved GitHub surface. MCP-0002, MCP-0003, SDK-0001 V1/1.1/1.2, TOOL-0001, REL-0001, CI-0001, SAFE-0001, SAFE-0002, REL-0002, AUTO-0001, and AUTO-0002 remain complete and verified for their approved scopes.

## Planned Work

If publication is approved, create `v0.2.0` at the exact candidate SHA, create the GitHub Release using the prepared notes, and upload only the approved verified assets. PyPI remains excluded. After publication/reconciliation, select the next engineering milestone separately.
