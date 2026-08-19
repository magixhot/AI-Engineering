# AUTO-0015 — Exact Post-Merge Quality Verifier Design

**Status:** DESIGN / CONTRACT ONLY

## Purpose

AUTO-0015 defines a read-only verifier for the exact post-merge GitHub Actions Quality gate on `master`.

The operational gap after AUTO-0014 is narrow but important: the external operator can merge a pull request and know the exact resulting `master` SHA, but the currently available connector path cannot reliably enumerate the push-triggered `Quality` workflow run for that exact merge SHA. This leaves a manual GitHub Actions confirmation step between stages.

AUTO-0015 removes that manual confirmation by defining a deterministic, fail-closed, read-only verification path for the exact merged commit.

AUTO-0015 does **not** authorize workflow reruns, workflow cancellation, workflow dispatch, pull-request merge, branch mutation, repository mutation, service control, deployment, publication, or any reconciliation mutation.

## Verified repository workflow identity

The repository has one tracked Quality workflow:

```text
.github/workflows/quality.yml
name: Quality
```

It runs on both:

```text
pull_request -> master
push         -> master
```

The post-merge gate is specifically the `push` run on `master`, not the pull-request run.

Workflow identity MUST be anchored by the tracked workflow path `quality.yml` (or its resolved GitHub workflow id), not by display name alone.

## GitHub Actions read contract

The verifier may use the GitHub Actions read endpoint for workflow runs:

```text
GET /repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs
```

The query MUST constrain at least:

```text
branch=master
event=push
head_sha=<exact merged master SHA>
```

The GitHub API supports `branch`, `event`, and `head_sha` filtering for workflow-run enumeration. The verifier must not broaden a failed exact query into an unconstrained search and then guess which run is authoritative.

Only read access is required. Authentication, when used, remains external runtime configuration and must never be written into tracked files, logs, receipts, or public evidence.

## Exact input contract

Verification input is immutable and explicit:

```text
repository: owner/name
branch: master
workflow: .github/workflows/quality.yml
head_sha: 40-character exact commit SHA
event: push
```

The verifier MUST reject malformed repository identities, non-40-character SHAs, unsupported branches, unsupported workflow paths, or unsupported events before any result can be accepted.

AUTO-0015 initially supports only the repository's existing post-merge Quality gate on `master`.

## Typed verification states

The verifier must return one of a small typed state set:

- `PENDING` — no authoritative terminal result is available yet, or the exact run is queued/in progress;
- `SUCCEEDED` — the exact matching run is completed with conclusion `success`;
- `FAILED` — the exact matching run is completed with a non-success terminal conclusion;
- `AMBIGUOUS` — more than one distinct authoritative run matches the exact identity and cannot be deterministically reduced;
- `INVALID` — input or response structure violates the contract;
- `UNAVAILABLE` — the read transport cannot obtain authoritative GitHub evidence.

Only `SUCCEEDED` may satisfy a post-merge stage gate.

`PENDING`, `FAILED`, `AMBIGUOUS`, `INVALID`, and `UNAVAILABLE` must all fail closed with respect to stage advancement.

## Exact success predicate

A post-merge gate is successful only when all of the following are true for the same authoritative workflow run:

```text
repository == expected owner/name
workflow identity == .github/workflows/quality.yml
head_branch == master
head_sha == exact expected merge SHA
event == push
status == completed
conclusion == success
```

A matching display title, short SHA, PR number, branch name alone, latest run, or successful PR-triggered run is insufficient.

## Multiple-run and rerun semantics

GitHub may expose rerun attempts or multiple records associated with similar identities. AUTO-0015 must define deterministic handling rather than selecting the newest-looking result by convenience.

The implementation must distinguish a rerun attempt of the same workflow-run identity from multiple distinct workflow runs for the same exact tuple.

A later implementation stage must prove the exact canonicalization rule with fixtures before live verification. If multiple distinct runs remain equally authoritative after the defined rule, the result is `AMBIGUOUS`, not `SUCCEEDED`.

AUTO-0015 itself may never request a rerun to resolve ambiguity or failure.

## Bounded polling contract

A caller may re-check a `PENDING` verification after a bounded delay. Polling is read-only and must be bounded.

The verifier must not busy-loop, create GitHub traffic floods, or silently convert a terminal `FAILED` state into indefinite polling.

A caller may impose a timeout, but timeout expiry yields a fail-closed non-success state; it does not weaken the exact success predicate.

## Evidence model

Successful verification evidence should be compact and non-secret. It may include:

```text
repository
workflow path or stable workflow id
run id
run attempt when available
head branch
exact head SHA
event
status
conclusion
```

Evidence must not include authorization headers, access tokens, cookies, environment dumps, unrelated account data, or full raw API responses when a bounded typed projection is sufficient.

The exact merged SHA remains the primary linkage between merge evidence and Quality evidence.

## Authority boundary

AUTO-0015 is observation only.

It may:

