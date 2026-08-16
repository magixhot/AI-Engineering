# AI-Engineering — Current Status

**Snapshot date:** 2026-08-16  
**Status:** ACTIVE  
**Release line:** 0.2.0 published  
**Current phase:** AUTO-0007 — Engineering Project Reconciliation Plan

## State by Delivery Area

| Area | State | Evidence in repository |
|---|---|---|
| Sprint 0 — Documentation Foundation | COMPLETED | Core project documents exist and are maintained. |
| Sprint 1 — MCP Foundation | IMPLEMENTED / VERIFIED | MCP bootstrap, SDK adapter, registry integration, STDIO entry point, and diagnostics are covered by MCP-0002 evidence. |
| Official Python MCP SDK migration | COMPLETE | `mcp` is a project dependency; SDK bootstrap and adapter are implemented and verified by MCP-0002. |
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
| AUTO-0006 Engineering Project Health / Readiness Audit | COMPLETE / VERIFIED | Typed read-only health aggregation, bounded Git readiness, deterministic next-action guidance, public `project health` CLI, and isolated-wheel E2E verification are complete. Evidence: `AUTO-0006_VERIFICATION_EVIDENCE.md`. |
| AUTO-0007 Engineering Project Reconciliation Plan | IN PROGRESS | Stages 01–03 are complete/verified. Stage 04 Public CLI is implementation-complete in PR #85; corrected head `0e9d0fbd86b174f243193d9b5716ba93aef1fbff` passed Quality #157. Merge and post-merge gate remain. |
| AUTO-0007-01 Reconciliation Planner Design | COMPLETE / VERIFIED | Read-only reconciliation contract and deterministic planner design are established in `AUTO-0007_ENGINEERING_PROJECT_RECONCILIATION_PLAN_DESIGN.md`. |
| AUTO-0007-02 Planner Implementation | COMPLETE / VERIFIED | PR #83 merged; post-merge Quality #147 passed. Master base before stage 03: `006e1677efae525207e49d8c1eb3f1429583c603`. |
| AUTO-0007-03 Reconciliation Invariants | COMPLETE / VERIFIED | Test-only invariant stage. PR #84 merged at `cbbfc382d5b094a21ae3e7dc9d7fc441f12df569`; Quality #148 and post-merge Quality #149 passed. |
| AUTO-0007-04 Public CLI | QUALITY PASSED / MERGE PENDING | PR #85, branch `agent/auto-0007-04-public-cli`, corrected head `0e9d0fbd86b174f243193d9b5716ba93aef1fbff`; Quality #157 passed. |
| Quality gates | PASS THROUGH CURRENT HEAD | AUTO-0007-02 #147, AUTO-0007-03 #148 + #149, AUTO-0007-04 corrected head #157. PR #85 merge and post-merge gate remain. |

## Current Priorities

1. Prepare PR #85 for merge after Quality #157 success.
2. Merge AUTO-0007-04 and run the mandatory post-merge gate.
3. Reconcile authoritative documentation after the merge before starting AUTO-0007-05.
4. Run AUTO-0007-05 Installed Distribution Verification only after the stage-04 post-merge gate succeeds.
5. Preserve the AUTO-0007 fail-closed, deterministic, read-only reconciliation contract.
6. Preserve the published `v0.2.0` release and its exact tag target.
7. Keep PyPI explicitly not approved/not published.

## Implemented Baseline

The verified baseline includes the official Python MCP SDK boundary, 15 registered tool operations, SDK project creation/scaffold CLI, engineering bootstrap, documentation ownership/synchronization, the guarded project migration framework, the production `python-engineering-v2` baseline and first V1-to-V2 migration edge, the read-only engineering project health/readiness audit, and the AUTO-0007 read-only reconciliation planner/invariant baseline.

AUTO-0005 extends AUTO-0004 with positive dual V1/V2 identity and exactly one approved production edge, `python-engineering-v1-to-v2`. New `python-engineering` bootstraps create the V2 identity marker `.ai-engineering.toml` and the V2 `.gitignore` in the same initial commit. Generic SDK-0001/SDK-0001.1 project generation remains separate from that engineering profile behavior.

AUTO-0006 composes the existing inspection, ownership, synchronization, migration, and bounded Git-readiness contracts into one read-only health report. The public installed command is `ai-engineering project health --project PATH`. It returns deterministic `key=value` output, identifies `healthy`, `action_required`, `manual_review`, or `unsupported`, and recommends only already-approved workflows. It has no write/apply/fix authority.

AUTO-0007 composes the existing project identity, inspection, documentation ownership/synchronization, migration readiness, and Git invariants into a read-only reconciliation planner. The planner is fail-closed and deterministic. AUTO-0007-03 verifies manual-review/unsupported behavior, ordering, determinism, project-byte preservation, and Git invariants without changing production authority. AUTO-0007-04 exposes the planner through the installed public CLI while preserving those boundaries.

The production `DEFAULT_MIGRATION_REGISTRY` contains exactly the approved V1-to-V2 edge. Its migration operations are bounded to creation of `.ai-engineering.toml` and exact machine-owned replacement of `.gitignore`. Re-running the same edge against its exact target baseline is an idempotent no-op; unsupported migration ids and unrelated baselines still fail closed.

Installed distribution verification exercises the real public migration and health CLI paths. AUTO-0006 installed-wheel verification covers representative V1, V2, and unsupported states and verifies preservation of Git HEAD, branch, staged index, working-tree status, and remotes. AUTO-0007-04 extends public CLI coverage only; it does not add apply/write authority.

REL-0003 published version `0.2.0` to GitHub. The immutable tag `v0.2.0` points to exact candidate SHA `1faf14c121b7b5da7c8781e3de4e836f85838a76`. Post-release engineering commits do not change the published artifact/tag target. No TestPyPI or PyPI publication occurred.

## Active Work

AUTO-0007-04 Public CLI is implementation-complete and quality-passed on PR #85. The corrected head is `0e9d0fbd86b174f243193d9b5716ba93aef1fbff`; Quality #157 succeeded. The PR remains the active merge gate. No AUTO-0007-05 implementation has started.

## Planned Work

### AUTO-0007 sequence

- AUTO-0007-04 — Public CLI — QUALITY PASSED / MERGE PENDING
- AUTO-0007-05 — Installed Distribution Verification — PLANNED
- AUTO-0007-06 — Final Reconciliation / Documentation — PLANNED

The sequence remains gated: each stage must preserve the read-only authority boundary and pass its quality/post-merge evidence before the next stage starts.
