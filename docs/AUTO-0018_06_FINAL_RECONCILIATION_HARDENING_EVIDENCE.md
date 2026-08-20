# AUTO-0018-06 — Final Reconciliation / Hardening Evidence

Status: FINAL RECONCILIATION / PENDING GATE

## Purpose

Reconcile AUTO-0018 against the approved design, the implemented runtime behavior, installed/E2E evidence, and the permanent authority/privacy boundaries before declaring the milestone complete.

This stage is documentation/evidence only. It does not add runtime behavior, task classes, repository mutation, workflow mutation, service-control authority, credentials, deployment, publication, release, or OpenCode authority.

## Delivery reconciliation

AUTO-0018 was delivered through the approved six-stage sequence:

1. `AUTO-0018-01` — design/contract, exact merged master `c925ae60f1a59f639daa61320f2783616e0d0b90`.
2. `AUTO-0018-02` — typed protocol-rejection and failure-taxonomy primitives, exact merged master `289634edbfcb12dc864b4776b5fee8299e375f49`.
3. `AUTO-0018-03` — bounded polling/transport resilience and low-noise observability, exact merged master `2a70e517acb80ded5810a0353922e960605e7829`.
4. `AUTO-0018-04` — non-mutating stale-workspace diagnostics and deterministic operator guidance, exact merged master `0a11e89e3e84ff7ae8602666264d325f359706c9`.
5. `AUTO-0018-05` — installed/E2E failure-mode evidence and cross-boundary audit, exact merged master `b59f651b4719f8463b3cde1132980a1cf340ad10`.
6. `AUTO-0018-06` — this final reconciliation/evidence stage.

## Implemented reliability / observability behavior

The final runtime preserves the existing read-only task-class set and adds deterministic diagnostics around that existing authority.

### Typed failure taxonomy

`ControlFailureKind` provides stable categories for transport read failure, protocol rejection, unsupported request, expected-head mismatch, repository snapshot failure, executor failure, exact Quality verification failure, and success.

Protocol rejection classification exposes bounded reason codes such as malformed JSON, schema mismatch, unsupported version, unknown task class, invalid request id, canonical request-id mismatch, and invalid field. Public-safe rejection evidence contains only the control comment id plus stable kind/reason values; raw request bodies and exception text are not copied into public diagnostics.

### Polling / transport resilience

Control-channel reads use deterministic bounded retry/backoff. Local structured diagnostics distinguish retry, failed-closed transport state, transport recovery, and polling start without producing per-poll control-channel chatter.

Comment/result publication is intentionally not retried, avoiding duplicate public claims/results after ambiguous write outcomes.

### Stale-workspace handling

Expected-head preflight is non-mutating. A mismatch returns typed `expected_head_mismatch` evidence containing only expected/observed public commit SHA values and deterministic operator guidance. The worker does not fetch, pull, reset, checkout, merge, clean, restore, or otherwise repair repository state automatically.

### Exact Quality path

`quality_verify` remains deterministic, read-only, and independent of OpenCode. Success still requires workflow `.github/workflows/quality.yml`, branch `master`, event `push`, exact target `head_sha`, terminal `completed`, conclusion `success`, and `satisfies_gate=true`.

## Installed / E2E evidence

AUTO-0018-05 exercised the installed worker after explicit operator synchronization and service reload.

The deliberately stale probe used request id:

```text
sha256:95acc26c3bb3f42628bf690427438e905a72f9cec2ace22a332573b99c7c19b5
```

It was claimed exactly once and terminated `FAILED` with `kind=expected_head_mismatch`, observed exact installed head `0a11e89e3e84ff7ae8602666264d325f359706c9`, and `pre_clean=true` / `post_clean=true`. The result demonstrated fail-closed stale-workspace handling without hidden repository synchronization.

The exact-head installed probe used request id:

```text
sha256:622339d2aee308ed14440c568188aa8457d36f3ed29b7a11cab759f40a808959
```

It terminated `SUCCEEDED` for exact head `0a11e89e3e84ff7ae8602666264d325f359706c9` with Quality run `32376689057`, workflow id `334955954`, branch/event `master` / `push`, `completed/success`, `satisfies_gate=true`, and clean pre/post evidence.

After AUTO-0018-05 merged, the first post-merge relay attempt intentionally demonstrated the same stale-workspace boundary until the operator explicitly fast-forwarded the installed checkout. After the confirmed fast-forward, the canonical verification request:

```text
sha256:10ee7ae15b853f79e89ed3dc3f75769422f3446931a29735a12540d199223523
```

terminated `SUCCEEDED` for exact master `b59f651b4719f8463b3cde1132980a1cf340ad10`. Evidence used Quality run `32379177746`, workflow id `334955954`, branch/event `master` / `push`, `completed/success`, `satisfies_gate=true`, and `pre_clean=true` / `post_clean=true`.

## Authority audit

AUTO-0018 did not add any remote write/apply task class. The protocol remains limited to `status`, `inspect`, `plan`, `diff`, and deterministic read-only `quality_verify`.

No automatic repository synchronization or repair was added. No Actions rerun/cancel/dispatch authority was added. No service start/stop/restart/enable/disable authority was added to the control protocol. No credential/token mutation, deployment, release, publication, or PyPI mutation was added. OpenCode permissions were not broadened.

The installed stale-workspace evidence confirms that this boundary is enforced in runtime rather than existing only as documentation.

## Public/private safety audit

AUTO-0018 diagnostics are constructed from bounded safe fields. Public protocol-rejection evidence does not carry raw request payloads or free-form exception text. Stale-workspace evidence contains only public commit identities and deterministic guidance. Installed evidence contains no workstation-local absolute paths, usernames, hostnames, credential values, private environment values, or unrelated machine metadata.

## Residual operational boundary

A long-running installed worker may legitimately lag behind a newly merged remote `master`. Exact-head requests fail closed in that state and require an explicit operator-reviewed local synchronization. This is an intentional safety boundary, not an unresolved request for hidden auto-repair authority.

AUTO-0018 therefore improves diagnosis of stale state without removing the human-controlled repository mutation boundary.

## Completion gate

AUTO-0018 may be declared COMPLETE / VERIFIED when this final reconciliation change passes exact PR-head Quality, merges with expected-head protection, and the exact merged `master` push passes the existing read-only post-merge Quality relay.

Until that final gate succeeds, AUTO-0018-06 remains pending and the milestone is not yet closed.