- read workflow-run metadata;
- validate exact workflow/run identity;
- project a typed verification result;
- expose bounded evidence for stage-gate decisions.

It may not:

- rerun failed jobs or workflows;
- cancel workflow runs;
- dispatch workflows;
- enable or change auto-merge;
- merge pull requests;
- create/update/delete refs;
- modify repository files;
- change branch protection;
- change workflow definitions;
- approve deployments;
- invoke AUTO-0008/AUTO-0009 mutation paths;
- start/stop local services;
- grant any later stage mutation authority.

A `SUCCEEDED` verification is evidence only. It does not itself perform the next operation.

## Transport boundary

The implementation may use a dedicated GitHub Actions read transport or an existing authenticated GitHub CLI/API read path, but the domain verifier must remain transport-independent and testable with deterministic fixtures.

Transport errors, permission failures, malformed JSON, pagination gaps, truncated result sets, or unexpected schema values must fail closed.

Pagination must be handled explicitly if the selected endpoint can return more results than one page. The implementation must never treat a partial first page as proof of uniqueness.

## Integration with staged delivery

The intended operational sequence after AUTO-0015 is:

```text
pre-merge Quality SUCCESS on exact PR head
-> merge with expected-head protection
-> obtain exact resulting master SHA
-> verify exact push-triggered Quality for that SHA
-> advance only on typed SUCCEEDED
```

This removes the manual GitHub UI confirmation step while preserving the existing gate semantics.

AUTO-0015 does not automate the merge itself and does not automatically start the next stage. Those remain separate orchestrator/operator decisions governed by existing repository contracts.

## Verification requirements

Later implementation must prove at minimum:

- exact `head_sha` matching rejects neighboring or short SHAs;
- PR-triggered Quality cannot satisfy a post-merge gate;
- non-`master` runs cannot satisfy the gate;
- wrong workflow identity cannot satisfy the gate;
- queued/in-progress run returns `PENDING`;
- completed/success returns `SUCCEEDED` only for the exact tuple;
- completed/failure/cancelled/timed_out/action_required/stale or other non-success terminal conclusions cannot satisfy the gate;
- malformed API responses fail closed;
- transport/auth/read failures fail closed;
- pagination does not create false uniqueness;
- duplicate/distinct matching runs follow deterministic canonicalization or return `AMBIGUOUS`;
- typed evidence contains no credentials or raw secret-bearing headers/bodies;
- verifier execution does not mutate repository state, workflow state, refs, PRs, issues, or local services;
- existing AUTO-0007 through AUTO-0014 tests remain green.

## Non-goals

AUTO-0015 does not introduce:

- CI workflow redesign;
- branch-protection redesign;
- merge queue authority;
- automatic PR merge;
- workflow repair or rerun;
- flaky-test retry policy;
- deployment gates;
- release automation;
- private control-plane migration;
- local workstation bootstrap;
- package-manager installation;
- credential provisioning.

Workstation bootstrap and a read-only workstation prerequisite doctor are intentionally a separate approved future milestone so environment provisioning does not become coupled to CI evidence verification.

## Staged delivery contract

AUTO-0015 is delivered strictly in order:

1. **AUTO-0015-01 — Exact Post-Merge Quality Verifier Design / Contract**: this document and planning synchronization only; no production implementation.
2. **AUTO-0015-02 — Typed Workflow-Run Evidence Model**: strict typed inputs, states, projections, and fail-closed validation.
3. **AUTO-0015-03 — GitHub Actions Read Transport**: bounded read-only workflow-run enumeration with pagination and safe error handling.
4. **AUTO-0015-04 — Exact Quality Verification Service / CLI**: deterministic exact-tuple selection and operator-facing read-only verification command.
5. **AUTO-0015-05 — Live Exact Post-Merge Verification**: prove the verifier against a real merged `master` SHA without manual GitHub UI confirmation.
6. **AUTO-0015-06 — Final Evidence / Documentation Reconciliation**: authoritative closure evidence and documentation synchronization only.

Each stage requires its own pre-merge Quality SUCCESS, merge, and exact post-merge Quality SUCCESS before the next stage begins.

## Next planned workstation milestone

After AUTO-0015 closure, the next approved design direction is a reproducible workstation bootstrap / doctor milestone.

That milestone will document and then read-only verify the prerequisites required on a fresh computer, including Windows/WSL, Linux/systemd, Git, Python, GitHub CLI/authentication, repository checkout, OpenCode installation/localhost health, project-local OpenCode agent configuration, AUTO-0014 worker config/service installation, external connector/account boundaries, security exclusions, troubleshooting, and a final `NEW WORKSTATION READY` checklist.

It must separate portable repository prerequisites, local workstation configuration, and external account/connector configuration so a new machine can be prepared without rediscovering the setup manually.

## Stage-01 completion rule

AUTO-0015-01 may be marked COMPLETE / VERIFIED only after this design-only change passes pre-merge Quality, is merged, and the exact resulting `master` commit passes post-merge Quality.

Production implementation must not begin before that gate is complete.
