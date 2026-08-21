# AUTO-0022 — GitHub Control Surface Coherence

## Purpose

Reconcile the authoritative public description of GitHub issue #130 with the
already verified read-only control protocol and aged-claim recovery contract.

AUTO-0022 does not add a task class or authority. It corrects one external
documentation surface so operators see the authority that already exists.

## Verified Input Baseline

AUTO-0021 terminal closure merged through PR #202 as exact `master`
`3e3c2b32d0caf677d55be9f090d4a1d236716e42`. Pre-merge Quality #417 and
push-triggered Quality #418 (run id `32512364877`) completed successfully.

At audit time, issue #130 is open, has title
`AUTO-0013 OpenCode control channel`, and reports
`updated_at=2026-08-21T12:31:00Z`. Its exact body bytes have SHA-256
`ee0db3171f5d0c39976102c14b4780ca0ea3677fe3ec82f7df9becdc66edf4ff`.

## Drift Finding

The issue body lists only `status`, `inspect`, `plan`, and `diff`.

The verified protocol enum also includes deterministic read-only
`quality_verify`, which requires an exact expected head and runs through the
Quality relay without OpenCode. The issue body also predates AUTO-0019
aged-claim terminal recovery and therefore omits its no-replay invariant.

This is external documentation drift, not missing implementation.

## Exact Target

AUTO-0022 governs exactly:

```text
repository: magixhot/AI-Engineering
issue:      130
field:      body
```

It does not create a general issue synchronizer or govern titles, state,
labels, milestones, assignees, comments, reactions, or other issues.

## Desired Body Contract

The reconciled body must state:

- transport-only, no-mutation authority;
- allowed classes `status`, `inspect`, `plan`, `diff`, and `quality_verify`;
- `quality_verify` requires exact `expected_head` and does not invoke OpenCode;
- other task classes use only the existing bounded read-only adapter;
- aged unresolved claims may receive separate terminal recovery evidence only
  after immediate reinspection;
- recovery never calls the task executor, OpenCode, or `quality_verify`, and
  never replays the claimed request;
- malformed, unknown, write-capable, or privacy-unsafe input fails closed;
- write/apply, repository/filesystem mutation, workflow control, service or
  credential mutation, deployment, release, and publication remain excluded.

No implementation, Quality, recovery, or release claim may exceed repository
code and already merged exact evidence.

## Guarded External Mutation

Before any body update, the operator must re-fetch issue #130 and verify:

- repository and issue number are exact;
- issue remains open;
- title remains unchanged;
- current body hash matches the stage-approved expected hash.

Drift fails closed without a write. If the precondition matches, exactly one
body-only update may be attempted. The result must then be re-read and compared
with the exact approved body. No automatic write retry is allowed after an
ambiguous response; reinspection decides the observed state.

## Verification

Evidence must record only public-safe data:

- pre-write body hash and approved desired-body hash;
- exact issue identity and unchanged non-body fields;
- post-write body hash and exact desired-body equality;
- preserved task/authority/no-replay boundaries;
- repository state and exact Quality gates.

No token, credential, local path, hostname, environment value, or unrelated
issue/comment content may enter evidence.

## Explicit Exclusions

AUTO-0022 does not authorize protocol/runtime changes, new task classes,
generic GitHub issue automation, comment rewriting, worker/OpenCode expansion,
request replay, automatic repair, workflow rerun/cancel/dispatch, service or
credential mutation, deployment, release, publication, or PyPI work.

## Delivery Stages

1. `AUTO-0022-01` — design, exact target, and fresh drift audit.
2. `AUTO-0022-02` — exact desired-body artifact and guarded mutation plan.
3. `AUTO-0022-03` — authorized body-only update and post-write evidence.
4. `AUTO-0022-04` — final cross-surface audit and terminal closure decision.

Every repository stage requires exact PR-head Quality, expected-head-protected
merge, and exact push-triggered post-merge Quality.

## Completion Rule

AUTO-0022 is complete only when issue #130 exactly reflects the verified task
classes and no-replay recovery boundary, no other issue field changed, public
evidence is bounded, all repository gates pass, and final audit finds no
unapproved authority expansion.
