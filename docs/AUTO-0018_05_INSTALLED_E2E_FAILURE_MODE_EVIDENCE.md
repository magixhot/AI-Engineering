# AUTO-0018-05 — Installed / E2E Failure-Mode Evidence

Status: EVIDENCE / PENDING INSTALLED E2E

## Purpose

Verify the AUTO-0018 runtime hardening through the installed workstation worker and audit the cross-boundary behavior without expanding authority.

The evidence stage must demonstrate both fail-closed stale-workspace handling and a successful exact-Quality path after the installed worker is running the current implementation.

## Exact starting state

AUTO-0018-04 completed on exact `master`:

```text
0a11e89e3e84ff7ae8602666264d325f359706c9
```

Exact post-merge Quality evidence for that commit is already terminal `SUCCESS` through the read-only relay. This does not by itself prove that the long-running workstation service has reloaded the newly merged runtime, so installed E2E evidence remains required.

## Installed-E2E precondition

The operator must explicitly update the validated local checkout to the exact current `master` commit and explicitly restart the canonical user service so the long-running process loads the current code.

This stage does not authorize hidden repository synchronization or hidden service control. No automatic fetch, pull, reset, checkout, merge, restart, enable, disable, or repair is performed by the worker.

Public evidence must not include workstation-local absolute paths, usernames, hostnames, credential values, private environment values, or unrelated machine metadata.

## Failure-mode probe

After the installed worker is confirmed to run the current implementation, publish one canonical `quality_verify` request whose `expected_head` is a known older public repository commit rather than the installed checkout HEAD.

Required terminal behavior:

- request is claimed once;
- execution fails before exact-Quality verification;
- result state is `FAILED`;
- result text contains bounded typed evidence with `kind=expected_head_mismatch`;
- evidence contains only the expected and observed public commit SHA plus deterministic operator guidance;
- `pre_clean` and `post_clean` remain true for a clean checkout;
- observed HEAD remains unchanged;
- no fetch, pull, reset, checkout, merge, clean, restore, or other repository mutation occurs;
- OpenCode is not invoked by this `quality_verify` mismatch path.

## Success-path probe

Publish a second canonical `quality_verify` request for exact current `master` with a distinct objective/request id.

Required terminal behavior:

- request is claimed once;
- exact-head preflight passes without mutation;
- verification remains independent of OpenCode;
- terminal state is `SUCCEEDED` only if exact Quality evidence satisfies the existing tuple;
- workflow path is `.github/workflows/quality.yml`;
- branch/event are `master` / `push`;
- head SHA is exact current `master`;
- workflow status is `completed` and conclusion is `success`;
- `satisfies_gate=true`;
- `pre_clean=true` and `post_clean=true`.

## Cross-boundary audit

The installed probes must preserve all approved boundaries:

- no new remote write/apply task class;
- no repository auto-synchronization or repair;
- no Actions rerun/cancel/dispatch;
- no service-control authority in the control protocol;
- no credential mutation;
- no deployment, release, publication, or PyPI mutation;
- no broader OpenCode permissions;
- no workstation-private details in public control-plane evidence.

## Completion rule

AUTO-0018-05 may be marked complete only after the installed failure-mode and success-path results are captured with exact request ids and terminal evidence, the cross-boundary audit passes, the evidence document is updated from `PENDING INSTALLED E2E` to verified status, and the normal PR-head/post-merge Quality gates succeed.
