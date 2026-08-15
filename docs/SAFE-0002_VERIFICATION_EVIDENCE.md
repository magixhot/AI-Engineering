# SAFE-0002 — Git/Python Execution Safety Verification Evidence

**Status:** COMPLETE / VERIFIED
**Evidence date:** 2026-08-15

## Verified Boundary

SAFE-0002 binds the active MCP Git and path-taking Python operations to `MCPConfig.workspace_root`.

The verified V1 contract is:

- active MCP Git operations use an explicitly bounded Git service;
- MCP Git is allowed only when `workspace_root` is itself the Git repository top level;
- parent-repository discovery above `workspace_root` is rejected;
- active MCP Python syntax/package/test paths are resolved against and contained by `workspace_root`;
- traversal, absolute outside-root, sibling-prefix, and supported link escapes are rejected before outside inspection/execution;
- `python.run_tests` launches only `sys.executable -m pytest <authorized-target>` with `cwd=workspace_root`, `shell=False`, `stdin=DEVNULL`, captured output, and a bounded timeout;
- public MCP tool names and input schemas remain unchanged;
- SAFE-0002 is not an operating-system sandbox and does not contain malicious code already authorized to run inside the workspace.

## Linux CI Evidence

Post-merge Quality run #71 verified commit `e87deba10d04f69bb8b108a42f9f73a8fbd41c71` after the Python link-escape evidence was added.

Results:

- Python: 3.11.15 on Ubuntu 24.04;
- pytest: **155 passed**;
- Ruff: **0 findings**;
- mypy: **0 issues in 79 source files**;
- Python symlink/link-escape coverage executed successfully on Linux;
- REL-0001 distribution verification remained part of the full pytest suite.

A later portability-only AUTO-0002 test repair was merged as `b1b0163b619e373d7fdd9b315426e35bf6dbfb1f`; post-merge Quality run #73 also completed successfully with Ruff, mypy, and full pytest green. The repair changed only a cross-platform newline assertion and did not change SAFE-0002 production behavior.

## Windows-Local Evidence

Windows verification was run from `C:\AI\Projects\AI-Engineering` on Python 3.11.9 against the post-repair `master` line.

Focused SAFE-0002 suite:

- collected: 13;
- passed: **12**;
- skipped: **1**;
- skip reason: the process could not create the Python symlink fixture (`WinError 1314`).

Full repository suite:

- collected: 155;
- passed: **153**;
- skipped: **2**;
- skip 1: SAFE-0002 Python link-escape fixture unavailable because the Windows process lacked symlink-creation privilege (`WinError 1314`);
- skip 2: SAFE-0001 Workspace link-escape fixture unavailable for the same privilege reason;
- Ruff: **0 findings**;
- mypy: **0 issues in 79 source files**;
- `git diff --check`: passed;
- final `git status --short`: clean.

The Windows skips are permitted by the SAFE contracts only because fixture creation itself was denied by the platform/process privilege. Equivalent link-escape coverage executes in Linux CI.

## Cross-Platform Defect Discovered During Verification

The first Windows full-suite run exposed an AUTO-0002 test defect: a human-content preservation assertion required literal LF line endings even though the production documentation synchronization implementation intentionally preserves the source document's existing LF or CRLF convention.

The production implementation was not changed. The test assertion was made line-ending-neutral while the dedicated CRLF-preservation test remained intact. PR #52 passed CI and was merged before the final Windows verification.

This defect is classified as test portability debt discovered and resolved during SAFE-0002-04; it is not a SAFE-0002 authorization defect.

## Completion Matrix

| Area | Evidence |
|---|---|
| MCP construction | Active Git/Python handlers are root-bound to `MCPConfig.workspace_root`. |
| Git exact-root repository | Existing status/branch/log/diff operations succeed at the authorized repository root. |
| Git parent-repository escape | Rejected by bounded Git repository-top-level policy. |
| Git non-repository root | Controlled Git-domain repository error. |
| Python syntax/package in-root | Relative and absolute in-root targets succeed. |
| Python outside/traversal | Controlled `PythonPermissionError`. |
| Python link escape | Linux executes rejection coverage; Windows records privilege-dependent fixture skip. |
| Pytest target containment | Outside/traversal/link escapes rejected before subprocess launch. |
| Pytest subprocess | Workspace-root cwd, current interpreter, shell disabled, stdin closed, timeout enforced. |
| MCP SDK session | Representative in-root success and outside-root controlled errors verified. |
| Regression | Workspace, SDK, AUTO-0001, AUTO-0002, release, Ruff, mypy, and full pytest remain green. |

## Final Status

SAFE-0002 is **COMPLETE / VERIFIED** for the approved V1 active-MCP Git/Python authority-root and subprocess containment contract.

This status does not claim OS sandboxing, containment of code already authorized to execute inside the workspace, network isolation, resource quotas, arbitrary-command safety, or future Git/Python tools that do not yet exist.
