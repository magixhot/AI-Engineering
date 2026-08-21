# AUTO-0020 — Canonical Project-State Documentation Coherence Gate Design

Status: DESIGN / PENDING GATE

## Purpose

Prevent the repository's canonical current-state documentation from silently
drifting behind verified delivery evidence.

AUTO-0020 defines one narrow machine-readable project-state contract, a
deterministic read-only coherence validator, and a Quality-gate integration
that detects contradictory current milestone/stage claims. It also reconciles
the existing canonical documents through AUTO-0019 after the validation
contract is established.

This milestone does not add documentation write/apply authority. It does not
change worker task classes, reconciliation execution authority, GitHub workflow
mutation authority, service-control authority, credentials, deployment,
publication, release, or OpenCode authority.

## Fresh post-AUTO-0019 audit

The audit was performed against exact verified `master`:

```text
c287e5cceef4e72148de7674f4095fedb78bd302
```

PR #190 merged the AUTO-0019 final reconciliation on that SHA. Push-triggered
Quality #394 (run id `32484748127`) completed successfully for exact event /
branch `push` / `master` and exact head above.

The repository implementation and exact evidence now complete AUTO-0019, but
the canonical bootstrap/state documents disagree:

- `docs/CURRENT_STATUS.md` still identifies AUTO-0014-06 as active;
- `docs/MASTER_INDEX.md` still identifies AUTO-0014-06 as active and omits the
  later active/completed milestone state;
- `docs/AI_CHAT_START.md` still tells a resumed session to continue from
  AUTO-0014-06;
- `docs/PROJECT_MAP.md` still reports AUTO-0014-06 as active;
- `docs/PROJECT_CONTEXT.md` still reports AUTO-0018-06 as active and uses the
  pre-final AUTO-0018 baseline;
- `docs/ROADMAP.md` still reports AUTO-0019 as design-active with AUTO-0019-01
  as the current priority.

AUTO-0017 performed a successful one-time reconciliation through AUTO-0016,
but later milestones again advanced evidence without a deterministic guard
that required all canonical current-state claims to advance together. Repeating
another unguarded text-only reconciliation would repair the present snapshot
without preventing the same class of drift.

Therefore the next safest milestone is a documentation-coherence gate before
selecting another runtime feature.

## Canonical document set

AUTO-0020 governs only these repository-level current-state documents:

1. `docs/AI_CHAT_START.md`;
2. `docs/PROJECT_CONTEXT.md`;
3. `docs/PROJECT_MAP.md`;
4. `docs/CURRENT_STATUS.md`;
5. `docs/ROADMAP.md`;
6. `docs/MASTER_INDEX.md`.

Historical design, stage, final-evidence, release, and ADR documents remain
immutable evidence except for separately reviewed corrections. The coherence
gate must not reinterpret a historical `PENDING GATE` label as a current-state
claim after later exact merge evidence exists.

## Relationship to existing documentation automation

AUTO-0002 and AUTO-0003 govern generated project-document synchronization and
ownership initialization for supported external engineering projects.
AUTO-0007 through AUTO-0012 govern reconciliation planning, guarded execution,
policy, approval, and evidence for those projects. AUTO-0017 was a repository
documentation reconciliation milestone.

AUTO-0020 is narrower and separate:

- it validates current-state coherence inside the AI-Engineering repository;
- it does not invoke AUTO-0002/AUTO-0003 apply behavior;
- it does not reuse AUTO-0008/AUTO-0009 mutation authority;
- it does not auto-edit any Markdown file;
- it does not turn documentation claims into runtime permissions.

## Canonical state contract

AUTO-0020 may add one tracked, machine-readable repository state manifest with
a versioned strict schema. The manifest is the source for only the minimal
current-state facts needed to detect contradiction, such as:

- schema version;
- last completed milestone;
- active milestone and active stage;
- active-state category;
- historical release line identity;
- canonical document-set version.

The manifest must not contain credentials, workstation paths, usernames,
hostnames, environment values, mutable external URLs, or hidden authority.

Exact commit/run evidence remains in reviewed stage/final documents. The
manifest must not require a self-referential commit SHA that is unknowable
before its own merge. A completed-through milestone claim may advance only in a
reviewed change that cites already-observed exact evidence.

## Read-only validator contract

The validator must be deterministic, offline, and read-only.

It must:

1. load exactly one supported manifest;
2. reject missing, duplicate, malformed, unknown-version, or unknown-field
   state;
3. inspect the complete canonical document set;
4. require each document to expose one unambiguous current-state claim in a
   stable machine-checkable form;
5. compare those claims with the manifest;
6. reject stale active milestone/stage claims and contradictory
   completed-through claims;
