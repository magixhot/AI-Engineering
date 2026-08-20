# AUTO-0018 — Read-Only Control Plane Reliability / Observability Hardening Design

Status: DESIGN / PENDING GATE

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

## Proposed delivery stages

1. AUTO-0018-01 — Design / Contract only.
2. AUTO-0018-02 — Typed protocol-rejection and failure-taxonomy primitives.
3. AUTO-0018-03 — Polling/transport resilience and observability hardening.
4. AUTO-0018-04 — Stale-workspace diagnostics and operator guidance.
5. AUTO-0018-05 — Installed/E2E failure-mode evidence and cross-boundary audit.
6. AUTO-0018-06 — Final reconciliation and hardening evidence.

AUTO-0018-01 is documentation-only. Stages -02 through -06 may change runtime behavior and therefore require explicit approval after the design gate before implementation begins.

## Verification requirements

Each approved implementation stage must preserve repository cleanliness and existing authority boundaries and must include focused tests for the relevant failure modes.

The normal repository gate remains mandatory:

1. exact PR-head Quality success;
2. merge with expected-head protection;
3. exact post-merge `master` push Quality verification through the read-only relay.

No workflow rerun/cancel/dispatch authority is introduced.

## Completion rule

AUTO-0018 is complete only when the approved reliability/observability hardening is implemented and verified without authority expansion, all newly introduced public diagnostics satisfy the privacy boundary, stale-workspace handling remains non-mutating, and final exact post-merge Quality evidence succeeds.
