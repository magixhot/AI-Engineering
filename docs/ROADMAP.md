# AI-Engineering Roadmap

## Completed

### Sprint 0 — Documentation Foundation

**Status:** COMPLETED

The core project documentation foundation has been established and is maintained as part of the delivery workflow.

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

### AUTO-0007 Engineering Project Reconciliation Plan

**Status:** IN PROGRESS

AUTO-0007 composes the existing project identity, inspection, documentation ownership/synchronization, migration readiness, and Git invariants into a deterministic, read-only reconciliation planner. The contract is explicitly fail-closed and does not add write/apply authority, publication scope, or a new migration edge.

#### AUTO-0007-01 — Reconciliation Planner Design

**Status:** COMPLETE / VERIFIED

The authoritative design defines the planner contract, supported plan states, ordered steps, blockers/issues, affected paths, reinspection boundaries, expected-state semantics, determinism, and Git/project-byte preservation requirements.

#### AUTO-0007-02 — Planner Implementation

**Status:** COMPLETE / VERIFIED

PR #83 merged. Post-merge Quality #147 passed. The resulting master base for the invariant stage was `006e1677efae525207e49d8c1eb3f1429583c603`.

#### AUTO-0007-03 — Reconciliation Invariants

**Status:** COMPLETE / VERIFIED

Test-only stage. It verifies manual-review/unsupported fail-closed behavior, determinism, ordering, project-byte preservation, and Git invariants without changing production code, CLI authority, write authority, or publication scope.

PR #84 merged at `cbbfc382d5b094a21ae3e7dc9d7fc441f12df569`. Quality #148 and post-merge Quality #149 passed.

#### AUTO-0007-04 — Public CLI

**Status:** IN PROGRESS

PR #85 is active on `agent/auto-0007-04-public-cli` at head `cbb961dd4bd76547254de027cc380a354bbb8ca1`.

The stage exposes:

```text
ai-engineering project reconcile plan --project PATH
```

The CLI preserves the planner's deterministic `key=value` representation, plan states, ordered steps, blockers, affected paths, reinspection boundaries, expected-state semantics, and fail-closed exit behavior. It adds no apply/write authority.

Quality #150 is currently in progress. AUTO-0007-05 does not start until #150 succeeds, PR #85 merges, and the post-merge gate passes.

#### AUTO-0007-05 — Installed Distribution Verification

**Status:** PLANNED

Verify the real installed-wheel/public CLI path for the reconciliation planner, including representative clean/ready/manual-review/unsupported states, deterministic output and controlled exit codes, and preservation of project bytes and Git invariants.

#### AUTO-0007-06 — Final Reconciliation / Documentation

**Status:** PLANNED

Reconcile the authoritative project documentation with the final AUTO-0007 implementation/evidence and close the milestone before selecting the next milestone.

### SAFE-0002 Git/Python Execution Safety

**Status:** COMPLETE / VERIFIED

SAFE-0002 binds active MCP Git and path-taking Python operations to `MCPConfig.workspace_root` and preserves the approved subprocess and path safety boundary. SAFE-0002 remains a bounded execution contract, not an operating-system sandbox.

## Current Priority

Complete AUTO-0007-04 Public CLI while preserving the established read-only, deterministic, fail-closed reconciliation boundary. After Quality #150 succeeds, merge PR #85, run the post-merge gate, then proceed to AUTO-0007-05 installed distribution verification.

Documentation is reconciled at every milestone boundary. A stage is not considered fully closed until implementation evidence, quality/post-merge evidence, and authoritative documentation agree.

## Planned

### Client and IDE Interoperability

Validate interoperability with additional MCP clients and IDE integration surfaces. VS Code 1.132.1 and Antigravity are already verified for their recorded contracts; other clients remain unverified until separately evidenced.

### Future Engineering Capabilities

Potential future work includes additional bootstrap profiles, additional explicit production migration edges, new bounded execution tools, publication expansion, additional client/IDE interoperability, and additional engineering automation. None of these are implied by existing verified contracts and each requires its own approved design and evidence.
