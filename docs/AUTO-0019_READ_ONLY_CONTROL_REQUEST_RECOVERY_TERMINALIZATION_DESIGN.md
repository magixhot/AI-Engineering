# AUTO-0019 — Read-Only Control Request Recovery / Terminalization Design

Status: DESIGN / PENDING GATE

## Purpose

Harden the existing read-only GitHub control plane so a request that has already been claimed cannot remain indefinitely ambiguous when the worker, executor path, or result publication path fails before a terminal result is visible.

AUTO-0019 is recovery/terminalization hardening only. It does not add remote write/apply authority, repository repair, workflow mutation, service-control mutation, credential mutation, deployment/publication/release scope, or broader OpenCode authority.

## Starting evidence

AUTO-0018 completed on exact `master` commit:

```text
bfce3e267ddd16b355ca0ac668138f8ccfa20bae
```

The current worker protocol publishes a claim before execution and publishes the terminal result afterward. Claim and result publication are intentionally not retried, because retrying an ambiguous write could create duplicate public evidence.

This leaves one remaining lifecycle ambiguity: a process/transport failure after a visible `CLAIMED` record and before a visible terminal result can strand the request permanently. The current worker treats any claimed request id as already consumed, so a later worker instance will not execute it again and does not currently publish deterministic terminal evidence for the stranded claim.

## Safety objective

AUTO-0019 must remove the indefinite ambiguous-claim state without introducing automatic replay of an already claimed request.

The core invariant is:

> A visible claim is an execution fence. Recovery may terminalize an unresolved claim, but must not silently execute or re-execute that same claimed request.

This intentionally favors duplicate-execution prevention over automatic completion. If an operator still wants the original read-only objective after recovery terminalizes a stranded claim, the operator issues a new canonical request with a newly derived request id.

## Authority boundary

AUTO-0019 MUST NOT add or imply any of the following:

- new remote write/apply task classes;
- automatic replay or re-execution of already claimed requests;
- automatic `git fetch`, pull, reset, checkout, merge, clean, restore, or repository repair;
- workflow rerun/cancel/dispatch;
- service start/stop/restart/enable/disable authority;
- workstation repair or package installation;
- credential/token/authentication mutation;
- deployment, release, publication, or PyPI mutation;
- broader OpenCode permissions or new executor authority.

Existing task classes remain `status`, `inspect`, `plan`, `diff`, and deterministic read-only `quality_verify`.

## Recovery model

### 1. Claim identity

A claim remains tied to exactly one canonical request id. Recovery logic must first reconstruct and validate the originating request using the existing protocol parser. Malformed or non-canonical request payloads remain fail-closed and are not recoverable as executable work.

### 2. Unresolved claim definition

A request is unresolved only when all of the following are true:

- a valid canonical request is visible from a trusted author;
- a valid claim for the same request id is visible;
- no valid terminal result for that request id is visible;
- the claim satisfies the configured recovery-age rule.

A request with a visible terminal result is complete and must never be recovery-terminalized again.

### 3. Age / ownership fence

Recovery must not race a live worker that has just claimed a request. A deterministic bounded grace interval must separate ordinary in-flight work from recovery-eligible unresolved claims.

The grace interval is a safety fence, not a retry cadence. It must be explicit, configurable within a bounded range, testable, and based only on public control-channel timestamps/identities rather than workstation-local clocks or private state.

### 4. Recovery action

Recovery for an eligible unresolved claim is terminalization only. The worker publishes a bounded typed terminal result stating that the prior claim did not produce observable terminal evidence and that no replay was attempted.

The recovery result must use the original request id and task class, preserve public-safe repository identity, and use a stable reason code such as:

```text
claimed_without_terminal_result
```

The recovery result state should be terminal and fail-closed (`FAILED` or `REFUSED`, to be fixed by implementation contract). It must not claim success for the original objective.

### 5. No replay

Recovery MUST NOT call OpenCode, `quality_verify`, or any task executor for the unresolved claimed request.

This is required even though the current task classes are read-only, because the control plane cannot prove whether the previous worker executed the task before losing the terminal publication path. Re-executing would create an ambiguous duplicate-execution path.

