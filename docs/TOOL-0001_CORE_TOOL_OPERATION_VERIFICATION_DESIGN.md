# TOOL-0001 — Core Tool Operation Verification

**Status:** COMPLETE / VERIFIED

## Objective

TOOL-0001 establishes reproducible automated verification contracts for the existing Workspace,
Git, and Python tool operations. It proves current behavior; it does not add tools, redesign
services, or change the MCP public surface.

The source of truth for the inventory is `EngineeringMCPServer._register_builtin_tools()`. Canonical
registry names are dotted. `ToolNameMapper.to_mcp()` replaces dots with underscores and
`from_mcp()` replaces only the first underscore with a dot, so operation-name underscores are
preserved (for example, `workspace.read_file` ↔ `workspace_read_file`).

## Current Inventory

| Group | Canonical internal name | Exposed MCP name | Arguments | Current return shape | Safety class | Current automated evidence |
|---|---|---|---|---|---|---|
| Workspace | `workspace.list` | `workspace_list` | `path: str` | `list[{path, is_file, is_directory, size}]` | READ_ONLY | Isolated service tests |
| Workspace | `workspace.read_file` | `workspace_read_file` | `path: str` | `{path, content}` | READ_ONLY | Isolated service and SDK-session tests |
| Workspace | `workspace.write_file` | `workspace_write_file` | `path: str`, `content: str` | `{success: True, path}` | LOCAL_MUTATION | Isolated service and SDK-session tests |
| Workspace | `workspace.create_file` | `workspace_create_file` | `path: str` | `{success: True, path}` | LOCAL_MUTATION | Isolated service tests |
| Workspace | `workspace.create_directory` | `workspace_create_directory` | `path: str` | `{success: True, path}` | LOCAL_MUTATION | Isolated service and mapping tests |
| Workspace | `workspace.move` | `workspace_move` | `source: str`, `destination: str` | `{success: True, source, destination}` | LOCAL_MUTATION | Isolated service tests |
| Workspace | `workspace.delete` | `workspace_delete` | `path: str` | `{success: True, path}` | LOCAL_MUTATION | Isolated service tests |
| Git | `git.status` | `git_status` | none | `{branch, is_clean, staged, modified, untracked}` | SUBPROCESS_EXECUTION | Isolated real-repository and SDK-session tests |
| Git | `git.branch` | `git_branch` | none | `{branch}` | SUBPROCESS_EXECUTION | Isolated real-repository tests |
| Git | `git.log` | `git_log` | `limit: int = 10` | `{commits: list[str]}` | SUBPROCESS_EXECUTION | Isolated real-repository tests |
| Git | `git.diff` | `git_diff` | none | `{diff: str}` | SUBPROCESS_EXECUTION | Isolated real-repository tests |
| Python | `python.version` | `python_version` | none | `{executable, version}` | READ_ONLY | Service and SDK-session tests |
| Python | `python.run_tests` | `python_run_tests` | `path: str | None = None` | `{command, success, exit_code, output}` | SUBPROCESS_EXECUTION | Isolated passing/failing fixture tests |
| Python | `python.check_syntax` | `python_check_syntax` | `file: str` | `{file, valid, error}` | READ_ONLY | Isolated valid/error fixture tests and mapping test |
| Python | `python.inspect_package` | `python_inspect_package` | `path: str` | `{path, modules: list[str]}` | READ_ONLY | Isolated package/error fixture tests and mapping test |

The inventory is all 15 registered operations. Tool-wrapper return shapes are documented above;
service methods return their current domain models or primitive values. The SDK adapter serializes a
successful non-string result as JSON text and returns handler exceptions as an `isError=True`
`CallToolResult` containing readable error text.

## Safety Classes

### READ_ONLY

`workspace_list`, `workspace_read_file`, `python_version`, `python_check_syntax`, and
`python_inspect_package` read local state only. Tests must use `tmp_path` for all filesystem input;
even read-only cases must not inspect the canonical checkout except where an existing MCP stdio
contract deliberately starts the server from it.

### LOCAL_MUTATION

`workspace_write_file`, `workspace_create_file`, `workspace_create_directory`, `workspace_move`,
and `workspace_delete` mutate local filesystem state. Every test must use a `tmp_path`-owned
fixture tree and assert the intended result there. It must never use real project files, OneDrive
paths, or paths outside the test-controlled directory.

### SUBPROCESS_EXECUTION

`git_status`, `git_branch`, `git_log`, `git_diff`, and `python_run_tests` execute local programs.
Git tests must use isolated temporary repositories. Python tests must use deterministic local
fixture targets. No test may install dependencies, use a network resource, or modify a user/global
environment.

## Workspace Verification Contract

