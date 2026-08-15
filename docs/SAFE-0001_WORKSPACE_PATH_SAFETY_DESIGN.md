# SAFE-0001 — Workspace Path Safety Boundary

**Status:** DESIGN / IMPLEMENTATION PENDING
**Scope:** Filesystem boundary for MCP-exposed Workspace operations

## Objective

SAFE-0001 defines a fail-closed workspace boundary for all seven existing Workspace operations without changing their public tool names or expanding tool scope. The active MCP server must treat one configured directory as the authority root and reject Workspace paths that resolve outside it.

The design addresses the known gap that `MCPConfig.workspace_root` exists but the current Workspace tool path uses a module-global unbounded `WorkspaceService()` and therefore does not enforce that root.

## Current Baseline

The current server configuration already contains `workspace_root: Path = Path.cwd()`, but `EngineeringMCPServer` registers module-level Workspace handlers and those handlers share an unconfigured `WorkspaceService`. `WorkspaceService` currently accepts caller-supplied paths directly for list, read, write, create, move, and delete operations.

SAFE-0001 therefore changes the path-authority model, not the set of tools. It is intentionally treated as a compatibility-sensitive security milestone.

## Boundary Decision

The canonical Workspace authority is `MCPConfig.workspace_root` captured when the server is constructed.

The active MCP path must create a Workspace service bound to that root. Workspace authorization must not depend on the process current working directory after construction, environment-specific absolute paths, OneDrive locations, or caller-controlled changes to `cwd`.

The configured root must be normalized to an absolute resolved path once during service construction. The root must exist and be a directory. Invalid root configuration is a startup/construction error; the service must not silently fall back to an unrestricted mode.

## Path Interpretation

Caller paths follow these rules:

1. A relative path is interpreted relative to the configured workspace root.
2. `.` and an empty-equivalent relative path identify the workspace root where the operation itself permits the root.
3. An absolute path is accepted only when its resolved target remains inside the configured workspace root.
4. `..` is not rejected merely by string inspection; the normalized/resolved target determines authorization.
5. Platform-specific path syntax must be handled by `pathlib`; no hardcoded Windows or Linux path rules belong in the public contract.

This preserves practical callers that already send absolute paths inside the project while preventing absolute-path escape.

## Canonicalization and Containment

Authorization is based on canonical resolved containment, not lexical prefix checks.

For an existing target, the implementation must resolve the path and verify that the result is either the workspace root or a descendant of it.

For a target that may not yet exist, such as `create_file`, `create_directory`, or a new `write_file` destination, the implementation must resolve the deepest existing parent chain with normal `Path.resolve(strict=False)` semantics and verify that the resulting candidate remains within the root before mutation.

String-prefix checks such as `str(path).startswith(str(root))` are prohibited because sibling paths can share textual prefixes without being descendants.

## Symlink, Junction, and Reparse-Point Policy

Filesystem links must not provide an escape route.

If a path inside the workspace traverses an existing symbolic link, junction, or equivalent filesystem redirect whose resolved target is outside the workspace root, the operation must be rejected with the workspace boundary error.

The conservative V1 rule also applies when the final path itself is a link to an outside target. SAFE-0001 does not special-case unlinking an outside-pointing symlink as safe; such paths are rejected rather than introducing operation-specific link semantics.

Broken-link and platform-specific reparse behavior must be covered by focused tests where reliably supported. The boundary is a path-authorization control, not a hardened operating-system sandbox against malicious concurrent filesystem races.

## Operation Matrix

| Operation | Root allowed | Boundary requirements |
|---|---:|---|
| `workspace.list` | Yes | Listed directory must resolve to root or descendant. |
| `workspace.read_file` | Path-authorized; normal file validation still applies | File path must resolve to root or descendant. |
| `workspace.write_file` | Path-authorized; normal OS type errors still apply | Existing target or prospective target must remain inside root. |
| `workspace.create_file` | No practical root-file creation; normal existing-path behavior applies | Prospective file and parent chain must remain inside root. |
| `workspace.create_directory` | Existing root keeps existing-path behavior | Prospective directory and parent chain must remain inside root. |
| `workspace.move` | Workspace root itself must not be moved | Both source and destination must independently resolve inside root; escape in either direction is rejected. |
| `workspace.delete` | No | Workspace root itself must never be deleted through a Workspace tool. |

A move from outside to inside, inside to outside, or through an outside-resolving link is rejected. SAFE-0001 does not turn Workspace tools into an import/export mechanism across the boundary.

## Root Protection

The configured workspace root is an authority boundary and must not be removed or relocated by its own tools.

`workspace.delete` targeting the root must raise the boundary permission error even if the directory is empty. `workspace.move` with the root as source must also be rejected. These checks occur before filesystem mutation.

Other operations may address the root when their normal semantics make sense, especially `workspace.list(".")`.

## Error Contract

Boundary violations use the existing `WorkspacePermissionError` domain exception. SAFE-0001 does not introduce a second security exception type unless implementation evidence proves the existing type insufficient.

Required controlled-error categories include:

- relative traversal resolving outside the root;
- absolute path outside the root;
- symlink/junction escape;
- move source outside the root;
- move destination outside the root;
- attempted root delete;
- attempted root move.

Existing `WorkspaceNotFoundError`, `WorkspaceAlreadyExistsError`, and ordinary OS errors remain responsible for their current non-boundary cases after authorization succeeds.

Authorization should happen before existence/type errors where the supplied path itself is outside the workspace. This prevents outside paths from being probed through differing file-existence behavior.

## Service Ownership and Dependency Injection

The active MCP server must not rely on the current module-global unbounded `_service = WorkspaceService()` for Workspace authorization.

