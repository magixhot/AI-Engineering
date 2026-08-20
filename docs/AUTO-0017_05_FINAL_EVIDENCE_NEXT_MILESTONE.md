# AUTO-0017-05 — Final Evidence / Next-Milestone Selection

Status: FINAL EVIDENCE / PENDING GATE

## Reconciled baseline

AUTO-0017 reconciled canonical current-state documentation with the verified engineering state through AUTO-0016 without changing runtime behavior, remote task authority, workflow mutation authority, service-control authority, credentials, publication scope, or immutable release history.

Verified delivery sequence:

- AUTO-0017-01 — Design / Contract: COMPLETE / VERIFIED.
- AUTO-0017-02 — Canonical Roadmap Reconciliation: COMPLETE / VERIFIED.
- AUTO-0017-03 — Project Context / Start-State Reconciliation: COMPLETE / VERIFIED.
- AUTO-0017-04 — Cross-Document Consistency Audit: COMPLETE / VERIFIED.
- AUTO-0017-05 — Final Evidence / Next-Milestone Selection: this stage.

The canonical current-state documents now agree on these boundaries:

- AUTO-0001 through AUTO-0016 are complete for their approved scopes.
- AUTO-0007 remains permanent read-only reconciliation planning.
- AUTO-0008 through AUTO-0012 retain their existing guarded execution/policy/evidence authority boundaries.
- AUTO-0013 remains bounded read-only remote control transport.
- AUTO-0014 remains local worker lifecycle supervision.
- AUTO-0015 remains exact post-merge Quality verification with no workflow mutation authority.
- AUTO-0016 remains portable workstation bootstrap/doctor plus the narrow read-only Quality relay.
- `v0.2.0` remains an immutable historical release boundary; later `master` work does not alter it.
- PyPI remains not approved and not published.

## Fresh post-reconciliation hardening audit

The corrected state exposed a reliability/operability gap in the read-only control plane that is safer to address before expanding execution authority.

Observed hardening findings:

1. Malformed or non-canonical control requests fail closed, but the worker currently skips protocol-parse failures without publishing a typed rejection or operator-visible diagnostic. This recently made a canonical request-id mismatch look like a relay outage until the local parser was exercised directly.
2. Exact-head fail-closed behavior is correct, but a stale local checkout can make an otherwise healthy worker refuse requests. The current operator path requires manual diagnosis and workspace synchronization.
3. Normal polling is intentionally quiet, so a live-but-idle worker and a worker repeatedly discarding malformed requests are difficult to distinguish from GitHub-side evidence alone.
4. Existing authority boundaries must remain unchanged while these reliability and observability gaps are addressed.

These findings do not justify new write/apply authority. They justify hardening the existing read-only control path first.

## Next milestone selection

Selected next milestone candidate:

**AUTO-0018 — Read-Only Control Plane Reliability / Observability Hardening**

Recommended design scope:

- preserve the existing read-only task-class and authority boundaries;
- add deterministic operator-visible diagnostics for malformed/ignored control requests without leaking secrets or workstation-private details;
- harden worker polling/error reporting so transport, protocol, expected-head, and executor failures are distinguishable;
- define safe stale-workspace detection/recovery guidance without granting hidden repository mutation authority;
- preserve exact post-merge Quality verification semantics and no rerun/cancel/dispatch authority;
- add tests and evidence for the failure modes discovered during AUTO-0017 relay diagnosis.

Explicitly out of scope for selection:

- new remote write/apply task classes;
- automatic `git pull`, reset, checkout, merge, or repository repair by the worker;
- workflow rerun/cancel/dispatch;
- service-control mutation;
- credential mutation;
- deployment, release, publication, or PyPI changes;
- any expansion of OpenCode authority.

## Approval boundary

AUTO-0017 selects AUTO-0018 as the next design target only. It does not preapprove AUTO-0018 implementation. Any runtime behavior change, new authority, automatic repair, publication, credential, or architecture change requires a separate explicit approval and design gate.

## AUTO-0017 completion condition

AUTO-0017 is complete when this final evidence is merged and exact post-merge Quality succeeds for the merged `master` SHA.
