# SAFE-0002 — Git/Python Execution Safety Design

**Status:** COMPLETE / VERIFIED
**Scope:** Active MCP Git and Python tool authorization and subprocess containment policy

## 1. Purpose

SAFE-0002 defines the next security boundary after SAFE-0001. SAFE-0001 constrains MCP Workspace filesystem operations to `MCPConfig.workspace_root`, but explicitly does not contain Git or Python subprocess semantics.

SAFE-0002 closes that gap for the active MCP path without turning AI-Engineering into an operating-system sandbox.

The design was documentation-first and is now implemented and verified for the V1 contract recorded here.

## 2. Existing Risk Surface

Before SAFE-0002 implementation, the active MCP server registered module-level Git and Python handlers using process-level service defaults rather than service instances explicitly bound to `MCPConfig.workspace_root`.

Current Git operations are read-only at the Git command level:

- `git.status`
- `git.branch`
- `git.log`
- `git.diff`

Current Python operations are:

- `python.version`
- `python.run_tests`
- `python.check_syntax`
- `python.inspect_package`

`python.run_tests` launches `python -m pytest` against a caller-selected path. `python.check_syntax` and `python.inspect_package` read caller-selected paths. SAFE-0002 now governs these path-taking operations on the active MCP path.

## 3. Security Objective

For the active MCP server only, Git and Python operations are explicitly bound to the configured `MCPConfig.workspace_root` and fail closed when they would inspect or execute against content outside that root.

The security objective is:

> An MCP client may use the existing Git/Python tools only against the configured workspace authority root and its authorized descendants, without using path traversal, absolute outside paths, parent-repository discovery, or caller-controlled subprocess working directories to escape the configured workspace.

## 4. Authority Root

`MCPConfig.workspace_root` is the single authority root for active MCP Workspace, Git, and path-taking Python operations.

The root is resolved and captured during server/service construction. Runtime mutation of the root is not part of SAFE-0002.

Authorization uses resolved path ancestry, not string-prefix comparison.

## 5. Active-Path Service Construction

The active MCP server uses explicit bounded Git/Python service instances as its security boundary, conceptually:

```text
EngineeringMCPServer
    ├── WorkspaceService(workspace_root)
    ├── GitService(workspace_root, bounded=True)
    └── PythonService(workspace_root, bounded=True)
```

Exact constructor signatures are an implementation detail, but active MCP handlers are instance-bound to the captured root.

Direct/internal no-argument services may retain legacy behavior for non-MCP consumers where compatibility requires it. Such legacy behavior is not used by the active MCP server.

## 6. Git Safety Contract

### 6.1 Repository policy

SAFE-0002 V1 permits active MCP Git operations only when the configured workspace root is itself the Git repository top-level directory.

The bounded Git service determines the repository top level and requires:

```text
resolved_git_toplevel == resolved_workspace_root
```

A workspace root that is merely a subdirectory of a parent Git repository is rejected for MCP Git operations. This prevents Git repository discovery from walking above the configured authority root.

Nested repositories below the workspace root are not selected automatically because the current Git tools expose no repository selector.

### 6.2 Allowed Git commands

SAFE-0002 V1 authorizes only the existing read-only command families required by the public tools:

- `git status --porcelain`
- `git branch --show-current`
- bounded `git log`
- `git diff`
- repository-top-level verification required by the safety implementation

No general-purpose Git command execution API is introduced.

### 6.3 Explicitly denied Git behavior

SAFE-0002 V1 does not authorize:

- `add`, `commit`, `reset`, `checkout`, `switch`, `restore`, `clean`, `stash`, `merge`, `rebase`, `cherry-pick`;
- `push`, `pull`, `fetch`, remote modification, credential helpers, or network Git;
- caller-supplied repository paths;
- operating on a parent repository above `workspace_root`;
- automatic nested-repository selection;
- mutation of global or user Git configuration.

Existing non-MCP project-template Git initialization remains outside this contract and is preserved by binding only the active MCP Git path.

## 7. Python Safety Contract

### 7.1 `python.version`

`python.version` remains path-independent and continues to report the active interpreter version and executable path. SAFE-0002 does not treat this operation as project-code execution.

### 7.2 `python.check_syntax`

