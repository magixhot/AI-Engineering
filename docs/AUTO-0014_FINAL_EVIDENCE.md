# AUTO-0014 — Final Evidence / Documentation Reconciliation

**Status:** FINAL RECONCILIATION / PENDING STAGE GATE

This document records the authoritative closure evidence for AUTO-0014 after staged implementation and successful installed local-service verification.

AUTO-0014 removes the manual local-worker startup burden while preserving the existing AUTO-0013 read-only authority boundary. It adds no new remote task classes, repository mutation authority, public OpenCode ingress, remote service-control authority, or request replay semantics.

## Verified service path

```text
External AI operator
  -> GitHub control issue
  -> installed user-scoped worker service
  -> localhost OpenCode server
  -> dedicated read-only AUTO-0013 agent
  -> AI-Engineering workspace
  -> typed GitHub result
```

The worker remains restricted to `status`, `inspect`, `plan`, and `diff`.

## Delivery record

| Stage | Evidence | State |
|---|---|---|
| AUTO-0014-01 | PR #137; design/contract; pre-merge and exact post-merge Quality SUCCESS | COMPLETE / VERIFIED |
| AUTO-0014-02 | PR #138; typed runtime/service configuration; pre-merge and exact post-merge Quality SUCCESS | COMPLETE / VERIFIED |
| AUTO-0014-03 | PR #139; single-instance lifecycle; pre-merge and exact post-merge Quality SUCCESS | COMPLETE / VERIFIED |
| AUTO-0014-04 | PR #140; user-service integration; pre-merge and exact post-merge Quality SUCCESS | COMPLETE / VERIFIED |
| AUTO-0014-05 corrective runtime-directory integration | PR #141; preserves hardened service sandbox and adds validated `RuntimeDirectory=` handling | COMPLETE / VERIFIED prerequisite |
| AUTO-0014-05 safe OpenCode stage diagnostics | PR #142; bounded safe error-stage qualification; exact merged master `5b5b3b0ec1922685a594679ddebc199f28b6b8d5`; exact post-merge Quality SUCCESS | COMPLETE / VERIFIED prerequisite |
| AUTO-0014-05 installed local-service evidence | PR #143; Quality #302 SUCCESS; merged master `58e0b3c6cd5393386ad97871aa34f6fd9e4fef47`; exact post-merge Quality SUCCESS | COMPLETE / VERIFIED |
| AUTO-0014-06 | final evidence/documentation reconciliation | PENDING FINAL STAGE GATE |

## Installed lifecycle evidence

Local service verification recorded:

```text
restart=PASS
single-instance=PASS
repository-invariants=PASS
```

The installed per-user service was observed active, restart created a fresh worker process, a second lifecycle instance for the same repository/control issue failed closed instead of racing, and repository state remained unchanged.

The service integration preserves `ProtectSystem=strict`, `ProtectHome=read-only`, `NoNewPrivileges=yes`, a user-scoped runtime directory, and explicit operator-controlled installation/enabling.

## Successful installed end-to-end evidence

The final installed-service request was:

```text
request_id=sha256:593eff3b7e76a65ec2399ea3988ae0895ea01c2bc608bb690bc62be46fe9baf7
expected_head=5b5b3b0ec1922685a594679ddebc199f28b6b8d5
task_class=status
```

The already-running service discovered and claimed the request autonomously. Its terminal typed result recorded:

```text
state=SUCCEEDED
repository=magixhot/AI-Engineering
branch=master
head=5b5b3b0ec1922685a594679ddebc199f28b6b8d5
pre_clean=true
post_clean=true
```

This proves the installed GitHub -> user service -> localhost OpenCode -> read-only agent -> typed GitHub result path without manual worker startup and without repository mutation.

## Authority boundaries

AUTO-0007 remains permanently read-only. AUTO-0008 remains the sole guarded one-step apply authority. AUTO-0009 remains bounded replan-between-writes orchestration. AUTO-0010 remains restriction-only policy. AUTO-0011 remains an optional explicit approval gate. AUTO-0012 remains deterministic execution evidence only. AUTO-0013 remains bounded read-only remote inspection/control transport. AUTO-0014 adds only local lifecycle supervision for that existing worker.

AUTO-0014 does not authorize write/apply execution, Git mutation, arbitrary shell execution, publication, deployment, public OpenCode ingress, inbound workstation webhooks, remote service start/stop commands, request replay/resume, or a second repository write path.

## Next approved design direction

After AUTO-0014 closes, the next approved milestone is a design-first read-only exact post-merge Quality verifier. Its purpose is to remove the remaining manual GitHub Actions confirmation by deterministically verifying the `Quality` workflow for the exact merged `master` SHA, including push event, completed status, and successful conclusion. It must fail closed and must not gain workflow rerun/cancel, merge, or repository mutation authority.

## Closure rule

AUTO-0014-06 and AUTO-0014 become COMPLETE / VERIFIED only after this final documentation change passes pre-merge Quality, is merged, and the exact resulting `master` commit passes post-merge Quality.
