# AUTO-0018 — Read-Only Control Plane Reliability / Observability Hardening Design

Status: IMPLEMENTED / FINAL GATE PENDING

## Purpose

Harden the existing read-only control plane so operators can distinguish protocol rejection, transport failure, stale-workspace rejection, executor failure, healthy idle polling, and exact Quality verification outcomes without expanding authority.

AUTO-0018 is reliability/observability hardening only. It preserves the existing read-only task classes and does not add remote write/apply authority, hidden repository repair, workflow mutation, service-control mutation, credential mutation, deployment, publication, release, or expanded OpenCode authority.

## Starting evidence

AUTO-0017 completed on exact `master` commit:

```text
8a4375257882fd846bbb605c8791c04a6d602478
```

The final AUTO-0017 hardening audit identified four concrete operability gaps in the existing read-only control path:

1. malformed/non-canonical requests fail closed but can be silently skipped;
2. expected-head mismatch is correctly fail-closed but difficult to diagnose from the external control plane;
3. normal polling is intentionally quiet, making healthy-idle and repeatedly rejected-request states hard to distinguish;
4. transient transport/executor failures need clearer typed/operator-visible classification while preserving current authority boundaries.

## Authority boundary

AUTO-0018 MUST NOT add or imply any of the following:

- new remote write/apply task classes;
- automatic `git pull`, reset, checkout, merge, clean, restore, or repository repair;
- automatic workstation repair or package installation;
- workflow rerun/cancel/dispatch;
- service start/stop/restart/enable/disable authority;
- credential/token/authentication mutation;
- deployment, release, publication, or PyPI mutation;
- broader OpenCode permissions or new executor authority.

Existing read-only task classes remain bounded by their current contracts. `quality_verify` remains deterministic, read-only, and independent of OpenCode execution.

## Reliability / observability requirements

### 1. Typed protocol rejection evidence

Malformed, non-canonical, or unsupported control requests must remain fail-closed. The design may add bounded operator-visible rejection evidence only when doing so can be done without echoing secrets, credentials, private environment values, local absolute paths, usernames, hostnames, or arbitrary untrusted request payloads.

The diagnostic contract should expose only a stable reason code and safe bounded metadata needed to identify the rejected control-channel item.

### 2. Failure taxonomy

The worker/control-plane evidence must distinguish at least:

- transport read failure;
- protocol parse / canonical request-id failure;
- unsupported request/task class;
- expected-head mismatch;
- repository cleanliness/snapshot failure;
- OpenCode/executor failure for task classes that require it;
- exact Quality verification failure;
- successful read-only result.

Failure categories must be deterministic and bounded. Free-form exception text must not become a secret or workstation-detail disclosure path.

### 3. Polling liveness observability

Healthy idle operation should be distinguishable from a worker that is repeatedly failing before it can claim work. Any liveness mechanism must remain read-only, bounded, low-noise, and must not create an unbounded stream of comments or logs.

The implementation design should prefer local structured diagnostics and/or bounded control-plane evidence tied to meaningful state transitions rather than per-poll chatter.

### 4. Stale-workspace detection without hidden mutation

Expected-head mismatch remains fail-closed. AUTO-0018 may improve diagnosis and recovery guidance but must not automatically mutate the repository to match `origin/master`.

Safe behavior:

- detect and classify stale workspace state;
- report the expected and observed commit SHA when public-safe;
- preserve cleanliness evidence;
- provide deterministic operator guidance.

Out of scope:

- automatic fetch/pull/reset/checkout/merge;
- changing branches;
- modifying index/worktree state.

### 5. Transport resilience

Transient GitHub/control-channel read errors should not turn a recoverable polling problem into an opaque worker outage. The runtime design may add bounded retry/backoff and structured failure reporting, provided it does not change repository state or expand authority.

Any retry policy must be deterministic, bounded, testable, and avoid duplicate result publication.

### 6. Public/private safety

No public GitHub evidence may include workstation-local usernames, absolute private paths, credentials, tokens, private environment values, hostnames, or unrelated machine metadata.

Diagnostics must be designed from safe fields outward rather than by publishing raw exception strings or request bodies.

## Delivery stages

1. AUTO-0018-01 — Design / Contract only — COMPLETE / VERIFIED.
2. AUTO-0018-02 — Typed protocol-rejection and failure-taxonomy primitives — COMPLETE / VERIFIED.
3. AUTO-0018-03 — Polling/transport resilience and observability hardening — COMPLETE / VERIFIED.
4. AUTO-0018-04 — Stale-workspace diagnostics and operator guidance — COMPLETE / VERIFIED.
5. AUTO-0018-05 — Installed/E2E failure-mode evidence and cross-boundary audit — COMPLETE / VERIFIED.
6. AUTO-0018-06 — Final reconciliation and hardening evidence — PENDING FINAL GATE.

AUTO-0018-01 was documentation-only. Runtime stages -02 through -05 were implemented only after explicit approval and stayed inside the authority boundary above. AUTO-0018-06 is documentation/evidence reconciliation only.

## Verification requirements

Each approved implementation stage preserves repository cleanliness and existing authority boundaries and includes focused verification for the relevant failure modes.

The normal repository gate remains mandatory:

1. exact PR-head Quality success;
2. merge with expected-head protection;
3. exact post-merge `master` push Quality verification through the read-only relay.

No workflow rerun/cancel/dispatch authority is introduced.

## Implementation reconciliation

The implementation now provides typed control failure/rejection taxonomy, bounded public-safe protocol rejection metadata, bounded deterministic retry/backoff for control-channel reads, low-noise transport state diagnostics, and non-mutating expected-head mismatch evidence with deterministic operator guidance.

The installed worker E2E demonstrated both fail-closed stale-workspace handling and successful exact-head Quality verification. The last verified merged baseline before AUTO-0018-06 is exact `master`:

```text
b59f651b4719f8463b3cde1132980a1cf340ad10
```

Its exact post-merge Quality relay succeeded on run `32379177746`, workflow id `334955954`, `.github/workflows/quality.yml`, `master` / `push`, exact head, terminal `completed`, conclusion `success`, `satisfies_gate=true`, and clean pre/post evidence.

The installed stale-workspace behavior intentionally requires explicit operator synchronization after a remote merge; no hidden repository auto-repair has been added.

## Completion rule

AUTO-0018 is complete only when the approved reliability/observability hardening is implemented and verified without authority expansion, all newly introduced public diagnostics satisfy the privacy boundary, stale-workspace handling remains non-mutating, and final exact post-merge Quality evidence succeeds.

The implementation and installed/E2E evidence requirements are satisfied. The milestone remains open only for AUTO-0018-06 exact PR-head Quality, expected-head-protected merge, and exact post-merge `master` push Quality verification.
