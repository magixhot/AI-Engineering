# AI-Engineering Roadmap

## Completed

### Sprint 0 — Documentation Foundation

**Status:** COMPLETED

The core project documentation foundation has been established.

## Implemented / Verified

### Sprint 1 — MCP Foundation

**Status:** IMPLEMENTED / VERIFIED

Implemented repository components include MCP bootstrap, the official SDK adapter, Composite
Registry, Runtime, Discovery, STDIO, diagnostics, and registered Workspace/Git/Python tool
subsystems. Runtime and Discovery remain repository subsystems, not steps in the active SDK request
path.

### Official Python MCP SDK Migration

**Status:** COMPLETE

The official Python MCP SDK is integrated as the protocol/server boundary. MCP-0002 automated
contracts, VS Code 1.132.1 manual interoperability, and the separately recorded Antigravity contract
are verified. This does not replace the internal Runtime, Registry, or Discovery subsystems.

### SDK-0001 Project Templates V1, SDK-0001.1 Python Scaffold, and SDK-0001.2 CLI

**Status:** COMPLETE / VERIFIED

The document-first standalone project template, optional generic Python scaffold, and installed
`ai-engineering project create` frontend are implemented and verified.

### AUTO-0001 Engineering Project Bootstrap

**Status:** COMPLETE / VERIFIED

AUTO-0001 adds the bounded `python-engineering` bootstrap workflow over SDK-0001, including typed
API, fail-closed post-generation verification, installed `ai-engineering project bootstrap`, and
isolated-wheel evidence.

### AUTO-0002 Project Documentation Synchronization

**Status:** COMPLETE / VERIFIED

AUTO-0002 adds deterministic local project inspection, documentation drift detection, explicit
synchronization planning, SHA-256 guarded ownership-preserving apply, post-apply verification, and
the installed commands:

```text
ai-engineering project docs check --project PATH
ai-engineering project docs plan --project PATH
ai-engineering project docs apply --project PATH
```

V1 writes only machine-owned sections of `CURRENT_STATUS.md`, `MASTER_INDEX.md`, and
`PROJECT_MAP.md`. Missing or malformed ownership markers require manual review. The workflow does not
stage or commit Git changes, execute project code, install dependencies, contact remote services, or
initialize markers automatically.

### AUTO-0003 Documentation Ownership Initialization

**Status:** COMPLETE / VERIFIED

AUTO-0003 provides the explicit initialization layer for the three AUTO-0002 writable documents when
the approved marker pair is completely absent and deterministic initialization is safe. It provides
ownership-state classification, deterministic read-only planning, SHA-256 guarded apply, staged
replacement/rollback behavior, post-write verification, AUTO-0002 handoff verification, idempotency,
and Git HEAD/index invariants.

Installed commands are:

```text
ai-engineering project docs ownership check --project PATH
ai-engineering project docs ownership plan --project PATH
ai-engineering project docs ownership apply --project PATH
```

Partial, duplicate, malformed, unsupported, missing-document, mixed-newline, and stale-plan states
fail closed. Existing AUTO-0002 commands remain unchanged and never initialize markers implicitly.
The ownership workflow is exercised through an isolated installed wheel outside the source checkout.
Verification evidence is recorded in `AUTO-0003_VERIFICATION_EVIDENCE.md`.

### SAFE-0002 Git/Python Execution Safety

**Status:** COMPLETE / VERIFIED

SAFE-0002 binds active MCP Git and path-taking Python operations to `MCPConfig.workspace_root`.
Bounded Git requires the configured workspace root to be the repository top level and rejects parent
repository discovery above the authority root. Bounded Python rejects outside, traversal, and
supported link escapes before inspection or pytest execution. Authorized pytest uses the current
interpreter, workspace-root cwd, `shell=False`, closed stdin, captured output, and a bounded timeout.

Linux CI verifies the full link-escape path. Final Windows-local evidence records 153 passed and two
privilege-dependent symlink-fixture skips (`WinError 1314`), with Ruff, mypy, diff-check, and working
tree cleanliness passing. SAFE-0002 is not an operating-system sandbox and does not contain malicious
code already authorized to execute inside the workspace.

## Current Priority

Preserve the verified MCP, SDK-0001, SAFE-0001, SAFE-0002, CI-0001, release, AUTO-0001, AUTO-0002,
and AUTO-0003 contracts. Select the next engineering milestone from a fresh post-AUTO-0003 roadmap
audit rather than implicitly expanding documentation ownership, execution surfaces, client claims,
or release scope.

## Planned

### Client and IDE Interoperability

Validate interoperability with additional MCP clients and IDE integration surfaces. VS Code 1.132.1
and Antigravity are already verified for their recorded contracts; ChatGPT/OpenAI, Claude Desktop,
and other clients remain unverified.

### Future Engineering Capabilities

Potential future work includes additional bootstrap profiles, broader project update/migration
behavior, new bounded execution tools, publication expansion, additional client/IDE interoperability,
and additional engineering automation. None of these are implied by existing verified contracts and
each requires its own approved design and evidence.
