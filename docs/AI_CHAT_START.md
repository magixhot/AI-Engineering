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

After reading them, continue from `CURRENT_STATUS.md` and the current roadmap. `CURRENT_STATUS.md` is authoritative for current state.

## Current Working State

AI-Engineering has completed and verified AUTO-0001 through AUTO-0008 for their approved scopes. AUTO-0009 stages 01–05 are COMPLETE / VERIFIED; stage 06 final documentation reconciliation is active.

Permanent reconciliation boundaries:

```text
ai-engineering project reconcile plan --project PATH
ai-engineering project reconcile apply --project PATH --step SEQUENCE
ai-engineering project reconcile run --project PATH [--max-steps N]
```

AUTO-0007 is permanently read-only. AUTO-0008 remains the sole guarded one-step apply boundary. AUTO-0009 is bounded orchestration over repeated fresh planning plus exactly one AUTO-0008 apply per iteration.

Verified baseline entering AUTO-0009-06:

```text
master = 9564f8ffdc869bb0d8058f74c78c1e5138e5a37c
```

AUTO-0009-05 merged in PR #103 and passed Quality #201 plus post-merge Quality #202 on that exact commit.

## Active Milestone

**AUTO-0009-06 — Final Evidence / Documentation Reconciliation**

Read `AUTO-0009_MULTI_STEP_RECONCILIATION_ORCHESTRATION_DESIGN.md` for the orchestration contract.

```text
AUTO-0009-01 design                  COMPLETE / VERIFIED
AUTO-0009-02 orchestrator core       COMPLETE / VERIFIED
AUTO-0009-03 safety invariants       COMPLETE / VERIFIED
AUTO-0009-04 public CLI              COMPLETE / VERIFIED
AUTO-0009-05 installed distribution  COMPLETE / VERIFIED
AUTO-0009-06 final reconciliation    IN PROGRESS
```

## AUTO-0009 Guardrails

- Fresh AUTO-0007 planning before every mutation.
- Exactly one AUTO-0008 delegated apply per orchestration iteration.
- Canonical deterministic ordering only.
- Finite progress bound; public default 8, hard maximum 100.
- Stop fail-closed on stale, manual-review, unsupported, failed, or limit-reached state.
- No arbitrary step list, parallel writes, `force`, stale bypass, new migration edges, publication, or direct Git mutation authority.
- Partial progress must be reported truthfully; no invented whole-run atomicity or rollback guarantee.

## General Engineering Guardrails

- Preserve originals.
- Extend, never replace.
- Documentation before implementation.
- Keep changes small, testable, deterministic, and reviewable.
- Make compatibility and security claims only from recorded evidence.
- Treat published tags/releases as immutable historical evidence.
