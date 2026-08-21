# AUTO-0019-06 — Final Reconciliation / Hardening Evidence

Status: FINAL RECONCILIATION / PENDING GATE

## Purpose

Reconcile AUTO-0019 against the approved no-replay recovery design, the
implemented runtime behavior, focused race/failure-mode coverage, installed E2E
evidence, and the permanent authority/privacy boundaries before declaring the
milestone complete.

This stage is documentation/evidence only. It does not add runtime behavior,
task classes, repository mutation, workflow mutation, service-control
authority, credentials, deployment, publication, release, or broader OpenCode
authority.

## Delivery reconciliation

AUTO-0019 was delivered through the approved six-stage sequence:

1. `AUTO-0019-01` — design/contract in PR #181, merged as exact `master`
   `e98374082ed0bd5978f5aa15b048e910a547d2cf` after Quality #374 and #375
   succeeded.
2. `AUTO-0019-02` — typed unresolved-claim lifecycle primitives and bounded
   recovery evidence in PR #182, merged as exact `master`
   `fb4524adf29e91bc0249a55d451ddd616014ccf3` after Quality #376 and #377
   succeeded.
3. `AUTO-0019-03` — deterministic aged-claim discovery, immediate
   reinspection, and no-replay terminalization in PR #183, merged as exact
   `master` `b2a9054d1f8fe2b8fc00aa11f669695806800531`. Quality #379 succeeded on
   the final PR head and push-triggered Quality #380 succeeded on the exact
   merge. Documentation-only PRs #184 and #185 corrected the recorded gate
   interpretation and each passed their own exact pre/post Quality gates
   (#381 through #384), ending at exact `master`
   `abadfadf52443dbaf2c0d5a716cf6e6455b3fb08`.
4. `AUTO-0019-04` — ambiguous-publication/concurrency hardening and focused
   failure-mode tests in PR #186, merged as exact `master`
   `d90cffc446e6c6a27ca57a813638ad821744f0c6` after Quality #385 and #386
   succeeded.
5. `AUTO-0019-05` — installed/E2E stranded-claim evidence and cross-boundary
   audit. PR #187 staged the evidence contract and passed Quality #387/#388.
   Installed GitHub CLI compatibility was corrected narrowly in PR #188 and
   passed Quality #389/#390. Final verified evidence merged through PR #189 as
   exact `master` `e42fe2cdc387195deb82ac414f54c39a526cc651` after Quality #391
   and #392 succeeded.
6. `AUTO-0019-06` — this final reconciliation/evidence stage.

The failed Quality #378 targeted the superseded PR #183 head
`7e1ac57e87d9cf96b5b042b1da5cf8498782e69f`. A line-length-only correction
advanced the PR to exact head `464eeeea710ad910599319e1958e219943b51569`,
which passed Quality #379 before merge. No failed or superseded run is treated
as completion evidence.

## Implemented recovery behavior

A visible valid claim remains an execution fence and consumes its canonical
request id for normal processing. Fresh claims are left untouched. When a
trusted valid claim is older than the bounded recovery grace and has no public
terminal result, the worker may publish a separate terminal recovery envelope;
it must not execute or re-execute the claimed request.

Recovery discovery is deterministic and uses the durable public control
channel. It requires a valid trusted origin request and the latest trusted
claim, then immediately re-reads the control issue before publication. A
terminal result, changed origin, missing/malformed origin, or newer-claim race
suppresses recovery.

The recovery envelope is strict and bounded. It reports the original request
id, task class and repository, terminal `FAILED`,
`kind=claim_recovery_required`,
`reason=claimed_without_terminal_result`, `replay_attempted=false`, and the
current protocol version. It contains no executor output or free-form local
exception text.

## Publication and transport hardening

Recovery publication remains single-attempt. An ambiguous publication outcome
is not retried in the same process, and a process-local fence suppresses later
poll-cycle attempts for that request. The worker never converts recovery
publication uncertainty into executor, OpenCode, or `quality_verify` activity.

After a process restart, durable public state remains authoritative. If the
ambiguous write actually created a recovery comment, normal terminal-result
inspection suppresses another publication. No durable shared lock or new
cross-process state was added.

The installed workstation exposed an older GitHub CLI that supports
`gh api --paginate` but not `--slurp`. Both read-only GitHub transports now use
explicit bounded `page=N` GET reads with a page size of 100 and a maximum of
100 pages. This preserves complete traversal, bounded retries, fail-closed read
semantics, and single-attempt writes without adding authority.

## Focused verification coverage

The AUTO-0019 tests cover:

- fresh versus aged claims;
- suppression when a normal terminal result or recovery already exists;
- malformed/missing origin requests;
- immediate-reinspection terminal and newer-claim races;
- exact recovery envelope fields and no executor entry;
- ambiguous-before-write and ambiguous-after-write publication failures;
- successful recovery publication and process-local fencing;
- bounded multi-page control-comment and Actions reads;
- transport read retry/recovery/fail-closed behavior;
- distinct exact-Quality relay behavior without OpenCode.

The normal repository Quality workflow continued to run Ruff, mypy, the full
pytest suite, and the exact pre-merge base-gate verifier for every staged
change. Completion evidence relies only on exact successful heads and exact
push-triggered merged-master runs.

## Installed / E2E evidence

The deterministic stranded fixture used original request id:

```text
sha256:d61960632421eaafcdc7300cd69965b0028f6bb9f148ea0b9dcb93ecf83831ff
```

Its request and claim were public comments `5369266460` and `5369268039`.
After the corrected installed worker was explicitly loaded and started, it
published exactly one recovery comment, `5369813615`, with terminal `FAILED`,
`claim_recovery_required`, `claimed_without_terminal_result`, and
`replay_attempted=false`. No second claim or ordinary result appeared for the
stranded request, and the task executor, OpenCode, and `quality_verify` were
not invoked for it.

The distinct liveness request id was:

```text
sha256:20409e5ce207053b7137d36ce798c9e94e31f591ae360f40d93bc80bdf3b6ec3
```

Request comment `5369824268` was claimed once by comment `5369825467` and
completed `SUCCEEDED` in result comment `5369827138`. The result verified exact
installed `master` `b1136c3f57616aa5197f078300a1fa54879aad1c` through Quality
run `32479152403`, workflow id `334955954`, branch/event `master` / `push`,
`completed/success`, `satisfies_gate=true`, and `pre_clean=true` /
`post_clean=true`.

This separate request proves that recovery terminalized the old claim without
damaging later normal polling or the read-only exact-Quality path.

## Authority audit

AUTO-0019 did not add any remote write/apply task class. The existing task
classes remain `status`, `inspect`, `plan`, `diff`, and read-only
`quality_verify`. Recovery is terminal evidence for an already claimed request,
not a new task class and not permission to execute it.

No automatic repository synchronization or repair was added. No Actions
rerun/cancel/dispatch authority was added. No service
start/stop/restart/enable/disable authority was added to the control protocol.
No credential/token mutation, deployment, release, publication, or PyPI
mutation was added. OpenCode permissions were not broadened.

If the objective of a recovered request is still desired, the operator must
submit a new canonical request with a distinct objective/request id. Recovery
never grants replay or resume authority.

## Public/private safety audit

Public recovery evidence is constructed only from strict protocol fields and
portable repository/request identities. Installed evidence contains no
workstation-local absolute paths, usernames, hostnames, credential values,
private environment values, raw exception bodies, or unrelated machine
metadata.

Local transport diagnostics remain bounded stable categories. The installed
compatibility correction does not expose command output or authentication
material in public results.

## Residual operational boundary

A claim may be terminalized only after the bounded grace interval and immediate
public reinspection. Publication ambiguity remains fail-closed and
single-attempt within the running process. The public GitHub control channel,
not workstation-local hidden state, remains the durable source of truth.

The process-local fence cannot eliminate a true simultaneous race between
separate worker processes and cannot persist an ambiguous-before-write decision
across process restart. Closing those residual edges would require a separately
approved server-side idempotency primitive, durable shared state, or
distributed lock. None is introduced here; every attempt still re-inspects the
public channel and never enters the claimed request executor.

These constraints intentionally prefer a terminal failure and a new
operator-authored request over automatic replay. They are the safety contract,
not unresolved authority for hidden recovery execution.

## Completion gate

AUTO-0019 may be declared COMPLETE / VERIFIED when this final reconciliation
change passes exact PR-head Quality, merges with expected-head protection, and
the exact merged `master` push passes the existing post-merge Quality gate.

Until that final gate succeeds, AUTO-0019-06 remains pending and the milestone
is not yet closed.
