# AI-Engineering Roadmap

## Completed / Verified

The documentation foundation, MCP foundation, SDK-0001, TOOL-0001, REL-0001/REL-0002/REL-0003, CI-0001, SAFE-0001/SAFE-0002, and AUTO-0001 through AUTO-0012 are COMPLETE / VERIFIED for their approved scopes.

AUTO-0007 remains the permanent read-only reconciliation planner. AUTO-0008 remains the guarded one-step apply boundary. AUTO-0009 is bounded multi-step orchestration. AUTO-0010 adds only a restrictive policy gate. AUTO-0011 adds only an optional explicit single-candidate approval gate. AUTO-0012 adds deterministic execution receipts/evidence only and does not add authority.

## AUTO-0012 — Deterministic Reconciliation Execution Evidence / Receipts

**Status:** COMPLETE / VERIFIED

Public receipt-enabled execution:

```text
ai-engineering project reconcile run --project PATH [--max-steps N] [--policy POLICY.toml] [--approval APPROVAL.json] --receipt-json
```

Receipt v1 is canonical deterministic machine-readable evidence for one reconciliation run. It records bounded execution context and already-observed results, including policy/approval evidence and delegated apply attempts, and carries a SHA-256 digest over the canonical payload excluding the digest field.

Receipt construction is observational only. A receipt cannot grant execution authority, replace policy or approval, select/reorder candidates, trigger mutation, retry/resume, perform rollback, bypass stale-state guards, or publish Git/release artifacts.

### Delivery Evidence

- AUTO-0012-01 — PR #121; Quality #248; post-merge #249.
- AUTO-0012-02 — PR #122; corrected Quality #251; post-merge #252.
- AUTO-0012-03 — PR #123; Quality #253; post-merge #254.
- AUTO-0012-04 — PR #124; corrected Quality #257; post-merge #258.
- AUTO-0012-05 — PR #125; corrected Quality #260; post-merge #261.
- AUTO-0012-06 — final evidence/documentation reconciliation only; no authority expansion.

Verified implementation baseline before final documentation reconciliation:

```text
2268f4c8278f3c81b5735e26337984aebd300c6b
```

That commit and its exact post-merge Quality #261 are historical verification evidence only; later repository progress does not invalidate AUTO-0012 closure.

## Delivery Gates

AUTO-0012 stages execute in order:

`01 → 02 → 03 → 04 → 05 → 06`

Stages 01–05 completed their required corrected pre-merge and exact post-merge Quality gates where applicable. Stage 06 reconciles documentation against the verified implementation baseline.

## Current Priority

No AUTO capability milestone is active after AUTO-0012 closure. Preserve AUTO-0007 read-only planning, AUTO-0008 sole guarded one-step apply authority, AUTO-0009 bounded replan-between-writes orchestration, AUTO-0010 restriction-only policy, AUTO-0011 approval as an additional fail-closed single-candidate gate, and AUTO-0012 receipts as evidence only. Any next capability milestone must begin with a separate design/contract.
