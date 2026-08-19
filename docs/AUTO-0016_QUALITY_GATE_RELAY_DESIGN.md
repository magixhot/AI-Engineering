# AUTO-0016-01A — Exact Quality Gate Relay Design

Status: DESIGN / PENDING GATE

## Purpose

Define a read-only relay that removes manual operator `SUCCESS` confirmation after merge. The existing local worker will read authoritative GitHub Actions evidence for one exact merged `master` SHA and publish bounded typed evidence into the existing GitHub control issue.

## Control path

```text
External AI operator
        |
        v
GitHub control issue request: quality_verify
        |
        v
Installed local worker
        |
        v
GhActionsReadTransport + exact Quality verifier
        |
        v
GitHub Actions read API
        |
        v
GitHub control issue typed result
        |
        v
External AI operator continues the stage gate
```

OpenCode is intentionally not in the `quality_verify` execution path. Exact Quality verification is deterministic repository-control evidence and must use the typed AUTO-0015 verifier directly. Existing OpenCode-backed `status`, `inspect`, `plan`, and `diff` task classes remain unchanged.

## Allowed task

The relay adds one narrowly-scoped read-only task class:

- `quality_verify` — verify `.github/workflows/quality.yml` for repository `magixhot/AI-Engineering`, branch `master`, event `push`, and one exact lowercase 40-character merged SHA.

The request must contain the exact target SHA. No natural-language request field may alter workflow, branch, event, repository, or verification semantics.

## Typed result

A terminal relay result records only bounded public-safe evidence:

- deterministic request id;
- repository;
- workflow path;
- branch;
- event;
- exact target SHA;
- verifier state (`PENDING`, `SUCCEEDED`, `FAILED`, `AMBIGUOUS`, `INVALID`, or `UNAVAILABLE`);
- `satisfies_gate` boolean;
- when available: workflow run id, workflow id, run attempt, status, and conclusion.

Only `SUCCEEDED` with `satisfies_gate=true` opens the post-merge gate.

## Authority boundary

This relay MUST NOT add or call:

- workflow rerun, cancel, dispatch, delete, or mutation;
- pull-request merge or repository/ref write;
- file write/apply, reconciliation apply/run, commit, push, checkout, reset, or stash mutation;
- package install, service start/stop/restart, deployment, or publication;
- arbitrary shell commands supplied by the remote request;
- OpenCode edit/write authority;
- credential, token, environment, local username, or absolute-path disclosure.

The worker may use authenticated `gh api` GET reads through the existing AUTO-0015 transport and may post the bounded result comment to the already-authorized control issue. Posting claim/result evidence is transport bookkeeping, not project mutation authority.

## Control issue reliability

The relay must consume the existing control issue through full pagination rather than the historical first-100-comments limitation. Duplicate or replayed request identifiers must remain fail-closed/idempotent.

## Failure behavior

Missing runs remain `PENDING`. Terminal non-success is `FAILED`. Multiple distinct exact matching run ids are `AMBIGUOUS`. Invalid request identity is `INVALID`. GitHub/transport/schema failures are `UNAVAILABLE`. None of these states may advance the stage gate.

## Delivery

1. **AUTO-0016-01A — Relay Design / Contract**: this document only.
2. **AUTO-0016-01B — Typed Relay Protocol + Worker Integration**: specialized request/result protocol, worker routing, paginated control transport, tests.
3. **AUTO-0016-01C — Installed Relay Verification**: update the installed local worker, submit a real `quality_verify` request, receive typed `SUCCEEDED` evidence in the control issue, and prove no repository/OpenCode authority expansion.

After AUTO-0016-01C is COMPLETE / VERIFIED, later stages must use relay evidence instead of asking the human operator to type `SUCCESS` or creating synthetic probe pull requests.

Each relay stage follows the normal pre-merge Quality, expected-head merge, and exact post-merge gate. Until 01C is live, the already-proven probe-PR mechanism may be used only as bootstrap evidence for these relay stages.