7. report bounded path/category diagnostics;
8. return non-zero on any ambiguity or mismatch;
9. leave repository bytes, index, worktree, refs, configuration, and remotes
   unchanged.

The validator must not infer current state from file modification time, GitHub
network state, prose ordering, PR numbers, branch names, or a partial document
subset.

## Stable claim boundary

The design may introduce a small explicit marker or fenced machine-readable
block in each canonical document. The marker must contain only the minimal
state keys required for comparison and must be human-readable alongside the
surrounding narrative.

The manifest must define a strict document-specific projection. A bootstrap or
current-status document may be required to match the active stage and current
priority, while an architecture/map document may need only completed-through
and active-milestone facts. A document must not duplicate state keys outside
its declared projection merely to satisfy the validator.

Free-form historical prose is not a safe parser input. The validator must not
attempt broad natural-language interpretation or rewrite prose to make a check
pass.

Missing, duplicated, malformed, or contradictory markers fail closed. Unknown
keys or schema versions fail closed until separately designed and tested.

## Quality integration

After focused implementation tests pass, the existing Quality workflow may run
the read-only coherence validator for pull requests and `master` pushes.

Quality integration must:

- use only repository checkout bytes;
- require no GitHub token or network call;
- perform no file generation or mutation;
- produce bounded deterministic diagnostics;
- fail before a contradictory state can merge;
- preserve all existing Ruff, mypy, pytest, and exact post-merge verification
  behavior.

AUTO-0020 does not authorize workflow dispatch, rerun, cancel, approval,
merge, ref mutation, or artifact publication.

## Reconciliation boundary

Once the manifest and validator are implemented and tested, the six canonical
documents will be reconciled through the last exact verified AUTO-0019 state
and the active AUTO-0020 stage.

The reconciliation may update reviewed documentation bytes only through normal
Git commits and pull requests. The validator itself remains read-only and may
only accept or reject the proposed state.

Immutable release facts remain unchanged: Git tag/release `v0.2.0` stays the
historical release boundary, later `master` milestones are not retroactively
inserted into that release, and PyPI remains not approved/not published.

## Failure and privacy requirements

Diagnostics may contain:

- portable repository-relative document paths;
- stable reason/category values;
- expected and observed milestone/stage identifiers;
- schema versions;
- bounded counts.

Diagnostics must not copy arbitrary document bodies, environment dumps,
credentials, authorization headers, workstation-local paths, usernames,
hostnames, or unrelated machine metadata.

Filesystem read errors, unsupported encodings, malformed state, or ambiguous
claims fail closed without partial success.

## Verification requirements

Focused tests must cover at minimum:

- one coherent canonical state;
- each governed document missing;
- manifest missing, duplicated, malformed, wrong-version, or unknown-field;
- marker missing, duplicated, malformed, or wrong-version;
- stale active milestone;
- stale active stage;
- contradictory completed-through milestone;
- historical prose containing older milestone names without becoming a false
  current-state mismatch;
- deterministic diagnostics independent of filesystem enumeration order;
- repository snapshot equality before and after validation;
- Quality workflow invocation of the validator;
- clean pass for the fully reconciled canonical document set.

## Explicit exclusions

AUTO-0020 MUST NOT add or imply:

- automatic documentation editing or repair;
- remote write/apply task classes;
- reconciliation apply/run authority;
- automatic Git fetch, pull, reset, checkout, merge, clean, or restore;
- Actions rerun/cancel/dispatch or merge authority;
- service-control mutation;
- credential/authentication mutation;
- deployment, release, publication, or PyPI changes;
- broader OpenCode access;
- a generic policy engine for arbitrary Markdown prose;
- replacement of historical evidence documents.

## Proposed delivery stages

1. `AUTO-0020-01` — Design / Contract.
2. `AUTO-0020-02` — Typed canonical-state manifest and strict parser.
3. `AUTO-0020-03` — Deterministic read-only cross-document validator.
4. `AUTO-0020-04` — Quality integration and failure-mode coverage.
5. `AUTO-0020-05` — Canonical document reconciliation and repository-wide
   coherence evidence.
6. `AUTO-0020-06` — Final reconciliation / next-milestone audit.

Every stage follows the normal exact gate: pre-merge Quality success on the
final PR head, expected-head-protected merge, and push-triggered Quality success
on the exact resulting `master` SHA.

## Completion rule

AUTO-0020 is complete only when one strict canonical state is represented
consistently across all six governed documents, deterministic offline
validation rejects stale/ambiguous state without modifying the repository, the
Quality workflow enforces that validation, historical/public/private
boundaries remain intact, repository-wide evidence passes, and final exact
post-merge Quality succeeds.
