# AI-Engineering Roadmap

## Completed / Verified

The documentation foundation, MCP foundation, SDK-0001 project templates/scaffold/CLI, TOOL-0001 core tool verification, REL-0001/REL-0002/REL-0003 release work, CI-0001 quality gates, SAFE-0001/SAFE-0002 safety boundaries, and AUTO-0001 through AUTO-0007 are COMPLETE / VERIFIED for their approved scopes.

## AUTO-0007 — Engineering Project Reconciliation Plan

**Status:** COMPLETE / VERIFIED

AUTO-0007 composes existing project identity, inspection, documentation ownership/synchronization, migration readiness, and Git invariants into a deterministic, read-only reconciliation planner. The contract is fail-closed and adds no write/apply authority, new migration edge, or publication behavior.

Public planning command:

```text
ai-engineering project reconcile plan --project PATH
```

AUTO-0007 remains permanently read-only under AUTO-0008.

## AUTO-0008 — Guarded Project Reconciliation Apply

**Status:** IN PROGRESS — AUTO-0008-01 DESIGN

AUTO-0008 defines a separate guarded execution boundary for applying an exact eligible reconciliation step through an already-approved subsystem write primitive. It does not add write behavior to AUTO-0007 and does not authorize arbitrary writes, commands, new migration edges, publication, `apply all`, `force`, or stale-plan bypass behavior.

### AUTO-0008-01 — Apply Design / Authority Contract

**Status:** IN PROGRESS

Documentation-only stage. Defines authority mapping, eligibility, stale-plan detection, Git/workspace safety, one-step execution, mandatory reinspection, failure/rollback reporting, deterministic result semantics, CLI boundaries, verification matrix, and Definition of Done.

No production code or write authority changes are allowed in this stage.

### AUTO-0008-02 — Guarded Executor Core

**Status:** PLANNED / BLOCKED

Typed core executor only. May delegate one exact eligible reconciliation step to an existing approved apply primitive. No public CLI in this stage.

### AUTO-0008-03 — Stale Plan / Failure / Git Safety Invariants

**Status:** PLANNED / BLOCKED

Verification of zero-write stale/manual-review/unsupported behavior, deterministic eligibility/refusal, Git/workspace preservation outside delegated scope, bounded failure/rollback evidence, and mandatory reinspection boundaries.

### AUTO-0008-04 — Public CLI

**Status:** PLANNED / BLOCKED

Planned bounded command:

```text
ai-engineering project reconcile apply --project PATH --step SEQUENCE
```

Final CLI shape is gated by the verified core/invariant contract. No `apply all`, `force`, stale bypass, arbitrary workflow, publication, or hidden interactive write path is permitted.

### AUTO-0008-05 — Installed Distribution Verification

**Status:** PLANNED / BLOCKED

Build/install isolated wheel and verify the installed public apply path without source-tree leakage, while preserving the same authority and safety boundaries.

### AUTO-0008-06 — Final Evidence / Documentation Reconciliation

**Status:** PLANNED / BLOCKED

Reconcile implementation, Quality/post-merge evidence, installed-distribution verification, and authoritative documentation before milestone closure.

## Delivery Gates

AUTO-0008 stages execute strictly in order:

`01 → 02 → 03 → 04 → 05 → 06`

Each stage requires the normal Quality gate before merge and a successful post-merge Quality gate before the next stage begins.

## Current Priority

Complete AUTO-0008-01 without production changes. Preserve AUTO-0007 read-only behavior and make the new execution authority explicit, narrow, one-step, stale-safe, fail-closed, and delegated to existing approved subsystem write APIs.

A stage is not fully closed until implementation/design evidence, Quality/post-merge evidence, and authoritative documentation agree.