Workspace services accept the supplied `Path` directly. The current implementation has **no
workspace-root or path-escape protection**. TOOL-0001 must not add or claim such protection; its
tests instead keep every input inside an isolated fixture root. A future safety-boundary feature
requires separately approved production scope.

| Tool | Required success evidence | Controlled current-error evidence | Status |
|---|---|---|---|
| `workspace_list` | List a fixture directory and preserve entry metadata/order. | Missing path and a file path raise `WorkspaceNotFoundError` with the existing directory/not-directory semantics. | VERIFIED |
| `workspace_read_file` | Read fixture UTF-8 text and return path/content through the wrapper. | Missing path raises `WorkspaceNotFoundError`; a non-file path follows current `Path.read_text()` behavior without a new domain error. | VERIFIED |
| `workspace_write_file` | Write and overwrite a fixture file; wrapper returns success/path. | Invalid target follows current filesystem exception behavior and leaves the fixture parent absent. | VERIFIED |
| `workspace_create_file` | Create a new file, including currently supported missing parents. | Existing file raises `WorkspaceAlreadyExistsError`. | VERIFIED |
| `workspace_create_directory` | Create a new directory, including currently supported parent creation. | Existing path raises `WorkspaceAlreadyExistsError`. | VERIFIED |
| `workspace_move` | Move a fixture file or directory and verify source/destination state. | Missing source raises `WorkspaceNotFoundError`; current destination conflict raises `FileExistsError` on the verified platform. | VERIFIED |
| `workspace_delete` | Delete a fixture file and an empty fixture directory. | Missing target raises `WorkspaceNotFoundError`; non-empty directory follows current `Path.rmdir()` error behavior. | VERIFIED |

No path-escape rejection test is required because no protection exists. Mutation tests establish
safety by fixture isolation, not by claiming an unimplemented public boundary.

## Git Verification Contract

Git verification uses a temporary repository initialized inside `tmp_path`. Commits use
process-local identity only (for example, command-scoped or environment `GIT_AUTHOR_*` and
`GIT_COMMITTER_*` values). Tests must not set global or canonical-repository Git configuration and
must not contact remotes.

| Tool | Required success evidence | Controlled current-error evidence | Status |
|---|---|---|---|
| `git_status` | Clean temporary repo, then modified and untracked fixture state with current counters. | Existing service subprocess/command failure contract remains covered. | VERIFIED |
| `git_branch` | Return the current temporary-repo branch. | Non-repository maps current Git command failure to `GitRepositoryNotFoundError`. | VERIFIED |
| `git_log` | Return one or more committed entries in a temporary repo. | Empty/no-commit repository behavior is the current Git command error; no empty-list API is claimed. | VERIFIED |
| `git_diff` | Clean repo returns an empty diff; modified tracked fixture returns a diff containing the change. | Existing Git command failure contract remains covered; no remote operation is used. | VERIFIED |

## Python Verification Contract

| Tool | Required success evidence | Controlled current-error evidence | Status |
|---|---|---|---|
| `python_version` | Wrapper returns the current interpreter executable and non-empty version. | No separate application-level error path exists. | VERIFIED |
| `python_run_tests` | Run a deterministic passing fixture test target and assert command, success, exit code, and captured output. | A deterministic failing fixture target returns `success=False` and a nonzero exit code. | VERIFIED |
| `python_check_syntax` | Validate a fixture Python file. | Syntax-error fixture returns `valid=False` with an error; missing path raises `SyntaxValidationError`. | VERIFIED |
| `python_inspect_package` | List sorted `*.py` module filenames in a fixture package directory. | Missing path raises `PythonExecutionError`; existing non-directory path returns the current empty result. | VERIFIED |

Focused tests must never invoke the project-wide suite through `python_run_tests`; fixture targets
keep subprocess work deterministic and bounded. No dependency installation, network access, or
arbitrary user command execution is in scope.

## Layer Strategy

TOOL-0001 uses the smallest layer that proves each behavior.

| Layer | Purpose | Required coverage |
|---|---|---|
| Service/unit | Prove filesystem, Git, and Python operation behavior with isolated fixtures. | All 15 operations: required success/error cases from the matrices. |
| Registry/tool-handler | Prove all 15 canonical descriptors are registered, wrappers preserve documented return shapes, and descriptor/MCP names remain correct. | Full inventory and mapping coverage; avoid duplicating every service case. |
| MCP SDK-session | Prove adapter serialization, controlled errors, and reversible public-name dispatch. | Representative operations: `workspace_read_file`, one workspace mutation in `tmp_path`, `git_status` in an isolated repo, and `python_version` or `python_check_syntax`. |

`test_mcp_sdk_adapter.py` verifies mapping round trips, multiword dispatch, the
`workspace_read_file` missing-file MCP error, representative Workspace read/write dispatch,
isolated-repository `git_status`, and `python_version`. It does not test every operation through
all three layers.

