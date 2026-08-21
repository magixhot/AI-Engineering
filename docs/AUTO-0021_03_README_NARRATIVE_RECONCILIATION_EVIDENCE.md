# AUTO-0021-03 — README Narrative Reconciliation Evidence

## Input Baseline

AUTO-0021-02 merged through PR #199 as exact `master`
`8363f50e86470092cdccf116e8dc00dcc8f9d43c`. Pre-merge Quality #411 and
push-triggered Quality #412 (run id `32508353783`) completed successfully.

The baseline already enforces document-set v2 with `README.md` first and
retains exact document-set v1 compatibility.

## Reconciled Landing Claims

Repository-root `README.md` now states:

- completion through AUTO-0020;
- AUTO-0021-01 and AUTO-0021-02 completion;
- AUTO-0021-03 as the only active stage;
- the exact read-only remote task classes `status`, `inspect`, `plan`, `diff`,
  and `quality_verify`;
- the AUTO-0019 no-replay recovery boundary;
- the offline/read-only document-set v2 coherence contract;
- the exact verified pre-stage baseline;
- immutable release line `v0.2.0` and no PyPI approval/publication claim.

The strict marker remains directly after the H1 and is the only README input
to the coherence validator. Historical or current narrative remains outside
the parser by design.

## Preserved Boundaries

This stage changes documentation only. It does not add prose parsing, generic
Markdown policy, remote task classes, executor or OpenCode authority,
automatic repair, workflow control, service/credential mutation, deployment,
release, publication, or PyPI authority.

Open issue #130 remains a separate external operational surface and is not
mutated by this repository-byte stage.

## Gate

AUTO-0021-03 remains active until the reconciled README and canonical stage
state pass exact PR-head Quality, expected-head-protected merge, and exact
push-triggered post-merge Quality.
