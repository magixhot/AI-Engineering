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

AI-Engineering has completed and verified AUTO-0001 through AUTO-0011 for their approved scopes.

Permanent reconciliation boundaries:

```text
ai-engineering project reconcile plan --project PATH
ai-engineering project reconcile apply --project PATH --step SEQUENCE
ai-engineering project reconcile run --project PATH [--max-steps N]
ai-engineering project reconcile run --project PATH --policy POLICY.toml [--max-steps N]
ai-engineering project reconcile approve --project PATH [--policy POLICY.toml]
ai-engineering project reconcile run --project PATH --approval APPROVAL.json [--policy POLICY.toml] [--max-steps N]
```

AUTO-0007 is permanently read-only. AUTO-0008 remains the sole guarded one-step apply boundary. AUTO-0009 is bounded orchestration over repeated fresh planning plus exactly one AUTO-0008 apply per iteration. AUTO-0010 policy can only restrict those existing authorities. AUTO-0011 approval is an optional additional single-candidate gate and cannot grant new mutation authority.

AUTO-0011 stage 06 completed through PR #118, Quality #242, and exact post-merge Quality #243. Administrative closure record PR #119 then passed Quality #244 and exact post-merge Quality #245. The recorded SHAs are historical verification evidence rather than a requirement that future `master` remain unchanged.

## Active Milestone

No AUTO capability milestone is active.

Read `AUTO-0011_RECONCILIATION_APPROVAL_DESIGN.md` and `AUTO-0011_FINAL_EVIDENCE.md` for the verified approval contract and closure evidence.

```text
AUTO-0011-01 design                   COMPLETE / VERIFIED
AUTO-0011-02 typed approval model     COMPLETE / VERIFIED
AUTO-0011-03 approval verification    COMPLETE / VERIFIED
AUTO-0011-04 guarded integration      COMPLETE / VERIFIED
AUTO-0011-05 installed distribution   COMPLETE / VERIFIED
AUTO-0011-06 final reconciliation     COMPLETE / VERIFIED
```

Any next AUTO capability must begin with a separate design/contract before production implementation.

## AUTO-0011 Guardrails

- Approval is explicit, deterministic, typed, digest-bound, and scoped to one candidate.
- Approval verification is an additional necessary gate, never sufficient mutation authority.
- Fresh candidate/Git/policy context must match the approval before the candidate write.
- Malformed, stale, unknown, or mismatched approval fails closed.
- A successful candidate is still applied only through AUTO-0008/AUTO-0009.
- Replanning after a successful write means the next candidate requires a fresh matching approval.
- AUTO-0010 remains independently restrictive and cannot be overridden by approval.
- No autonomous approval, whole-run approval, remote signing service, arbitrary commands/scripts/plugins, new workflows, force/stale bypass, direct Git mutation, publication, or rollback guarantee.

## General Engineering Guardrails

- Preserve originals.
- Extend, never replace.
- Documentation before implementation.
- Keep changes small, testable, deterministic, and reviewable.
- Make compatibility and security claims only from recorded evidence.
- Treat published tags/releases as immutable historical evidence.