The requested file must resolve at or below `workspace_root` before file existence/content is inspected.

Outside-root, traversal, and link-escape paths are rejected with a controlled Python-domain permission error before source content is read.

### 7.3 `python.inspect_package`

The requested package directory must resolve at or below `workspace_root` before existence or module enumeration occurs.

Outside-root, traversal, and link-escape paths are rejected before package contents are enumerated.

### 7.4 `python.run_tests`

`python.run_tests` is the only existing Python tool that executes project-controlled Python code and therefore receives the strictest V1 policy.

The bounded service:

1. resolves the requested test target relative to `workspace_root` when a relative path is supplied;
2. requires the resolved target to remain at or below `workspace_root`;
3. rejects absolute outside-root, traversal, and link-escape targets;
4. launches pytest with `cwd=workspace_root`;
5. invokes only the current interpreter as `sys.executable -m pytest <authorized-target>`;
6. keeps the target as an argument rather than constructing a shell command;
7. keeps `shell=False`;
8. uses `stdin=DEVNULL`;
9. retains captured stdout/stderr behavior;
10. enforces a bounded subprocess timeout.

The default target remains `tests`, interpreted under `workspace_root`.

SAFE-0002 V1 does not add arbitrary script, module, `-c`, interpreter, executable, shell, or command arguments.

## 8. Environment Policy

Subprocess execution does not rely on shell expansion.

SAFE-0002 V1 does not attempt to provide a fully scrubbed hermetic environment. However, the active bounded subprocess path does not mutate global environment variables and does not introduce caller-controlled environment injection.

A future explicit environment allowlist/sanitization milestone may be added if evidence shows it is required.

## 9. Path Authorization Semantics

For all path-taking bounded Python operations:

- relative paths are interpreted from captured `workspace_root`;
- absolute paths are permitted only if their resolved path remains within the root;
- `..` traversal that resolves outside the root is rejected;
- existing symlink/junction/reparse-point escapes that resolve outside the root are rejected;
- sibling-prefix lookalikes are rejected by ancestry checks;
- authorization occurs before outside-target existence/type/content probing where practical.

The same containment helper may be reused across Workspace/Python only if doing so preserves clear domain ownership and error types. SAFE-0002 does not require a broad architectural refactor.

## 10. Error Contract

SAFE-0002 uses controlled domain-specific permission errors rather than leaking raw path-resolution or subprocess failures.

Error classes include:

- `GitPermissionError` for repository-boundary violations;
- `PythonPermissionError` for Python path/execution-boundary violations.

Existing errors remain responsible for non-authorization failures after authorization succeeds:

- Git repository-not-found and command failures;
- Python execution and syntax-validation failures;
- ordinary authorized-path file errors.

SDKAdapter continues converting controlled tool failures into MCP `isError=True` results without protocol corruption.

## 11. Compatibility Contract

SAFE-0002 intentionally changes active MCP behavior where the previous behavior could escape the configured workspace.

Verified compatibility preservation:

- all existing tool names and input schemas remain unchanged;
- successful in-root result shapes remain unchanged;
- `python.version` behavior remains unchanged;
- existing SDK-0001/AUTO-0001 project creation and Git initialization behavior remains unchanged;
- AUTO-0002 local documentation synchronization remains unchanged;
- direct/internal service compatibility may remain unbounded only when it is not used by active MCP handlers.

The following behavior is intentionally a controlled error:

- MCP Git inspection when `workspace_root` is inside a parent repository rather than the repository top level;
- MCP Python path access outside `workspace_root`;
- MCP pytest execution against outside-root targets.

## 12. Threat Model

SAFE-0002 V1 addresses:

- information disclosure from Git operations resolving a parent repository outside the workspace;
- reading Python source/package structure outside the workspace;
- executing pytest against caller-selected outside-workspace code;
- traversal and absolute-path escapes;
- link-based escapes for path-taking Python operations;
- accidental use of process cwd as the active MCP authorization root;
- shell-injection risks from subprocess construction.

## 13. Non-Goals

SAFE-0002 V1 does not claim protection against:

