# AI-Engineering

## Chat Bootstrap

For a new or continued session, restore context in this order:

1. `README.md`
2. `PROJECT_CONTEXT.md`
3. `PROJECT_MAP.md`
4. `CURRENT_STATUS.md`
5. `ROADMAP.md`
6. `DECISIONS.md`
7. `CODING_STANDARDS.md`
8. `MASTER_INDEX.md`
9. The design/evidence document for the active milestone listed in `MASTER_INDEX.md`, if one exists

After reading them, continue from `CURRENT_STATUS.md` and the current roadmap. `CURRENT_STATUS.md` is the authoritative current-state document.

## Current Working State

AI-Engineering has completed and verified AUTO-0001 through AUTO-0007 for their approved scopes. AUTO-0007 remains a deterministic, fail-closed, read-only reconciliation planner exposed through:

```text
ai-engineering project reconcile plan --project PATH
```

AUTO-0008 stages 01 through 05 are COMPLETE / VERIFIED. The current verified implementation baseline entering the final reconciliation stage is `35196bde98e8436265dd85ac397e4fc6b6f51037`, verified by AUTO-0008-05 Quality #183 and post-merge Quality #184.

## Active Milestone

AUTO-0008 — Guarded Project Reconciliation Apply is active at **AUTO-0008-06 — Final Evidence / Documentation Reconciliation**.

Read `AUTO-0008_GUARDED_PROJECT_RECONCILIATION_APPLY_DESIGN.md` for the authority contract.

Verified public apply command:

```text
ai-engineering project reconcile apply --project PATH --step SEQUENCE
```

AUTO-0008 is a separate execution-authority boundary. It does not add write behavior to AUTO-0007. It applies at most one exact eligible reconciliation step per call and delegates only to an already-approved existing subsystem apply primitive.

```text
AUTO-0008-01 design             COMPLETE / VERIFIED
AUTO-0008-02 executor core      COMPLETE / VERIFIED
AUTO-0008-03 safety invariants  COMPLETE / VERIFIED
AUTO-0008-04 public CLI         COMPLETE / VERIFIED
AUTO-0008-05 installed wheel    COMPLETE / VERIFIED
        ↓
AUTO-0008-06 final reconciliation — ACTIVE
        ↓
Quality → merge → post-merge gate → final closure evidence
```

AUTO-0008 is not fully closed until stage 06 itself passes Quality, merge, and post-merge verification and authoritative closure evidence is recorded.

## AUTO-0008 Guardrails

- Preserve AUTO-0007 read-only behavior unchanged.
- No arbitrary file writes or arbitrary command execution.
- No new migration edges, ownership semantics, writable document classes, or publication authority.
- One actionable step per executor call.
- Reinspect current reconciliation state before delegation and after successful apply where required.
- Stale plan, unsupported identity, manual-review condition, or reinspection boundary must fail closed with zero unauthorized writes.
- Delegate mutation to the existing subsystem that already owns the approved write primitive.
- Do not claim stronger atomicity or rollback guarantees than the delegated subsystem provides.
- No `apply all`, `force`, stale-plan bypass, Git commit/tag/push behavior, TestPyPI, or PyPI behavior.

## General Engineering Guardrails

- Preserve originals.
- Extend, never replace.
- Documentation before implementation.
- Keep changes small, testable, deterministic, and reviewable.
- Keep environment-specific absolute paths out of project code and documentation contracts.
- Make compatibility and security claims only from recorded evidence.
- Treat published tags/releases as immutable historical evidence.
- Do not expand SAFE-0002 claims without a separate contract and evidence.

## Project Context

AI-Engineering is the Engineering MCP Server and engineering-automation foundation for the AI Infrastructure ecosystem. It uses the official Python MCP SDK at the protocol/server boundary while preserving the internal Runtime and Registry architecture.

Reference project: AI-Archive-Server.
