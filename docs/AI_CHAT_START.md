# AI-Engineering

<!-- canonical-project-state
{"schema_version":1,"completed_through":"AUTO-0019","active_milestone":"AUTO-0020","active_stage":"AUTO-0020-04","active_state":"IMPLEMENTATION_ACTIVE"}
-->

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

AI-Engineering has completed and verified AUTO-0001 through AUTO-0013. AUTO-0014 stages 01 through 05 are COMPLETE / VERIFIED. AUTO-0014-06 final evidence/documentation reconciliation is the only active stage.

Permanent reconciliation boundaries remain unchanged:

```text
ai-engineering project reconcile plan --project PATH
ai-engineering project reconcile apply --project PATH --step SEQUENCE
ai-engineering project reconcile run --project PATH [--max-steps N]
ai-engineering project reconcile run --project PATH --policy POLICY.toml [--max-steps N]
ai-engineering project reconcile approve --project PATH [--policy POLICY.toml]
ai-engineering project reconcile run --project PATH --approval APPROVAL.json [--policy POLICY.toml] [--max-steps N]
ai-engineering project reconcile run --project PATH [--max-steps N] [--policy POLICY.toml] [--approval APPROVAL.json] --receipt-json
```

AUTO-0007 is permanently read-only. AUTO-0008 remains the sole guarded one-step apply boundary. AUTO-0009 is bounded orchestration. AUTO-0010 policy can only restrict existing authority. AUTO-0011 approval cannot grant new mutation authority. AUTO-0012 receipts are deterministic evidence only. AUTO-0013 adds bounded read-only remote inspection/control transport. AUTO-0014 adds only local lifecycle supervision for that same worker.

## AUTO-0014 Current Gate

```text
AUTO-0014-01 design/contract                    COMPLETE / VERIFIED
AUTO-0014-02 typed runtime/service config       COMPLETE / VERIFIED
AUTO-0014-03 single-instance lifecycle          COMPLETE / VERIFIED
AUTO-0014-04 user service integration           COMPLETE / VERIFIED
AUTO-0014-05 installed service verification     COMPLETE / VERIFIED
AUTO-0014-06 final reconciliation               ACTIVE
```

PR #143 passed Quality #302, merged as `58e0b3c6cd5393386ad97871aa34f6fd9e4fef47`, and exact post-merge Quality succeeded.

Read `AUTO-0014_LOCAL_CONTROL_WORKER_SERVICE_DESIGN.md`, `AUTO-0014_05_INSTALLED_LOCAL_SERVICE_VERIFICATION.md`, and `AUTO-0014_FINAL_EVIDENCE.md` for the service contract and closure evidence.

Successful installed-service request:

```text
sha256:593eff3b7e76a65ec2399ea3988ae0895ea01c2bc608bb690bc62be46fe9baf7
```

It produced a typed `SUCCEEDED` result on branch `master` at exact HEAD `5b5b3b0ec1922685a594679ddebc199f28b6b8d5` with `pre_clean=true` and `post_clean=true`.

## AUTO-0014 Guardrails

- Worker remote task classes remain only `status`, `inspect`, `plan`, and `diff`.
- OpenCode remains localhost-only.
- Service installation/enabling remains an explicit local operator action.
- The user service adds no repository or Git mutation authority.
- Remote service start/stop commands are not authorized.
- Claimed-request replay/resume is not authorized.
- A typed result is evidence only and grants no later mutation authority.

## Next Approved Direction

After AUTO-0014 closes, begin design-first work for a read-only exact post-merge Quality verifier. It should verify the `Quality` workflow for the exact merged `master` SHA and fail closed unless the expected push run is completed successfully. It must not gain rerun/cancel, merge, or repository mutation authority.

## General Engineering Guardrails

- Preserve originals.
- Extend, never replace.
- Documentation before implementation.
- Keep changes small, testable, deterministic, and reviewable.
- Make compatibility and security claims only from recorded evidence.
- Treat published tags/releases as immutable historical evidence.
