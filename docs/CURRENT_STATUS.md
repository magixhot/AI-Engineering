# AI-Engineering — Current Status

**Snapshot date:** 2026-08-16
**Status:** ACTIVE
**Release line:** 0.2.0 published
**Current phase:** AUTO-0005 Complete / Verified

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
| SAFE-0002 Git/Python Execution Safety | COMPLETE / VERIFIED | Active MCP Git and path-taking Python operations are bound to `MCPConfig.workspace_root`; approved path and subprocess boundaries remain verified. |
| REL-0002 Release Publication | COMPLETE / VERIFIED | Historical tag `v0.1.0` and GitHub Release `AI-Engineering 0.1.0` remain preserved. |
| REL-0003 0.2.0 Release | COMPLETE / VERIFIED | Tag `v0.2.0` targets `1faf14c121b7b5da7c8781e3de4e836f85838a76`; GitHub Release `AI-Engineering 0.2.0` is published with verified wheel/sdist assets. PyPI is not published. |
| AUTO-0001 Engineering Project Bootstrap | COMPLETE / VERIFIED | Typed bootstrap API, fail-closed verification, installed bootstrap CLI, and isolated-wheel smoke are verified. |
| AUTO-0002 Project Documentation Synchronization | COMPLETE / VERIFIED | Read-only inspection, bounded drift detection/planning, SHA-256 guarded apply, ownership preservation, installed `project docs check/plan/apply`, and isolated-wheel verification are complete. |
| AUTO-0003 Documentation Ownership Initialization | COMPLETE / VERIFIED | Ownership classification/planning, guarded atomic apply, AUTO-0002 handoff, idempotency, Git invariants, installed ownership CLI, and isolated-wheel verification are complete. Evidence: `AUTO-0003_VERIFICATION_EVIDENCE.md`. |
| AUTO-0004 Engineering Project Update / Migration Framework | COMPLETE / VERIFIED | Positive project identity, explicit migration registry, deterministic planning, SHA-256 guards, guarded atomic apply/rollback, Git invariants, installed migration CLI, and isolated-wheel verification are complete. Evidence: `AUTO-0004_VERIFICATION_EVIDENCE.md`. |
| AUTO-0005 Python Engineering Baseline V2 / First Production Migration | COMPLETE / VERIFIED | New engineering bootstraps use `python-engineering-v2`; dual V1/V2 identity and the registered `python-engineering-v1-to-v2` edge are verified through the installed public CLI. Evidence: `AUTO-0005_VERIFICATION_EVIDENCE.md`. |
| Quality gates | PASS | AUTO-0005 design #113/#114; V2 bootstrap corrected #120/#121; production edge corrected #123/#124; installed-wheel migration #125/#126. |

## Current Priorities

1. Preserve the published `v0.2.0` release and its exact tag target.
2. Preserve SAFE-0001/SAFE-0002 and AUTO-0001 through AUTO-0005 boundaries unless separately redesigned.
3. Keep PyPI explicitly not approved/not published.
4. Select the next engineering milestone from a fresh post-AUTO-0005 roadmap audit.

## Implemented Baseline

The verified baseline includes the official Python MCP SDK boundary, 15 registered tool operations, SDK project creation/scaffold CLI, engineering bootstrap, documentation ownership/synchronization, the guarded project migration framework, the production `python-engineering-v2` baseline and first V1-to-V2 migration edge, local distribution verification, automated GitHub Actions quality gates, and the approved workspace/Git/Python safety boundaries.

AUTO-0005 extends AUTO-0004 with positive dual V1/V2 identity and exactly one approved production edge, `python-engineering-v1-to-v2`. New `python-engineering` bootstraps create the V2 identity marker `.ai-engineering.toml` and the V2 `.gitignore` in the same initial commit. Generic SDK-0001/SDK-0001.1 project generation remains separate from that engineering profile behavior.

The production `DEFAULT_MIGRATION_REGISTRY` now contains exactly the approved V1-to-V2 edge. Its migration operations are bounded to creation of `.ai-engineering.toml` and exact machine-owned replacement of `.gitignore`. Re-running the same edge against its exact target baseline is an idempotent no-op; unsupported migration ids and unrelated baselines still fail closed.

Installed distribution verification exercises the real public `project migrate check|plan|apply` path from a legacy V1 project through V2 and verifies Git HEAD/index invariants.

REL-0003 published version `0.2.0` to GitHub. The immutable tag `v0.2.0` points to exact candidate SHA `1faf14c121b7b5da7c8781e3de4e836f85838a76`. Post-release engineering commits do not change the published artifact/tag target. No TestPyPI or PyPI publication occurred.

## Active Work

AUTO-0005 is complete and verified for its approved scope. MCP-0002, MCP-0003, SDK-0001 V1/1.1/1.2, TOOL-0001, REL-0001, CI-0001, SAFE-0001, SAFE-0002, REL-0002, REL-0003, AUTO-0001, AUTO-0002, AUTO-0003, AUTO-0004, and AUTO-0005 remain complete and verified for their approved scopes.

## Planned Work

The next milestone is intentionally not preselected. Additional bootstrap profiles, additional production migration edges, additional client/IDE interoperability, new bounded execution tools, publication expansion, and additional engineering automation remain separately scoped work.
