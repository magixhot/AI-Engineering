# AUTO-0006 — Engineering Project Health / Readiness Audit Design

**Document ID:** AUTO-0006
**Status:** Design / Proposed
**Date:** 2026-08-16

## 1. Purpose

AUTO-0006 defines a deterministic, read-only health and readiness audit for an existing AI-Engineering project.

The audit answers one bounded operational question:

> What is the current engineering state of this project, and which already-approved workflow should be used next?

AUTO-0006 does not repair, migrate, synchronize, initialize, execute, publish, or otherwise modify the target project. It composes existing verified read-only contracts into one stable report.

## 2. Why This Milestone Is Next

After AUTO-0005, AI-Engineering can create a V2 engineering project, initialize documentation ownership, synchronize managed documentation, identify supported V1/V2 baselines, plan guarded migrations, and apply the first production V1-to-V2 migration.

The remaining operational gap is discovery across those workflows. A user or automation currently has to know which command to run first and interpret several independent states.

AUTO-0006 closes that gap without expanding the execution or publication surface.

## 3. Scope

AUTO-0006 V1 shall provide a local, deterministic, read-only project audit that reports:

- project root and basic inspection state;
- supported engineering identity state;
- Git repository/root/HEAD/branch state needed for readiness reporting;
- documentation ownership state;
- documentation synchronization state when ownership permits evaluation;
- migration readiness for explicitly registered production migrations;
- one overall health/readiness state;
- deterministic recommended next action selected only from already-approved public workflows.

The installed CLI target is:

```text
ai-engineering project health --project PATH
```

No `apply`, `fix`, `repair`, or implicit mutation subcommand is part of AUTO-0006 V1.

## 4. Non-Goals

AUTO-0006 V1 does not:

- modify project files;
- initialize documentation ownership markers;
- synchronize documentation;
- apply migrations;
- stage, commit, reset, checkout, branch, tag, fetch, pull, push, or modify Git remotes;
- install or update dependencies;
- execute project Python code, tests, build backends, package managers, hooks, or arbitrary commands;
- contact network services;
- read or publish credentials or secrets;
- create release artifacts, tags, GitHub Releases, TestPyPI, or PyPI publications;
- add a new migration edge or baseline;
- infer unsupported project identity heuristically;
- perform fuzzy matching, AI-generated repair, or conflict resolution.

## 5. Architectural Rule: Compose Existing Contracts

AUTO-0006 shall prefer the existing public read-only APIs rather than reimplementing their policy.

The health layer may compose:

- `inspect_project_state(...)` from AUTO-0002;
- documentation ownership classification/planning from AUTO-0003;
- documentation synchronization inspection/planning from AUTO-0002;
- `detect_project_identity(...)` and explicit migration registry resolution/planning from AUTO-0004/AUTO-0005.

AUTO-0006 may add narrowly scoped read-only Git observation needed for its report, but it must not weaken existing Git authority/root guarantees and must not introduce Git mutation.

Write/apply APIs must never be called by the health audit.

## 6. Result Model

The implementation shall expose a typed immutable result model. Exact Python names may be finalized during implementation, but the public concepts are fixed by this design.

A health report contains:

- resolved project root;
- inspection result;
- identity result;
- Git readiness result;
- documentation ownership result;
- documentation synchronization result;
- migration readiness result;
- overall state;
- recommended next action;
- deterministic issue records.

Each issue record shall have a stable machine-readable code, severity/state, bounded description, and optional affected path or workflow identifier.

## 7. Overall States

AUTO-0006 V1 uses these overall states:

### `healthy`

The project is positively identified as the current supported engineering baseline, required documentation ownership is initialized, managed documentation is synchronized, and no blocking/manual-review condition is present.

### `action_required`

The project is positively understood and an already-approved deterministic workflow can advance it. Examples include:

- supported legacy V1 identity with the registered V1-to-V2 migration available;
- safely initializable documentation ownership;
- deterministic documentation drift that AUTO-0002 can synchronize.

### `manual_review`

The project is recognized enough to diagnose, but an existing fail-closed contract reports ambiguity, malformed ownership, local machine-owned modification, unsupported file type/link state, or another condition requiring human review.

### `unsupported`

The project cannot be positively identified as a supported engineering project or cannot be safely inspected under the approved contracts.

No state may be upgraded from `manual_review` or `unsupported` by heuristic fallback.

## 8. Deterministic Precedence

When multiple conditions exist, the overall state shall use this precedence from most restrictive to least restrictive:

```text
unsupported
manual_review
action_required
healthy
```

The recommended next action must correspond to the highest-priority actionable condition and shall be selected deterministically.

## 9. Recommended Next Actions

AUTO-0006 may recommend only an existing approved public workflow or explicit human review.

Allowed V1 recommendations are bounded to concepts equivalent to:

```text
none
manual_review
project migrate plan --migration python-engineering-v1-to-v2
project docs ownership plan
project docs plan
```

The report may include the target project path separately. It shall not construct shell command strings containing untrusted quoting or execute the recommendation.

If a project is V1 and the approved production migration is available, migration readiness takes precedence over documentation synchronization against the legacy baseline.

For an exact V2 project, documentation ownership/synchronization readiness determines whether additional action is required.

## 10. Identity Rules

AUTO-0006 must reuse the positive identity boundary established by AUTO-0004/AUTO-0005.

Supported V1 and V2 identities may be reported positively.

Malformed, contradictory, unsupported, or unapproved `.ai-engineering.toml` content must remain fail-closed and must never fall back to legacy V1 identity.

Unsupported projects receive `unsupported`; AUTO-0006 must not invent a profile or baseline.

