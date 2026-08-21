# AUTO-0019-05 — Installed / E2E Stranded-Claim Evidence

Status: VERIFIED EVIDENCE / PENDING STAGE GATE

## Purpose

Verify AUTO-0019 claim recovery through the installed workstation worker and
audit the public-control, local-service, repository, executor, and privacy
boundaries without expanding authority.

The installed probe must demonstrate that a visible valid claim with no
terminal result becomes a bounded terminal recovery result after the configured
grace interval. It must also demonstrate that recovery does not execute or
re-execute the claimed request.

## Exact starting state

AUTO-0019-04 completed on exact `master`:

```text
d90cffc446e6c6a27ca57a813638ad821744f0c6
```

Pre-merge Quality #385 succeeded on exact PR head
`d8a0fe45d973e006ef57b5f47a27de55ab659a4c`. Push-triggered post-merge
Quality #386 (run id `32463603399`) succeeded on the exact `master` SHA above.

This repository evidence does not prove that a long-running workstation service
has synchronized and reloaded the AUTO-0019-04 runtime. Installed E2E evidence
therefore remains required.

## Installed compatibility observation

The first installed probe published canonical request
`sha256:d61960632421eaafcdc7300cd69965b0028f6bb9f148ea0b9dcb93ecf83831ff`
as public comment `5369266460` and its exact claim as comment `5369268039`.
The claim was created at `2026-08-21T11:29:47Z` and no ordinary terminal result
was published.

The installed worker failed closed before recovery discovery because its GitHub
CLI supports `gh api --paginate` but not the newer `--slurp` flag used by both
control-comment and exact-Quality transports. Direct authenticated GitHub API
reading succeeded without that flag. Local diagnostics remained bounded as
`transport_read_failure`; no request executor, OpenCode call, `quality_verify`,
repository mutation, or recovery publication occurred.

The corrective prerequisite replaces `--slurp` with explicit bounded
`page=N` reads in both transports. It preserves read-only GET behavior,
full-page traversal, deterministic bounds, existing retry/fail-closed behavior,
and single-attempt publication semantics. The original public fixture remains
valid and claimed while this correction passes its normal Quality gates and is
loaded by the installed service.

The correction merged through PR #188 as exact `master`
`b1136c3f57616aa5197f078300a1fa54879aad1c`. Pre-merge Quality #389
(run id `32478745136`) succeeded on exact PR head
`31ac082bd9941e9c85b2ba34243ffc7d71170cf6`. Push-triggered post-merge
Quality #390 (run id `32479152403`) then succeeded on the exact merged
`master` SHA.

## Verified installed recovery

Before resuming polling, the operator reported the installed checkout at exact
`b1136c3f57616aa5197f078300a1fa54879aad1c`, a clean worktree, the canonical
service inactive, and the installed worker loading the corrected transport
without the unsupported `--slurp` option. The service was then started
explicitly and reported active. The installed lifecycle constructs the worker
with the deterministic default recovery grace of 300 seconds, within the
validated 60-to-86,400-second bounds.

On its normal poll, the installed worker published recovery comment
`5369813615` at `2026-08-21T12:29:30Z` for the original request id:

`sha256:d61960632421eaafcdc7300cd69965b0028f6bb9f148ea0b9dcb93ecf83831ff`

The bounded recovery envelope reported:

- `state = FAILED`;
- `kind = claim_recovery_required`;
- `reason = claimed_without_terminal_result`;
- `replay_attempted = false`;
- task class `status`;
- repository `magixhot/AI-Engineering`;
- protocol version `1`.

Inspection of the control issue found exactly one recovery envelope for this
request id and no ordinary terminal result. The worker did not publish a
second claim. Because recovery terminalized the public request without entering
the task executor, it did not invoke OpenCode or `quality_verify` and did not
replay the stranded request.

## Verified distinct liveness probe

After recovery, the trusted operator published a new `quality_verify` request
with the distinct objective `AUTO-0019-05 installed liveness probe after
stranded-claim recovery.` for exact installed `master`
`b1136c3f57616aa5197f078300a1fa54879aad1c`.

The public evidence is:

- request id
  `sha256:20409e5ce207053b7137d36ce798c9e94e31f591ae360f40d93bc80bdf3b6ec3`;
- request comment `5369824268`, created at `2026-08-21T12:30:41Z`;
- claim comment `5369825467`, created at `2026-08-21T12:30:49Z`;
- terminal result comment `5369827138`, created at
  `2026-08-21T12:31:00Z`.

The terminal result reported `SUCCEEDED`, branch `master`, exact head
`b1136c3f57616aa5197f078300a1fa54879aad1c`, and `pre_clean=true` /
`post_clean=true`. Its nested Quality evidence reported workflow
`.github/workflows/quality.yml`, event/branch `push` / `master`, exact target
head, workflow id `334955954`, run id `32479152403`, run attempt `1`, terminal
status `completed`, conclusion `success`, and `satisfies_gate=true`.

