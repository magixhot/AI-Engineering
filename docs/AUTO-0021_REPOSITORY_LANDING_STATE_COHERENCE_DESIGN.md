# AUTO-0021 — Repository Landing State Coherence

## Purpose

Extend the existing strict canonical project-state gate to the repository-root
`README.md`, which is both the GitHub landing page and the first document in
the session bootstrap order.

This milestone remains offline, deterministic, and read-only at validation
time. It does not authorize a generic Markdown policy engine or any remote
GitHub state mutation.

## Verified Input Baseline

AUTO-0020 and its terminal quiescent-state correction are COMPLETE / VERIFIED.
PR #197 merged as exact `master`
`c72c79a477de630f50532a454e11d513e9727a79`. Pre-merge Quality #407 and
push-triggered Quality #408 (run id `32504454989`) completed successfully.

The exact baseline has:

- schema v2 terminal `QUIESCENT` support;
- schema v1 active-manifest compatibility;
- exactly six governed canonical Markdown documents;
- deterministic offline validation in Quality;
- no approved successor before this design.

## Fresh Audit Finding

`docs/AI_CHAT_START.md` requires readers to open `README.md` first.
`README.md` is also the default public GitHub landing page.

At the exact baseline, `README.md` still claims:

- current phase `AUTO-0018-06`;
- AUTO-0018-06 pending;
- exact baseline
  `b59f651b4719f8463b3cde1132980a1cf340ad10`.

The strict manifest governs only six files under `docs/`, so Quality can
correctly report `{"coherent":true,"issues":[]}` while the first public
project-state surface contradicts them.

This is a document-set boundary gap, not a validator-algorithm failure.

## Selected Scope

AUTO-0021 governs exactly one additional surface:

```text
README.md
```

The current six governed documents remain unchanged members of the set. No
glob, directory scan, filename heuristic, natural-language parser, or
repository-wide arbitrary Markdown policy is introduced.

## Document-Set v2 Contract

The current manifest schema remains version 2. The document set advances from
version 1 to version 2.

Document-set v1 remains accepted with its exact historical six-document
projection. Document-set v2 requires the exact seven-document set, with
`README.md` first in deterministic validation order.

`README.md` projects:

1. `completed_through`;
2. `active_milestone`;
3. `active_stage`;
4. `active_state`;
5. `release_line`.

It must contain exactly one strict `canonical-project-state` marker directly
after its top-level heading. The marker uses the existing JSON/null semantics.

Unknown document-set versions, missing/extra paths, wrong projection order,
duplicate fields, and mixed version/set combinations fail closed.

## Compatibility

The parser must preserve:

- schema v1 active-manifest compatibility;
- schema v2 active and `QUIESCENT` lifecycle behavior;
- document-set v1 exact six-document compatibility;
- stable bounded error categories;
- existing canonical marker syntax and diagnostics.

The validator already iterates the typed manifest projections. It must not
special-case README prose or infer state from headings, badges, dates, Git
history, GitHub metadata, or release objects.

## README Reconciliation

After the v2 marker and document-set contract are enforced, README narrative
will be reconciled to:

- completed state through AUTO-0020;
- active AUTO-0021 stage at the time of reconciliation;
- current read-only control-plane task classes and no-replay recovery
  boundary;
- schema/document-set coherence behavior;
- immutable release line `v0.2.0`;
- no PyPI approval/publication claim.

Historical release facts remain immutable. Later `master` milestones are not
retroactively inserted into the `v0.2.0` release.

## Quality Integration

No workflow mutation is required. The existing command:

```text
uv run python -B -m ai_engineering.project_state_coherence .
```

loads the manifest and therefore begins enforcing README automatically when
the current manifest advances to document-set v2.

Validation remains:

- repository-checkout-only;
- offline;
- read-only;
- bytecode-disabled in Quality;
- bounded in diagnostics;
- ordered by the typed projection list.

## Verification Requirements

Focused tests must cover:

- document-set v1 exact six-document compatibility;
- document-set v2 exact seven-document construction;
- README first in deterministic order;
- missing README;
- README directory or symlink;
- missing, duplicate, malformed, wrong-version, stale, or extra-field marker;
- fabricated successor in a quiescent marker;
- active AUTO-0021 marker matching;
- unknown document-set version;
- v1/v2 projection mismatch;
- historical README prose not parsed as current state;
- tracked repository coherence;
- repository snapshot equality before/after validation;
- existing Ruff, mypy, pytest, and exact post-merge Quality behavior.

## Explicit Exclusions

AUTO-0021 does not authorize:

- automatic README or documentation repair;
- generic Markdown policy or prose interpretation;
- GitHub repository-description/topic mutation;
- control-issue body mutation;
- network validation from Quality;
- new remote task classes;
- reconciliation apply/run authority changes;
- workflow rerun/cancel/dispatch;
- service or credential mutation;
- deployment, release, publication, or PyPI work;
- broader OpenCode authority.

The open control issue #130 has a separately observed stale task-class
description. It is an external operational surface and is deliberately not
folded into this offline repository-byte milestone.

## Delivery Stages

1. `AUTO-0021-01` — design/contract and fresh audit evidence.
2. `AUTO-0021-02` — typed document-set v2 compatibility, README marker
   bootstrap, and focused failure-mode tests.
3. `AUTO-0021-03` — README narrative reconciliation and public landing
   evidence.
4. `AUTO-0021-04` — final reconciliation and next-surface audit.

Every stage requires exact PR-head Quality success, expected-head-protected
merge, and push-triggered Quality success on the exact resulting `master`
SHA.

## Completion Rule

AUTO-0021 is complete only when README and the existing six canonical
documents represent one strict current state, Quality enforces the exact
seven-document set offline without repository mutation, README narrative is
reconciled, compatibility tests pass, and the final exact post-merge Quality
gate succeeds.
