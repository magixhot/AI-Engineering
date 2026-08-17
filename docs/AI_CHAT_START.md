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

AI-Engineering has completed and verified AUTO-0001 through AUTO-0012 for their approved scopes.

Permanent reconciliation boundaries:

```text
ai-engineering project reconcile plan --project PATH
ai-engineering project reconcile apply --project PATH --step SEQUENCE
ai-engineering project reconcile run --project PATH [--max-steps N]
ai-engineering project reconcile run --project PATH --policy POLICY.toml [--max-steps N]
ai-engineering project reconcile approve --project PATH [--policy POLICY.toml]
ai-engineering project reconcile run --project PATH --approval APPROVAL.json [--policy POLICY.toml] [--max-steps N]
ai-engineering project reconcile run --project PATH [--max-steps N] [--policy POLICY.toml] [--approval APPROVAL.json] --receipt-json
```

AUTO-0007 is permanently read-only. AUTO-0008 remains the sole guarded one-step apply boundary. AUTO-0009 is bounded orchestration over repeated fresh planning plus exactly one AUTO-0008 apply per iteration. AUTO-0010 policy can only restrict those existing authorities. AUTO-0011 approval is an optional additional single-candidate gate and cannot grant new mutation authority. AUTO-0012 receipts are deterministic execution evidence only and cannot grant or substitute for authority.

AUTO-0012 implementation completed through PR #125, corrected Quality #260, and exact post-merge Quality #261. The verified implementation baseline `2268f4c8278f3c81b5735e26337984aebd300c6b` is historical verification evidence rather than a requirement that future `master` remain unchanged.

## Active Milestone

No AUTO capability milestone is active after AUTO-0012 documentation closure.

Read `AUTO-0012_RECONCILIATION_EXECUTION_EVIDENCE_DESIGN.md` and `AUTO-0012_FINAL_EVIDENCE.md` for the verified receipt contract and closure evidence.

```text
AUTO-0012-01 design/contract             COMPLETE / VERIFIED
AUTO-0012-02 typed receipt model         COMPLETE / VERIFIED
AUTO-0012-03 evidence projection         COMPLETE / VERIFIED
AUTO-0012-04 public CLI integration      COMPLETE / VERIFIED
AUTO-0012-05 installed distribution      COMPLETE / VERIFIED
AUTO-0012-06 final reconciliation        DOCUMENTATION CLOSURE
```

Any next AUTO capability must begin with a separate design/contract before production implementation.

## AUTO-0012 Guardrails

- Receipt v1 is canonical deterministic machine-readable evidence for one reconciliation run.
- Receipt construction is a pure observational projection from already-observed orchestration evidence plus bounded read-only context.
- A receipt or its SHA-256 digest is never an authority token and cannot replace AUTO-0010 policy or AUTO-0011 approval.
- Receipt generation cannot choose/reorder candidates, change bounds/policy, approve, invoke mutation, retry/resume, suppress failure, rollback, or mutate Git/project state.
- Without explicit `--receipt-json`, existing reconciliation run behavior remains compatible.
- No receipt-file application writes, signatures/PKI, key management, remote logging, trusted timestamps, replay/resume, force/stale bypass, new workflows, direct Git publication, or release/publication authority.

## General Engineering Guardrails

- Preserve originals.
- Extend, never replace.
- Documentation before implementation.
- Keep changes small, testable, deterministic, and reviewable.
- Make compatibility and security claims only from recorded evidence.
- Treat published tags/releases as immutable historical evidence.