- malicious code executed by an authorized in-workspace pytest run;
- subprocesses spawned by tests;
- network access performed by authorized test code;
- OS-level filesystem or process sandboxing;
- container isolation;
- CPU/memory/disk quotas;
- race-proof filesystem capability security;
- environment-secret exfiltration by authorized in-workspace test code;
- Python import-hook/sitecustomize isolation;
- Git hooks outside commands that SAFE-0002 never invokes;
- arbitrary command execution because no such tool exists;
- additional Git mutation tools;
- additional Python execution tools;
- SAFE-0001 Workspace redesign;
- AUTO-0002 documentation ownership changes;
- release or publication changes.

The project must not describe SAFE-0002 as an OS sandbox.

## 14. Verification Matrix

Implementation evidence covers:

| Area | Required evidence |
|---|---|
| MCP construction | Git/Python active handlers are bound to `MCPConfig.workspace_root` |
| Git exact-root repo | status/branch/log/diff succeed when root is the Git top level |
| Git parent-repo escape | root inside a parent repository is rejected |
| Git non-repo root | controlled repository error |
| Git command scope | only approved command families are reachable through existing tools |
| Python version | unchanged successful result |
| Syntax relative in-root | succeeds |
| Syntax absolute in-root | succeeds |
| Syntax outside/traversal | controlled rejection before content read |
| Syntax link escape | controlled rejection where fixture creation is supported |
| Package relative/absolute in-root | succeeds |
| Package outside/link escape | controlled rejection |
| Pytest default target | runs `tests` under workspace root |
| Pytest in-root explicit target | succeeds with workspace-root cwd |
| Pytest outside/traversal | rejected before subprocess launch |
| Pytest link escape | rejected where fixture creation is supported |
| Pytest command construction | `sys.executable -m pytest`, shell disabled, stdin closed |
| Pytest timeout | controlled execution error |
| MCP SDK session | representative in-root Git/Python success and outside-root controlled errors |
| Regression | existing Workspace, SDK, AUTO-0001, AUTO-0002, release tests remain green |

Windows link-fixture skips are acceptable only when the platform or process privilege genuinely prevents fixture creation and Linux CI executes the equivalent coverage. Final evidence records Linux execution and Windows `WinError 1314` skips exactly under that rule.

## 15. Atomic Implementation Sequence

### SAFE-0002-02 — Bound Active MCP Git Operations

Completed. Explicit bounded Git service/tool instances were added for the active MCP server, including exact-root repository verification, permission errors, and focused service/SDK-session tests.

### SAFE-0002-03 — Bound Active MCP Python Operations

Completed. Root-bound Python service/tool instances, path authorization for syntax/package/test targets, workspace-root pytest cwd, subprocess timeout, and focused service/SDK-session tests were added.

### SAFE-0002-04 — Cross-Platform and Integration Evidence

Completed. Full Linux quality evidence, explicit Python link-escape coverage, Windows-local verification, regression evidence, and documentation reconciliation are recorded in `SAFE-0002_VERIFICATION_EVIDENCE.md`.

No release publication is implied.

## 16. Completion Criteria

SAFE-0002 completion evidence confirms:

- the design contract was accepted;
- active MCP Git and Python handlers are explicitly root-bound;
- Git cannot walk above `workspace_root` to a parent repository;
- path-taking Python operations cannot inspect or execute outside `workspace_root`;
- pytest executes only through the bounded existing command contract with workspace-root cwd and timeout;
- successful existing in-root result shapes and public tool schemas are preserved;
- non-MCP SDK/AUTO project-generation behavior remains green;
- representative SDK-session boundary tests pass;
- repository pytest, Ruff, mypy, and distribution verification pass;
- documentation states the exact verified boundary without claiming OS-level sandboxing.

## 17. Accepted Compatibility/Security Decision

The implemented and verified policy is:

> `MCPConfig.workspace_root` is the authority root for active MCP Git and path-taking Python operations, and MCP Git operations are permitted only when that root is itself the Git repository top level.

This is the central SAFE-0002 compatibility/security decision. The recorded V1 behavior and evidence follow from that boundary.

## 18. Verification Evidence

See `SAFE-0002_VERIFICATION_EVIDENCE.md` for the final Linux/Windows evidence, including 155-pass Linux CI, 153-pass/2-permitted-skip Windows verification, Python link-escape coverage, subprocess checks, the resolved AUTO-0002 newline-test portability defect, and the explicit non-sandbox boundary.
