# SAFE-0001 — Workspace Path Safety Boundary

**Status:** COMPLETE / VERIFIED
**Scope:** Filesystem boundary for MCP-exposed Workspace operations

## Objective

SAFE-0001 defines and implements a fail-closed workspace boundary for all seven existing MCP-exposed Workspace operations without changing their public tool names or successful result shapes. The active MCP server treats `MCPConfig.workspace_root` as the authority root and rejects Workspace paths that resolve outside it.

## Implemented Boundary

The active MCP path constructs `WorkspaceService` with the configured `MCPConfig.workspace_root` and binds Workspace handlers through an explicit `WorkspaceTools` instance. The active MCP server no longer relies on the module-global Workspace service for authorization.

The configured root is captured and resolved when the bounded service is constructed. Relative paths are interpreted from that root. Absolute paths are accepted only when their resolved target remains at or below the root. Authorization uses resolved `pathlib` ancestry rather than string-prefix checks.

Traversal through `..`, absolute outside-root paths, sibling-prefix lookalikes, and existing symlink/junction-style redirects that resolve outside the root are rejected with `WorkspacePermissionError`. Prospective create/write destinations are authorized before mutation. `workspace.move` independently authorizes source and destination. The workspace root itself cannot be moved or deleted.

## Compatibility Treatment

SAFE-0001 discovered that SDK-0001 Project Templates historically use `WorkspaceService()` as an internal filesystem helper while intentionally generating projects at caller-selected paths outside the repository cwd. Applying the MCP boundary to every no-argument instance would have broken the established SDK-0001/REL-0001 contract.

The verified compatibility treatment is therefore explicit:

- `WorkspaceService(root)` is bounded and is used by all active MCP Workspace handlers;
- no-argument `WorkspaceService()` preserves legacy non-MCP compatibility for existing internal consumers;
- module-level Workspace helper functions explicitly construct a service rooted at the cwd captured at import and are not the active MCP server path;
- there is no mutable global `set_workspace_root()` mechanism.

This preserves the approved SDK/template behavior without weakening the MCP Workspace authority boundary.

## Operation Matrix

| Operation | Root allowed | Boundary behavior |
|---|---:|---|
| `workspace.list` | Yes | Directory must resolve to root or descendant. |
| `workspace.read_file` | Normal file semantics | File must resolve to root or descendant. |
| `workspace.write_file` | Normal OS type semantics | Existing or prospective target must remain inside root. |
| `workspace.create_file` | Existing-path semantics apply | Prospective file/parent chain must remain inside root. |
| `workspace.create_directory` | Existing root keeps existing-path behavior | Prospective directory/parent chain must remain inside root. |
| `workspace.move` | Root source prohibited | Source and destination independently must remain inside root. |
| `workspace.delete` | Root prohibited | Target must remain inside root; root cannot be deleted. |

## Error Contract

Boundary violations use the existing `WorkspacePermissionError` domain exception. Existing `WorkspaceNotFoundError`, `WorkspaceAlreadyExistsError`, and ordinary OS errors remain responsible for their prior non-boundary cases after authorization succeeds.

Authorization occurs before outside-path existence/type probing where applicable.

## MCP and Configuration Contract

`MCPConfig.workspace_root` is now an enforced security setting for the active Workspace tool path. The default may still originate from `Path.cwd()`, but it is captured and resolved during server/service construction. Changing the workspace root at runtime is out of scope; a new server instance is required.

Existing canonical/exposed names remain unchanged:

- `workspace.list` / `workspace_list`
- `workspace.read_file` / `workspace_read_file`
- `workspace.write_file` / `workspace_write_file`
- `workspace.create_file` / `workspace_create_file`
- `workspace.create_directory` / `workspace_create_directory`
- `workspace.move` / `workspace_move`
- `workspace.delete` / `workspace_delete`

All 15 overall Workspace/Git/Python descriptors and snake_case mappings remain covered by the existing registry/SDK tests.

## Verification Evidence

### Linux / GitHub Actions

PR #32 (`feat: enforce workspace path safety boundary`) completed successfully and was merged as `fb9ba7596ff826a0526caa7464fdb991d6323d23`.

Successful PR Quality run: `31883170195`.

Verified on Linux / Python 3.11:

- Ruff: PASS;
- mypy: PASS — 69 source files;
- pytest: **99 passed**;
- REL-0001 distribution verification: PASS;
- SDK-0001 project-template and CLI suites: PASS;
- focused Workspace and representative SDK-session boundary coverage: PASS.

The post-merge `master` Quality run also completed successfully.

### Windows local verification

Windows verification was executed on Python 3.11.9 using a dedicated external temporary directory because the machine's default pytest temporary directory had an unrelated local ACL/permission problem.

Focused SAFE verification:

- **36 passed, 1 skipped**;
- the single skip was the symlink escape fixture because Windows returned `WinError 1314` (the process lacked the privilege required to create the symlink).

Full Windows suite:

- **98 passed, 1 skipped**;
- the same single symlink fixture was skipped for `WinError 1314`;
- Ruff: PASS / 0 findings;
- mypy: PASS / 0 issues in 69 source files;
- working tree remained clean.

The skip is permitted by the SAFE-0001 design because the platform/permissions genuinely prevented creation of the link fixture. Linux CI executed the symlink coverage successfully as part of its 99-passing suite.

## Verified Coverage

Focused verification covers:

- resolved workspace-root capture;
- relative and absolute in-root success;
- relative traversal and absolute outside-root rejection;
- sibling-prefix containment correctness;
- prospective create/write escape rejection;
- link escape rejection where fixture creation is supported;
- independent move endpoint authorization;
- root move/delete protection;
- existing in-root controlled errors;
- server construction from `MCPConfig.workspace_root`;
- representative SDK-session in-root calls and controlled outside-root errors.

## Security Boundary Statement

SAFE-0001 is a path-authorization boundary for MCP-exposed Workspace operations. It is not an operating-system sandbox and does not claim race-proof capability security, ACL enforcement, content scanning, filesystem quotas, or containment of Git/Python subprocess semantics.

## Non-Goals

SAFE-0001 V1 does not include new Workspace tools, tool/schema renaming, Git/Python sandboxing, remote filesystems, per-client roots, runtime root switching, subdirectory allowlists, content/file-type policy, quotas, OS-level sandboxing, release publishing, or deployment changes.

## Completion Result

SAFE-0001 is **COMPLETE / VERIFIED** for the approved V1 contract: the active MCP Workspace path is root-bounded, fail-closed for outside paths, covered by service and SDK-session tests, green on Linux CI, and locally verified on Windows with one explicitly permitted privilege-dependent symlink skip.
