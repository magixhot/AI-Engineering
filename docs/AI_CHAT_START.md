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

AI-Engineering has completed and verified AUTO-0001 through AUTO-0012 for their approved scopes. AUTO-0013 stages 01–05 are COMPLETE / VERIFIED; AUTO-0013-06 final evidence/documentation reconciliation is active.

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

AUTO-0007 is permanently read-only. AUTO-0008 remains the sole guarded one-step apply boundary. AUTO-0009 is bounded orchestration over repeated fresh planning plus exactly one AUTO-0008 apply per iteration. AUTO-0010 policy can only restrict those existing authorities. AUTO-0011 approval is an optional additional single-candidate gate and cannot grant new mutation authority. AUTO-0012 receipts are deterministic execution evidence only. AUTO-0013 adds bounded read-only remote inspection/control transport and evidence only.

## Active Milestone

```text
AUTO-0013-01 design/contract                    COMPLETE / VERIFIED
AUTO-0013-02 typed request/result protocol      COMPLETE / VERIFIED
AUTO-0013-03 read-only OpenCode adapter         COMPLETE / VERIFIED
AUTO-0013-04 GitHub control worker              COMPLETE / VERIFIED
AUTO-0013-04 corrective failure hardening       COMPLETE / VERIFIED
AUTO-0013-05 workspace routing correction       COMPLETE / VERIFIED prerequisite
AUTO-0013-05 end-to-end verification            COMPLETE / VERIFIED
AUTO-0013-06 final reconciliation               ACTIVE — DOCUMENTATION CLOSURE
```

Read `AUTO-0013_OPENCODE_CONTROL_BRIDGE_DESIGN.md`, `AUTO-0013_05_END_TO_END_VERIFICATION.md`, and `AUTO-0013_FINAL_EVIDENCE.md` for the active bridge contract and evidence.

The verified successful live request id is:

```text
sha256:dcdfcd976fff8c7afd16352fdc63e2781c7067c6492c4e43733abd4bd6efeb2c
```

It produced a typed `SUCCEEDED` result on branch `master` at exact HEAD `2d03f9e37e373def6b0f705b6f2b5da751279427` with `pre_clean=true` and `post_clean=true`. Adapter success requires complete before/after repository snapshot equality.

AUTO-0013-05 evidence PR #134 passed Quality #280 and exact post-merge Quality SUCCESS on master `abcecfdbdf5767db67cda78aaf6359e0f599f005`.

AUTO-0013 is not fully COMPLETE / VERIFIED until AUTO-0013-06 itself passes pre-merge Quality, merges, and the exact resulting master passes post-merge Quality.

## AUTO-0013 Guardrails

- Allowed remote task classes are only `status`, `inspect`, `plan`, and `diff`.
- Request text is analysis input, never shell code.
- OpenCode edit authority and external-directory access are denied.
- Shell is deny-by-default with a narrow read-only Git allowlist.
- OpenCode remains localhost-only.
- A typed result is evidence only and grants no later mutation authority.
- AUTO-0013 cannot invoke or replace reconciliation apply/run authority.
- No commit/push/reset/checkout/clean/stash mutation, package publication, deployment, public OpenCode ingress, arbitrary remote shell execution, or second write path is authorized.
- Automatic local worker startup, altered event delivery, a private control plane, or any write/apply capability requires a separate future design/contract.

## General Engineering Guardrails

- Preserve originals.
- Extend, never replace.
- Documentation before implementation.
- Keep changes small, testable, deterministic, and reviewable.
- Make compatibility and security claims only from recorded evidence.
- Treat published tags/releases as immutable historical evidence.