Preferred implementation direction:

1. `WorkspaceService` receives a required workspace root at construction.
2. `EngineeringMCPServer` constructs the bounded service from `self._config.workspace_root`.
3. Registered Workspace handlers are bound to that service through a small explicit adapter/factory or equivalent dependency-injection mechanism.
4. Canonical MCP names and descriptor schemas remain unchanged.

A mutable process-global `set_workspace_root()` or similar hidden reconfiguration mechanism is explicitly rejected.

If preserving module-level public helper functions is necessary for compatibility, they must not be the active unbounded server path. Any compatibility treatment must remain explicit and tested.

## Configuration Semantics

`MCPConfig.workspace_root` becomes an enforced security setting rather than dormant metadata.

The current default `Path.cwd()` may remain for the default configuration, but it is captured and resolved when the server/service is created. No hardcoded repository path is permitted.

Changing the workspace root during a running server is out of scope for SAFE-0001 V1. A new server instance is required for a different authority root.

## Return Shapes and MCP Names

SAFE-0001 must not rename tools or change successful result shapes solely for the boundary implementation.

Existing canonical/exposed names remain:

- `workspace.list` / `workspace_list`
- `workspace.read_file` / `workspace_read_file`
- `workspace.write_file` / `workspace_write_file`
- `workspace.create_file` / `workspace_create_file`
- `workspace.create_directory` / `workspace_create_directory`
- `workspace.move` / `workspace_move`
- `workspace.delete` / `workspace_delete`

The path strings echoed by existing wrappers are not security authorities; authorization is based on the server-side resolved path.

## Verification Strategy

Implementation verification must use isolated temporary workspaces and must not mutate the canonical repository outside normal test fixtures.

Required service coverage:

- relative in-root success for all applicable operations;
- absolute in-root success for representative operations;
- `..` traversal escape rejection;
- absolute outside-root rejection;
- prospective create/write path escape rejection;
- move source and destination boundary rejection;
- root delete and root move rejection;
- existing controlled errors still behave correctly inside the root;
- symlink escape tests on platforms where test creation is supported;
- no string-prefix false-positive containment.

Required integration coverage:

- server construction uses `MCPConfig.workspace_root`;
- representative SDK-session Workspace calls are bounded by that root;
- an outside-path MCP call returns a controlled domain error without server/protocol failure;
- all 15 tool descriptors and snake_case mappings remain unchanged.

CI must remain green on Linux/Python 3.11, while local Windows coverage must verify Windows path semantics. Platform-dependent link tests may be skipped only when the operating system or permissions genuinely prevent fixture creation, with the reason explicit.

## Compatibility Policy

SAFE-0001 intentionally changes previously permissive behavior: Workspace operations that target paths outside the configured root will fail after implementation.

That change is accepted as a security boundary, but no unrelated filesystem semantics should be normalized in the same milestone. For example, the existing platform-dependent `Path.rename()` conflict behavior remains separate unless a distinct contract changes it.

Git and Python tools are not automatically brought under the Workspace path boundary by this milestone. Any cross-tool path policy requires separate design because their subprocess and package semantics differ.

## Failure Classes

Implementation failures must be classified before broad changes:

A. ROOT CONFIGURATION — invalid, missing, or incorrectly captured root.
B. RELATIVE PATH RESOLUTION — incorrect interpretation of caller-relative paths.
C. ABSOLUTE PATH CONTAINMENT — incorrect in-root/outside-root decision.
D. NONEXISTENT TARGET — unsafe or incorrect prospective path validation.
E. LINK ESCAPE — symlink/junction/reparse-point bypass or false rejection.
F. ROOT PROTECTION — workspace root can be moved or deleted.
G. SERVICE INJECTION — active MCP handlers are not using the configured bounded service.
H. ERROR CONTRACT — wrong exception or outside-path information leak ordering.
I. PLATFORM PORTABILITY — Windows/Linux path behavior differs from the approved contract.
J. MCP REGRESSION — descriptor, mapping, result-shape, or protocol regression.
K. UNKNOWN — evidence does not yet identify the failure class.

## Non-Goals

SAFE-0001 V1 does not include:

- new Workspace tools;
- tool renaming or schema redesign;
- Git/Python tool sandboxing;
- remote filesystem support;
- per-client roots or multiple simultaneous roots;
- runtime root switching;
- allowlists of selected subdirectories;
- content scanning or file-type policy;
- filesystem quotas;
- OS-level sandboxing, containers, ACL management, or race-proof capability security;
- normalization of unrelated platform-dependent filesystem behavior;
- release publishing or deployment changes.

## Completion Criteria

SAFE-0001 becomes **COMPLETE / VERIFIED** only when:

1. the active MCP Workspace service is constructed with and enforces `MCPConfig.workspace_root`;
2. relative and absolute in-root paths work according to existing operation contracts;
3. traversal, absolute outside paths, and link-based escapes are rejected fail-closed;
4. prospective write/create destinations cannot escape through parent resolution;
5. both move endpoints are independently authorized;
6. workspace root move/delete are prohibited;
7. boundary violations use controlled `WorkspacePermissionError` behavior;
8. Workspace MCP names, schemas, and successful return shapes remain stable;
9. isolated service and representative SDK-session tests cover success/error paths;
10. Linux CI passes and Windows-local verification covers platform path behavior;
11. pytest, Ruff, mypy, and `git diff --check` are green; and
12. documentation records the implemented behavior without claiming an OS-level sandbox.

## Implementation Boundary

This document is the design contract only. SAFE-0001 implementation must be a separate atomic change after review and merge of this contract.
