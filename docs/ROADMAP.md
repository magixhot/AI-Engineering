# AI-Engineering Roadmap

## Completed / Verified

The documentation foundation, MCP foundation, SDK-0001, TOOL-0001, REL-0001/REL-0002/REL-0003, CI-0001, SAFE-0001/SAFE-0002, and AUTO-0001 through AUTO-0010 are COMPLETE / VERIFIED for their approved scopes.

AUTO-0007 remains the permanent read-only reconciliation planner. AUTO-0008 remains the guarded one-step apply boundary. AUTO-0009 is bounded multi-step orchestration. AUTO-0010 adds only a restrictive policy gate over those existing authorities.

## AUTO-0011 — Reconciliation Approval

**Status:** CLOSURE IN PROGRESS — stages 01–05 COMPLETE / VERIFIED

Public approval-enabled commands:

```text
ai-engineering project reconcile approve --project PATH [--policy POLICY.toml]
ai-engineering project reconcile run --project PATH --approval APPROVAL.json [--policy POLICY.toml] [--max-steps N]
```

AUTO-0011 adds an optional explicit approval gate as another necessary condition before the existing guarded mutation path. The deterministic artifact binds one canonical candidate to portable project identity, Git HEAD/branch state, and explicit policy context. Malformed, stale, or mismatched approval fails closed before that candidate write.

Approval cannot expand workflow authority, override AUTO-0010 policy, bypass Git guards, or approve an entire orchestration run. Fresh replanning means a later candidate requires a fresh matching approval.

### Delivery Evidence

- AUTO-0011-01 — PR #113; Quality #228; post-merge #229.
- AUTO-0011-02 — PR #114; corrected Quality #232; post-merge #233.
- AUTO-0011-03 — PR #115; corrected Quality #235; post-merge #236.
- AUTO-0011-04 — PR #116; corrected Quality #238; post-merge #239.
- AUTO-0011-05 — PR #117; Quality #240; post-merge #241.
- AUTO-0011-06 — documentation-only final evidence/reconciliation; closure gate in progress.

Verified implementation baseline entering stage 06:

```text
master = 2d181d38d26087bb672eaaa0691b27f071353eb7
```

## Delivery Gates

AUTO-0011 stages execute strictly in order:

`01 → 02 → 03 → 04 → 05 → 06`

Stages 01 through 05 completed their required pre-merge and exact post-merge Quality gates. Stage 06 must also pass both gates before AUTO-0011 can be marked fully COMPLETE / VERIFIED.

## Current Priority

Complete AUTO-0011-06 as documentation-only closure. Preserve AUTO-0007 read-only planning, AUTO-0008 sole guarded one-step apply authority, AUTO-0009 bounded replan-between-writes orchestration, AUTO-0010 restriction-only policy, and AUTO-0011 approval as an additional fail-closed gate rather than authority.