### 6. Duplicate-publication protection

Before publishing recovery evidence, the worker must re-read the control channel and fail closed if a terminal result has appeared meanwhile.

Recovery result publication itself remains single-attempt unless a later approved protocol explicitly introduces idempotent server-side publication semantics. An ambiguous publication failure must not cause blind comment retries.

## Failure taxonomy extension

AUTO-0019 may add a stable lifecycle category/reason for unresolved claims, for example:

- `claim_recovery_required` — lifecycle classification;
- `claimed_without_terminal_result` — terminalization reason.

The exact enum names are implementation details, but the public contract must remain bounded and deterministic.

No raw exception text, request body, local path, username, hostname, environment value, credential, or arbitrary executor output may be copied into recovery evidence.

## Recovery result evidence

A recovery terminal result should expose only fields already allowed by the control protocol plus bounded machine-stable lifecycle evidence. At minimum it must identify:

- original request id;
- original task class;
- repository;
- terminal state;
- stable recovery reason;
- statement/code that no replay was attempted.

If repository snapshot evidence is included, it must be public-safe and must not become a prerequisite for terminalizing a claim whose original execution state is unknowable.

## Concurrency requirements

AUTO-0019 must fail closed under the following races:

1. two worker instances observe the same recovery-eligible claim;
2. a normal terminal result appears while recovery is being considered;
3. a recovery terminal result appears while another worker is considering recovery;
4. control-channel reads fail before the final publication decision;
5. publication returns an ambiguous transport failure.

The design does not require distributed locking. It requires deterministic reinspection immediately before publication and no executor replay. Duplicate recovery comments must be prevented where the existing GitHub evidence model permits; if an unavoidable ambiguous-write edge remains, it must be documented explicitly rather than hidden by retry.

## Operator workflow

Normal request handling remains unchanged:

1. canonical request is published;
2. worker claims it;
3. worker executes once;
4. worker publishes terminal result.

Recovery path:

1. worker discovers an aged claim with no terminal result;
2. worker validates the original request and claim identity;
3. worker re-reads the channel immediately before recovery publication;
4. if still unresolved, worker publishes terminal fail-closed recovery evidence without executing the objective;
5. operator may submit a new canonical request if the objective is still desired.

## Proposed delivery stages

1. AUTO-0019-01 — Design / Contract only.
2. AUTO-0019-02 — Typed unresolved-claim lifecycle primitives and bounded recovery evidence.
3. AUTO-0019-03 — Deterministic aged-claim discovery, reinspection, and no-replay terminalization.
4. AUTO-0019-04 — Concurrency / ambiguous-publication hardening and focused failure-mode tests.
5. AUTO-0019-05 — Installed/E2E stranded-claim evidence and cross-boundary audit.
6. AUTO-0019-06 — Final reconciliation / hardening evidence.

AUTO-0019-01 is documentation-only. Runtime stages -02 through -06 require the normal exact pre-merge and post-merge Quality gates and remain within the authority boundary defined here.

## Verification requirements

Focused verification must cover at least:

- fresh claim inside grace interval is not recovery-terminalized;
- aged valid claim without terminal result becomes recovery-eligible;
- visible terminal result suppresses recovery;
- malformed/non-canonical originating request is never executed by recovery;
- recovery never invokes OpenCode or `quality_verify`;
- reinspection detects a terminal result that appears during the recovery race;
- transport read failure fails closed;
- ambiguous result-publication failure does not trigger blind retry;
- recovery evidence is bounded and public-safe;
- repository cleanliness/authority boundaries remain unchanged.

The normal repository gate remains mandatory:

1. exact PR-head Quality success;
2. merge with `expected_head_sha` protection;
3. exact post-merge `master` push Quality verification through the read-only relay.

## Completion rule

AUTO-0019 is complete only when a stranded visible claim can be deterministically terminalized without replaying the original request, concurrency and publication races fail closed, installed/E2E evidence confirms the behavior, public/private boundaries remain intact, and final exact post-merge Quality evidence succeeds.