The distinct request was claimed once and completed normally. This proves that
terminal recovery did not damage subsequent worker polling or the existing
exact-Quality path. The liveness task class does not invoke OpenCode.

## Observed boundary result

The recovery and liveness observations preserved the approved boundaries. The
worker performed no repository synchronization, repair, workflow mutation,
service control, deployment, release, package publication, credential change,
or expansion of remote task authority. Exact branch/HEAD and clean pre/post
state were preserved by the installed Quality result; neither recovery nor
Quality verification has repository or remotes mutation authority. Public
evidence contains only the portable repository, protocol, request, comment,
commit, and Quality identifiers required for audit.

## Installed-E2E precondition

The operator must explicitly fast-forward the validated local checkout to the
exact current `master` commit and explicitly restart the canonical
`ai-engineering-worker.service` before the probe.

The worker must not perform hidden repository synchronization or hidden service
control. No automatic fetch, pull, reset, checkout, merge, clean, restore,
restart, enable, disable, package installation, or repair is authorized.

Before the probe, record only bounded local evidence that:

- the installed checkout is on exact expected `master`;
- the checkout is clean;
- the canonical user service is active after the explicit restart;
- the configured recovery grace interval remains within the approved bounds.

Workstation-local absolute paths, usernames, hostnames, credentials, environment
values, and unrelated machine metadata must not be copied into public evidence.

## Deterministic stranded-claim fixture

The fixture uses only the existing trusted GitHub control-channel envelopes:

1. ensure the installed worker is not polling while the fixture is created;
2. publish one canonical read-only request from the trusted operator;
3. publish one valid `CLAIMED` envelope for that exact request id;
4. publish no normal result and do not invoke the request executor;
5. resume the explicitly managed installed worker;
6. wait until the public claim timestamp reaches the configured recovery grace;
7. allow the installed worker to poll normally.

Creating the request and claim while polling is paused prevents the installed
worker from executing the request between the two public comments. The fixture
models the exact durable public state left by a worker that stopped after claim
publication and before terminal result publication. Recovery behavior depends
only on this public state and does not require fabricated workstation-local
state.

The request id and public comment ids must be recorded after publication. The
fixture must use a distinct objective so its canonical request id cannot collide
with any earlier request.

## Required recovery evidence

The installed worker must produce exactly one recovery envelope with:

- the original canonical request id;
- the original task class and repository;
- terminal state `FAILED`;
- `kind=claim_recovery_required`;
- `reason=claimed_without_terminal_result`;
- `replay_attempted=false`;
- the current protocol version;
- no normal result envelope for the stranded request.

The worker must re-read the control channel immediately before publication. The
recovery publication remains single-attempt. The probe must not deliberately
manufacture an ambiguous GitHub write response: doing so would be
nondeterministic and could itself create duplicate public evidence. The
ambiguous-before-write and ambiguous-after-write no-retry boundaries remain
covered by the focused AUTO-0019-04 tests.

## No-replay and repository evidence

The installed observation must confirm:

- no OpenCode request is made for the stranded request;
- `quality_verify` is not invoked for the stranded request;
- no task executor is entered for the stranded request;
- no second claim or ordinary terminal result is published for that request;
- repository branch, HEAD, index, worktree, and remotes remain unchanged;
- the checkout remains clean before and after recovery.

The recovery envelope is the public no-replay contract. Any local diagnostic
used to corroborate the observation must remain bounded and must not be copied
verbatim if it contains workstation-private data.

## Distinct liveness probe

After recovery terminalizes the stranded request, publish a new canonical
`quality_verify` request with a distinct objective and request id for the exact
installed `master` SHA.

This is a new request, not replay of the stranded request. It must be claimed
once and may report `SUCCEEDED` only when the existing exact Quality tuple is
satisfied:

- workflow `.github/workflows/quality.yml`;
- branch/event `master` / `push`;
- exact target `head_sha`;
- terminal workflow status `completed`;
- conclusion `success`;
- `satisfies_gate=true`;
- clean pre/post repository evidence.

The liveness probe confirms that recovery does not damage normal request
handling and that the installed worker is running the current implementation.

## Cross-boundary audit

The installed probes must preserve every approved boundary:

- no new remote write/apply task class;
- no replay or re-execution of an already claimed request;
- no repository synchronization, mutation, or repair by recovery;
- no Actions rerun, cancel, or dispatch;
- no service-control authority in the control protocol;
- no credential or authentication mutation;
- no deployment, release, publication, or PyPI mutation;
- no broader OpenCode permissions;
- no workstation-private data in public control-plane evidence;
- no durable shared state or distributed lock added by this stage.

## Completion rule

AUTO-0019-05 may be marked complete only after the installed recovery and
distinct liveness results are captured with exact request ids and bounded
terminal evidence, repository invariants and cross-boundary audit pass, this
document is updated from `PENDING INSTALLED E2E` to verified status, and the
normal exact PR-head and post-merge `master` Quality gates succeed.