## 11. Documentation Readiness Rules

Documentation readiness is evaluated using existing AUTO-0003/AUTO-0002 semantics.

The report must distinguish at least:

- ownership initialized;
- ownership initialization available;
- ownership manual review required;
- synchronization clean;
- synchronization drift/action available;
- synchronization manual review required;
- synchronization blocked because ownership is not initialized.

AUTO-0006 shall not initialize markers implicitly and shall not write managed sections.

## 12. Migration Readiness Rules

Migration readiness is registry-driven and explicit.

For V1:

- the report may identify `python-engineering-v1-to-v2` as available only through the production registry;
- read-only migration planning may be used to distinguish ready from manual-review/conflict states;
- the audit never calls guarded apply.

For exact V2:

- the V1-to-V2 edge is already-target/idempotent and is not reported as required work.

Unknown migration ids or future baselines are not inferred.

## 13. Git Readiness and Invariants

AUTO-0006 is read-only with respect to Git.

It may inspect repository root, branch, HEAD, staged/unstaged/untracked state when required for diagnosis, using bounded subprocess invocation with argument lists, `shell=False`, captured output, and no stdin-driven interaction.

The health audit must preserve:

- HEAD;
- current branch;
- index/staged contents;
- working-tree bytes;
- remotes and Git configuration.

No audit command may call mutating Git operations.

Working-tree changes are reportable facts, not an automatic failure by themselves. Existing ownership/migration contracts decide whether a specific changed path blocks an approved workflow.

## 14. Filesystem and Safety Boundary

All target paths must resolve from the explicit `--project PATH` authority root.

AUTO-0006 must preserve existing containment/link safety behavior of delegated modules. It must not follow an unsafe link merely to improve diagnostics.

Permission errors, unsupported types, containment failures, malformed metadata, and ambiguous identity are controlled errors/states, never reasons to broaden inspection.

## 15. CLI Contract

The installed command is:

```text
ai-engineering project health --project PATH
```

Output shall be deterministic `key=value` text suitable for humans and simple automation.

The output shall include at least:

```text
project=...
overall=healthy|action_required|manual_review|unsupported
identity=...
baseline=...
git=...
docs_ownership=...
docs_sync=...
migration=...
issue_count=N
issue=CODE:STATE:DETAIL
next_action=...
```

Exact additional keys may be added during implementation if deterministic and documented.

Exit codes:

- `0` — `healthy`;
- `1` — `action_required`, `manual_review`, `unsupported`, or controlled audit failure.

AUTO-0006 V1 intentionally avoids a multi-code severity protocol so shell integration remains simple and consistent with existing project commands.

No traceback shall be emitted for controlled project-state failures.

## 16. Determinism

For unchanged project bytes and Git metadata, repeated audits must produce the same semantic report.

Issue ordering shall be stable and independent of filesystem enumeration order.

Path rendering shall use normalized project-relative POSIX-style paths where paths are part of issue records.

The audit must not depend on wall-clock time, network state, random identifiers, or mutable global caches.

## 17. Compatibility

AUTO-0006 must preserve:

- generic SDK-0001/SDK-0001.1 project generation behavior;
- AUTO-0001/AUTO-0005 bootstrap behavior;
- AUTO-0002 documentation synchronization contracts;
- AUTO-0003 ownership initialization contracts;
- AUTO-0004 migration framework and safety invariants;
- AUTO-0005 V2 identity and production migration edge;
- SAFE-0001 and SAFE-0002 boundaries;
- existing CLI command behavior;
- published `v0.2.0` tag, release, and artifacts.

PyPI remains explicitly not approved/not published.

## 18. Verification Requirements

AUTO-0006 verification shall cover at least:

- exact healthy V2 project;
- V2 project needing safe ownership initialization;
- V2 project with deterministic documentation drift;
- documentation ownership manual-review state;
- supported V1 project with production migration available;
- V1 migration conflict/manual-review state;
- malformed V2 marker fail-closed;
- unsupported/arbitrary project fail-closed;
- deterministic issue ordering and repeated-report equality;
- no project-byte changes;
- Git HEAD/branch/index invariants;
- controlled CLI errors with no traceback;
- installed-wheel execution outside the source checkout.

CI must continue to pass Ruff, mypy, and the full pytest suite.

## 19. Planned Delivery Sequence

### AUTO-0006-01 — Design

Approve this read-only health/readiness contract.

### AUTO-0006-02 — Typed Health Aggregation

Implement the typed domain report and deterministic composition of existing read-only project workflows.

### AUTO-0006-03 — Read-only Git/Issue Readiness Coverage

Add only the narrowly required bounded Git observations and comprehensive healthy/action/manual-review/unsupported tests.

### AUTO-0006-04 — CLI

Add installed `ai-engineering project health --project PATH` with deterministic output and controlled exit behavior.

### AUTO-0006-05 — Installed Distribution Verification

Build and install the wheel in an isolated virtual environment and exercise representative health states using only the installed public CLI.

### AUTO-0006-06 — Final Evidence and Status Reconciliation

Record verification evidence and reconcile `CURRENT_STATUS.md`, `ROADMAP.md`, and `MASTER_INDEX.md`.

## 20. Acceptance Criteria

AUTO-0006 is complete only when:

1. the public audit is deterministic and read-only;
2. it positively distinguishes supported V1/V2 state without heuristic identity fallback;
3. it reports documentation ownership and synchronization readiness through existing contracts;
4. it reports explicit production migration readiness without applying migrations;
5. it preserves project bytes and Git invariants;
6. the installed wheel exposes the public health CLI outside the source checkout;
7. full CI is green;
8. final repository evidence and status documentation are reconciled.
