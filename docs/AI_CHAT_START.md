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

After reading them, continue from `CURRENT_STATUS.md`; it is authoritative for current state.

## Current Working State

AI-Engineering has completed and verified AUTO-0001 through AUTO-0009. AUTO-0010 stages 01–05 are COMPLETE / VERIFIED; AUTO-0010-06 final evidence/documentation reconciliation is active.

Permanent reconciliation boundaries:

```text
ai-engineering project reconcile plan --project PATH
ai-engineering project reconcile apply --project PATH --step SEQUENCE
ai-engineering project reconcile run --project PATH [--max-steps N]
ai-engineering project reconcile run --project PATH --policy POLICY.toml [--max-steps N]
```

AUTO-0007 is permanently read-only. AUTO-0008 remains the sole guarded one-step apply boundary. AUTO-0009 is bounded orchestration over repeated fresh planning plus exactly one AUTO-0008 apply per iteration. AUTO-0010 policy can only restrict those existing authorities.

Verified implementation baseline entering AUTO-0010-06:

```text
master = 272b9328a819f9a4fc281f41aed9970cd05e208f
```

PR #110 merged AUTO-0010-05 and passed Quality #222 plus exact post-merge Quality #223.

## Active Milestone

AUTO-0010-06 — Final Evidence / Documentation Reconciliation.

Read `AUTO-0010_RECONCILIATION_POLICY_DESIGN.md` and `AUTO-0010_FINAL_EVIDENCE.md`.

```text
AUTO-0010-01 design                  COMPLETE / VERIFIED
AUTO-0010-02 policy core             COMPLETE / VERIFIED
AUTO-0010-03 safety invariants       COMPLETE / VERIFIED
AUTO-0010-04 orchestration + CLI     COMPLETE / VERIFIED
AUTO-0010-05 installed distribution  COMPLETE / VERIFIED
AUTO-0010-06 final reconciliation    IN PROGRESS
```

## AUTO-0010 Guardrails

- Policy is an explicit restriction layer, never execution authority.
- Fresh policy loading/evaluation occurs before every candidate write.
- Invalid/unknown/contradictory policy fails closed.
- Refused candidate writes do not occur; earlier successful orchestration progress remains truthful.
- The stricter of CLI and policy progress limits applies.
- No arbitrary commands/scripts/plugins, network policy retrieval, new workflows, force/stale bypass, direct Git mutation, publication, or rollback guarantee.
- AUTO-0007/AUTO-0008/AUTO-0009 authority boundaries remain unchanged.

## General Engineering Guardrails

- Preserve originals.
- Extend, never replace.
- Documentation before implementation.
- Keep changes small, testable, deterministic, and reviewable.
- Make compatibility and security claims only from recorded evidence.
- Treat published tags/releases as immutable historical evidence.
