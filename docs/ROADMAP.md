# AI-Engineering Roadmap

## Completed

### Sprint 0 — Documentation Foundation

**Status:** COMPLETED

The core project documentation foundation has been established.

## Implemented / Verified

### Sprint 1 — MCP Foundation

**Status:** IMPLEMENTED / VERIFIED

Implemented repository components include MCP bootstrap, the official SDK adapter, Composite Registry, Runtime, Discovery, STDIO, diagnostics, and registered Workspace/Git/Python tool subsystems. Runtime and Discovery remain repository subsystems, not steps in the active SDK request path.

### Official Python MCP SDK Migration

**Status:** COMPLETE

The official Python MCP SDK is integrated as the protocol/server boundary. MCP-0002 automated contracts, VS Code 1.132.1 manual interoperability, and the separately recorded Antigravity contract are verified.

### SDK-0001 Project Templates V1, SDK-0001.1 Python Scaffold, and SDK-0001.2 CLI

**Status:** COMPLETE / VERIFIED

The document-first standalone project template, optional generic Python scaffold, and installed `ai-engineering project create` frontend are implemented and verified.

### AUTO-0001 Engineering Project Bootstrap

**Status:** COMPLETE / VERIFIED

AUTO-0001 provides the bounded `python-engineering` bootstrap workflow over SDK-0001, including typed API, fail-closed verification, installed CLI, and isolated-wheel evidence.

### AUTO-0002 Project Documentation Synchronization

**Status:** COMPLETE / VERIFIED

AUTO-0002 provides deterministic local project inspection, documentation drift detection, explicit synchronization planning, SHA-256 guarded ownership-preserving apply, post-apply verification, and installed `project docs check|plan|apply` commands.

### AUTO-0003 Documentation Ownership Initialization

**Status:** COMPLETE / VERIFIED

AUTO-0003 provides explicit deterministic initialization of approved AUTO-0002 ownership markers, guarded apply/rollback, handoff verification, idempotency, Git invariants, and installed ownership CLI verification. Evidence: `AUTO-0003_VERIFICATION_EVIDENCE.md`.

### AUTO-0004 Engineering Project Update / Migration Framework

**Status:** COMPLETE / VERIFIED

AUTO-0004 provides the bounded framework for updating positively identified engineering projects without rewriting or guessing human-owned content. The verified contract includes explicit named migration contracts, deterministic read-only planning, ownership/change-state classification, SHA-256 guards, guarded atomic create/replace/delete operations, rollback verification, idempotency, and Git HEAD/branch/index/remotes invariants.

Installed commands are:

```text
ai-engineering project migrate check --project PATH --migration ID
ai-engineering project migrate plan --project PATH --migration ID
ai-engineering project migrate apply --project PATH --migration ID
```

Evidence: `AUTO-0004_VERIFICATION_EVIDENCE.md`.

### AUTO-0005 Python Engineering Baseline V2 / First Production Migration

**Status:** COMPLETE / VERIFIED

AUTO-0005 defines `python-engineering-v2` as the active engineering bootstrap baseline and registers the first production migration edge, `python-engineering-v1-to-v2`.

New `python-engineering` bootstraps create `.ai-engineering.toml` and the V2 `.gitignore` in the same initial Git commit. The generic SDK-0001/SDK-0001.1 scaffold remains separate and compatible with the legacy V1 fixture contract.

Project identity positively recognizes supported V1 and V2 projects. Malformed or unapproved V2 identity markers fail closed. The production registry contains exactly the approved V1-to-V2 edge, which touches only `.ai-engineering.toml` and exact machine-owned `.gitignore` content using existing AUTO-0004 operation types.

Installed-wheel verification proves the public CLI path from a legacy V1 project through `check`, `plan`, and guarded `apply`, then verifies V2 identity, unchanged Git HEAD/staged index, approved working-tree changes only, and idempotent repeated plan/apply. Unsupported migration ids remain controlled fail-closed errors.

Evidence: `AUTO-0005_VERIFICATION_EVIDENCE.md`.

### AUTO-0006 Engineering Project Health / Readiness Audit

**Status:** COMPLETE / VERIFIED

AUTO-0006 provides one deterministic read-only entry point for engineering project readiness. It composes existing project inspection, documentation ownership/synchronization, migration readiness, and bounded Git observations into a typed health report without modifying the target project.

Installed command:

```text
ai-engineering project health --project PATH
```

Stable overall states are `healthy`, `action_required`, `manual_review`, and `unsupported`. Next-action recommendations point only to already-approved workflows. Dirty staged/unstaged/untracked Git state is observable but is not by itself an automatic blocker.

Installed-wheel verification covers V1 action-required, V2 healthy, and unsupported states; deterministic output/exit codes; controlled traceback-free failures; and preservation of Git HEAD, branch, staged index, working-tree status, and remotes.

Evidence: `AUTO-0006_VERIFICATION_EVIDENCE.md`.

### SAFE-0002 Git/Python Execution Safety

**Status:** COMPLETE / VERIFIED

SAFE-0002 binds active MCP Git and path-taking Python operations to `MCPConfig.workspace_root` and preserves the approved subprocess and path safety boundary. SAFE-0002 remains a bounded execution contract, not an operating-system sandbox.

## Current Priority

Preserve the verified MCP, SDK-0001, SAFE-0001, SAFE-0002, CI-0001, release, and AUTO-0001 through AUTO-0006 contracts. Select the next engineering milestone from a fresh post-AUTO-0006 roadmap audit rather than implicitly expanding migration scope, execution surfaces, client claims, bootstrap profiles, or publication scope.

## Planned

### Client and IDE Interoperability

Validate interoperability with additional MCP clients and IDE integration surfaces. VS Code 1.132.1 and Antigravity are already verified for their recorded contracts; other clients remain unverified until separately evidenced.

### Future Engineering Capabilities

Potential future work includes additional bootstrap profiles, additional explicit production migration edges, new bounded execution tools, publication expansion, additional client/IDE interoperability, and additional engineering automation. None of these are implied by existing verified contracts and each requires its own approved design and evidence.
