# AI-Engineering Roadmap

## Completed / Verified

The documentation foundation, MCP foundation, SDK-0001, TOOL-0001, REL-0001/REL-0002/REL-0003, CI-0001, SAFE-0001/SAFE-0002, and AUTO-0001 through AUTO-0009 are COMPLETE / VERIFIED for their approved scopes.

AUTO-0007 remains the permanent read-only reconciliation planner. AUTO-0008 remains the guarded one-step apply boundary. AUTO-0009 is bounded multi-step orchestration. AUTO-0010 adds only a restrictive policy gate over those existing authorities.

## AUTO-0010 — Reconciliation Policy

**Status:** STAGE 06 IN PROGRESS; STAGES 01–05 COMPLETE / VERIFIED

Public policy-enabled command:

```text
ai-engineering project reconcile run --project PATH --policy POLICY.toml [--max-steps N]
```

Policy can only restrict already-supported workflows and observable Git conditions. It is freshly evaluated before each candidate mutation, fails closed on invalid/unknown/contradictory input, and cannot grant execution authority by itself. The stricter of CLI and policy progress limits applies.

### Delivery Evidence

- AUTO-0010-01 — PR #106; Quality #207; post-merge #208.
- AUTO-0010-02 — PR #107; corrected Quality #211; post-merge #212.
- AUTO-0010-03 — PR #108; corrected Quality #214; post-merge #215.
- AUTO-0010-04 — PR #109; corrected Quality #220; post-merge #221.
- AUTO-0010-05 — PR #110; Quality #222; post-merge #223.
- AUTO-0010-06 — Final Evidence / Documentation Reconciliation — IN PROGRESS.

Verified implementation baseline entering stage 06:

```text
master = 272b9328a819f9a4fc281f41aed9970cd05e208f
```

## Delivery Gates

AUTO-0010 stages execute strictly in order:

`01 → 02 → 03 → 04 → 05 → 06`

Stage 06 must pass its pre-merge Quality gate, merge, and exact post-merge Quality gate before AUTO-0010 can be marked COMPLETE / VERIFIED.

## Current Priority

Close AUTO-0010-06 without widening authority. Preserve AUTO-0007 read-only planning, AUTO-0008 sole guarded one-step apply authority, AUTO-0009 bounded replan-between-writes orchestration, and AUTO-0010 policy as restriction-only.
