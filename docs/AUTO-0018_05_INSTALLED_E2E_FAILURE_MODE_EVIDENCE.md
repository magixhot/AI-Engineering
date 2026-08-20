# AUTO-0018-05 — Installed / E2E Failure-Mode Evidence

Status: EVIDENCE / VERIFIED INSTALLED E2E

## Purpose

Verify the AUTO-0018 runtime hardening through the installed workstation worker and audit the cross-boundary behavior without expanding authority.

The evidence stage demonstrates both fail-closed stale-workspace handling and a successful exact-Quality path after the installed worker is running the current implementation.

## Exact starting state

AUTO-0018-04 completed on exact `master`:

```text
0a11e89e3e84ff7ae8602666264d325f359706c9
```

The operator reported the installed checkout at this exact SHA and the canonical worker service as active before the probes. The public control-plane results below independently demonstrate behavior introduced by AUTO-0018-04 and preserve clean repository evidence.

## Installed stale-workspace probe

Canonical request id:

```text
sha256:95acc26c3bb3f42628bf690427438e905a72f9cec2ace22a332573b99c7c19b5
```

The request deliberately used older public commit `2a70e517acb80ded5810a0353922e960605e7829` as `expected_head` while the installed checkout remained at `0a11e89e3e84ff7ae8602666264d325f359706c9`.

Terminal evidence:

- request was claimed once;
- terminal state: `FAILED`;
- task class: `quality_verify`;
- branch: `master`;
- observed HEAD: `0a11e89e3e84ff7ae8602666264d325f359706c9`;
- `pre_clean=true` and `post_clean=true`;
- typed reason: `expected_head_mismatch`;
- public evidence contains the expected and observed public commit SHA plus deterministic operator guidance;
- the observed HEAD was unchanged;
- no repository synchronization or repair occurred;
- exact Quality verification was not entered for the mismatched head, so this path remained independent of OpenCode and fail-closed before executor work.

This is the required installed proof that stale-workspace diagnosis is typed, bounded, non-mutating, and operator-visible.

## Installed exact-head Quality probe

Canonical request id:

```text
sha256:622339d2aee308ed14440c568188aa8457d36f3ed29b7a11cab759f40a808959
```

The request used exact current `master` `0a11e89e3e84ff7ae8602666264d325f359706c9`.

Terminal evidence:

- request was claimed once;
- terminal state: `SUCCEEDED`;
- task class: `quality_verify`;
- branch/event: `master` / `push`;
- workflow path: `.github/workflows/quality.yml`;
- workflow id: `334955954`;
- workflow run id: `32376689057`;
- exact head SHA: `0a11e89e3e84ff7ae8602666264d325f359706c9`;
- workflow status: `completed`;
- workflow conclusion: `success`;
- `satisfies_gate=true`;
- `pre_clean=true` and `post_clean=true`.

This proves the exact-head path still reaches the deterministic read-only Quality verifier and preserves the existing exact tuple without OpenCode dependence.

## Cross-boundary audit

PASS. The installed probes preserve all approved boundaries:

- no new remote write/apply task class;
- no repository auto-synchronization or repair;
- no Actions rerun/cancel/dispatch;
- no service-control authority in the control protocol;
- no credential mutation;
- no deployment, release, publication, or PyPI mutation;
- no broader OpenCode permissions;
- no workstation-private details in public control-plane evidence.

The stale-workspace result proves that mismatch handling reports only public-safe commit identifiers and deterministic guidance while preserving repository cleanliness. The success-path result proves that exact Quality verification remains read-only and exact-head gated.

## Completion rule

The installed failure-mode and success-path evidence requirements are satisfied. AUTO-0018-05 may be marked complete after this evidence branch passes exact PR-head Quality, merges with expected-head protection, and the exact post-merge `master` push Quality gate succeeds through the read-only relay.
