# AI-Engineering Roadmap

## Completed / Verified

The documentation foundation, MCP foundation, SDK-0001, TOOL-0001, REL-0001/REL-0002/REL-0003, CI-0001, SAFE-0001/SAFE-0002, and AUTO-0001 through AUTO-0012 are COMPLETE / VERIFIED for their approved scopes.

AUTO-0013 stages 01–05 are COMPLETE / VERIFIED. AUTO-0013-06 is the active final evidence/documentation reconciliation stage.

AUTO-0007 remains the permanent read-only reconciliation planner. AUTO-0008 remains the guarded one-step apply boundary. AUTO-0009 is bounded multi-step orchestration. AUTO-0010 adds only a restrictive policy gate. AUTO-0011 adds only an optional explicit single-candidate approval gate. AUTO-0012 adds deterministic execution receipts/evidence only. AUTO-0013 adds bounded read-only remote inspection/control transport and evidence only.

## AUTO-0013 — OpenCode Control Bridge

**Status:** STAGE 06 DOCUMENTATION CLOSURE IN PROGRESS

Verified read-only control path:

```text
External AI operator
  -> GitHub control issue
  -> local control worker
  -> localhost OpenCode server
  -> dedicated read-only AUTO-0013 agent
  -> AI-Engineering workspace
  -> typed GitHub result
```

Allowed task classes are `status`, `inspect`, `plan`, and `diff`. The dedicated OpenCode agent denies edits, external-directory access, and arbitrary shell execution; shell access is deny-by-default with a narrow read-only Git allowlist.

### Delivery Evidence

- AUTO-0013-01 — PR #127; Quality #265; exact post-merge Quality SUCCESS.
- AUTO-0013-02 — PR #128; Quality #268; exact post-merge Quality SUCCESS.
- AUTO-0013-03 — PR #129; Quality #270; exact post-merge Quality SUCCESS.
- AUTO-0013-04 — PR #131; Quality #273; exact post-merge Quality SUCCESS.
- AUTO-0013-04 corrective hardening — PR #132; Quality #275; exact post-merge Quality SUCCESS.
- AUTO-0013-05 workspace routing correction — PR #133; Quality #278; exact post-merge Quality SUCCESS.
- AUTO-0013-05 E2E evidence — PR #134; Quality #280; exact post-merge Quality SUCCESS on `abcecfdbdf5767db67cda78aaf6359e0f599f005`.
- AUTO-0013-06 — final evidence/documentation reconciliation only; final gates pending.

The verified successful live request id is:

```text
sha256:dcdfcd976fff8c7afd16352fdc63e2781c7067c6492c4e43733abd4bd6efeb2c
```

Its terminal result recorded `SUCCEEDED`, `master`, exact HEAD `2d03f9e37e373def6b0f705b6f2b5da751279427`, `pre_clean=true`, and `post_clean=true`. Adapter success requires complete before/after repository snapshot equality.

## Delivery Gates

AUTO-0013 stages execute in order:

`01 → 02 → 03 → 04 → 05 → 06`

Stages 01–05 have completed their required pre-merge and exact post-merge Quality gates. Stage 06 reconciles authoritative documentation against the verified implementation and live E2E evidence. AUTO-0013 is fully COMPLETE / VERIFIED only after stage 06 itself passes pre-merge Quality, merges, and exact post-merge Quality succeeds.

## Current Priority

Complete AUTO-0013-06 without expanding authority. Preserve AUTO-0007 read-only planning, AUTO-0008 sole guarded one-step apply authority, AUTO-0009 bounded replan-between-writes orchestration, AUTO-0010 restriction-only policy, AUTO-0011 approval as an additional fail-closed single-candidate gate, AUTO-0012 receipts as evidence only, and AUTO-0013 as read-only remote inspection/control transport only.

Any future automatic local service startup, changed polling/event delivery, private control plane, or write/apply capability requires a separate design/contract.