## Operation Verification Matrix

| Tool | Safety class | Success evidence required | Controlled-error evidence required | Unit/service test? | SDK-session test? | Current status |
|---|---|---|---|---|---|---|
| `workspace_list` | READ_ONLY | Fixture directory listing | Missing/not-directory | Yes | No | VERIFIED |
| `workspace_read_file` | READ_ONLY | Fixture text read | Missing and current non-file behavior | Yes | Yes | VERIFIED |
| `workspace_write_file` | LOCAL_MUTATION | Fixture write/overwrite | Current invalid-target behavior | Yes | Yes (representative mutation) | VERIFIED |
| `workspace_create_file` | LOCAL_MUTATION | New fixture file | Existing conflict | Yes | No | VERIFIED |
| `workspace_create_directory` | LOCAL_MUTATION | New fixture directory | Existing conflict | Yes | No | VERIFIED |
| `workspace_move` | LOCAL_MUTATION | Fixture move | Missing source/current destination conflict | Yes | No | VERIFIED |
| `workspace_delete` | LOCAL_MUTATION | Fixture file and empty directory delete | Missing/current non-empty directory behavior | Yes | No | VERIFIED |
| `git_status` | SUBPROCESS_EXECUTION | Clean and dirty temporary repo | Existing command error | Yes | Yes | VERIFIED |
| `git_branch` | SUBPROCESS_EXECUTION | Temporary repo branch | Non-repository | Yes | No | VERIFIED |
| `git_log` | SUBPROCESS_EXECUTION | Committed temporary repo | Empty repo current error | Yes | No | VERIFIED |
| `git_diff` | SUBPROCESS_EXECUTION | Clean and modified temporary repo | Existing command error | Yes | No | VERIFIED |
| `python_version` | READ_ONLY | Interpreter/version result | None exposed | Yes | Yes | VERIFIED |
| `python_run_tests` | SUBPROCESS_EXECUTION | Passing fixture target | Failing fixture target | Yes | No | VERIFIED |
| `python_check_syntax` | READ_ONLY | Valid fixture | Syntax-error/missing fixture | Yes | No | VERIFIED |
| `python_inspect_package` | READ_ONLY | Fixture package modules | Missing path/current non-directory behavior | Yes | No | VERIFIED |

All matrix tests now pass. The matrix distinguishes service, registry, and representative SDK
evidence; no tool is marked VERIFIED solely because it is registered or manually exercised.

## Isolation Rules

- Use pytest `tmp_path` or an external writable temporary root for every fixture.
- Create Git repositories only inside temporary directories; use process-local Git identity.
- Do not hardcode `C:\\Users\\...`, `D:\\...`, a OneDrive path, or a user-specific path.
- Do not modify the canonical repository under test, global Git configuration, or user/global
  environment.
- Do not use network access, remotes, package installation, or dependency management.
- Keep destructive filesystem operations inside fixture directories and assert their boundaries.
- Use deterministic local Python fixture files/tests; do not run arbitrary user commands.

## Error-Behavior Rules

For every planned controlled-error case, assert the current deterministic exception/result type or
stable semantic message. Do not over-specify text that is not a public promise. At the SDK layer,
assert that normal tool errors are returned as readable `isError=True` results, with no raw
traceback, server crash, or protocol failure. Validation failure must not mutate a fixture when the
operation reaches validation before mutation.

Platform filesystem errors that the current services deliberately pass through are recorded as
current behavior; this milestone does not normalize them.

## Non-Goals

TOOL-0001 excludes:

- new Workspace, Git, or Python tools;
- service refactors, API redesign, or tool renaming;
- MCP transport changes, registry/SDK adapter redesign, or new clients;
- remote Git operations and shell-command tools;
- dependency management or Python environment creation;
- performance benchmarks, broad end-to-end automation, and release packaging changes; and
- adding workspace-root protection or changing existing error semantics.

## Completion Criteria

TOOL-0001 is complete only when:

1. the current 15-tool inventory and operation matrix are documented;
2. required safe success/error cases are implemented at the selected layers;
3. representative Workspace, Git, and Python SDK-session dispatch is verified, including
   snake_case operation names where relevant;
4. all tests are isolated, reproducible, and make no network/global-environment changes;
5. existing tool behavior and public names remain unchanged;
6. full pytest, Ruff, mypy, and `git diff --check` pass; and
7. documentation is updated to VERIFIED only where the implemented evidence supports it.

## Completion Evidence

The focused service/registry/SDK-session suite is isolated under pytest `tmp_path` fixtures and
temporary Git repositories. The complete repository suite passed with 89 tests, with Ruff and mypy
reporting no findings. TOOL-0001 changes tests and verification documentation only; it does not
change public tool behavior. The earlier Git porcelain status parsing repair is recorded separately
in merged PR #22.
