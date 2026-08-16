# AUTO-0004 — Engineering Project Update / Migration Design

**Status:** DESIGN / PROPOSED
**Milestone:** M3 — Engineering Automation
**Scope:** deterministic, preserve-originals migration of an existing AI-Engineering project baseline to a newer approved project contract

## 1. Purpose

AUTO-0004 defines a bounded update/migration framework for existing engineering projects that were created or bootstrapped by an earlier approved AI-Engineering project contract.

The framework exists to evolve an existing project without treating it as a fresh scaffold and without silently replacing human-owned files.

AUTO-0004 is not a general repository rewrite engine. It is an explicit inspect -> plan -> review -> guarded apply -> verify workflow for narrowly approved migrations.

The design follows the project rule: **documentation before implementation**.

## 2. Relationship to Existing Contracts

AUTO-0004 must preserve these established authorities:

- SDK-0001 remains authoritative for project-template structure and template-owned assets.
- AUTO-0001 remains authoritative for initial `python-engineering` bootstrap.
- AUTO-0002 remains authoritative for documentation synchronization inside its exact three-document writable set.
- AUTO-0003 remains authoritative for AUTO-0002 ownership-marker initialization.
- SAFE-0001 and SAFE-0002 remain unchanged MCP authorization/execution boundaries.
- REL-0003 remains immutable release evidence for published `v0.2.0`.

AUTO-0004 may compose existing public APIs where appropriate, but must not duplicate or weaken their contracts.

## 3. Objective

Provide a deterministic workflow that can:

1. identify the current supported project baseline;
2. identify a requested target migration contract;
3. inspect only approved local project state;
4. produce an explicit dry-run migration plan;
5. classify every candidate path by ownership and conflict state;
6. preserve all human-authored content unless an approved rule proves a replacement safe;
7. reject ambiguous or unsupported changes for manual review;
8. apply only a previously planned, digest-guarded update set;
9. roll back if an all-or-nothing write set cannot be completed;
10. verify the target baseline after apply;
11. leave Git HEAD, index, branch, and remotes unchanged.

V1 is local-only and requires no network access.

## 4. V1 Supported Project Identity

AUTO-0004 V1 supports only projects that can be positively identified as an approved AI-Engineering project baseline.

A project must expose deterministic identity evidence sufficient to establish:

- project root;
- project profile, initially `python-engineering` only;
- source baseline identifier;
- target migration identifier;
- package/project name where required by the migration;
- ownership metadata needed to distinguish machine-owned and human-owned paths.

If project identity is missing, ambiguous, contradictory, or unsupported, planning must fail closed.

AUTO-0004 must never guess that an arbitrary Python repository is an AI-Engineering-managed project.

## 5. Migration Registry

Migrations must be explicit, named, and registered.

Each migration contract must define at minimum:

- migration id;
- supported source baseline(s);
- exact target baseline;
- supported profile(s);
- ordered operation set;
- ownership expectations for every touched path;
- verification rules;
- whether the migration is reversible by AUTO-0004 rollback during the same apply transaction.

There is no generic "upgrade to latest" mutation in V1. A caller must resolve to one exact approved migration contract.

## 6. Ownership Model

Every path considered by a migration must be classified before planning mutation.

Required V1 ownership classes:

- `machine_owned` — content is fully controlled by an approved baseline and may be replaced only under the migration rule;
- `human_owned` — content must not be rewritten automatically;
- `managed_section` — only an established bounded machine-owned section may be changed through its existing authority;
- `generated_absent` — an approved generated path is missing and may be added if the migration rule allows it;
- `unknown` — ownership cannot be proven and therefore requires manual review.

Ownership must be established from explicit project/migration contract evidence, not filename intuition alone.

## 7. Change-State Model

For each candidate path, planning must classify the observed state relative to the expected source baseline.

Required V1 states:

- `unchanged_source` — exact expected source bytes are present;
- `already_target` — exact target bytes are already present;
- `missing` — source path is absent;
- `locally_modified` — source baseline path exists but differs from expected source bytes;
- `unexpected_present` — target add-path already exists with unrecognized content;
- `unsupported_type` — expected file/directory shape is not present;
- `outside_root` — resolved path escapes the requested project root;
- `manual_review` — any other state where preservation cannot be proven.

Automatic replacement of `locally_modified`, `unexpected_present`, `unknown`, `unsupported_type`, or `outside_root` paths is forbidden in V1.

## 8. Preserve-Originals Contract

The central AUTO-0004 rule is:

**Human-owned or ambiguously owned content is never silently overwritten, deleted, moved, or normalized.**

Automatic changes are permitted only when the migration contract can prove one of the following:

- the exact source bytes are still present and the path is machine-owned;
- an approved generated path is absent and may be created;
- an existing established managed-section authority performs the bounded update;
- the path is already at the exact target state, in which case the operation is a no-op.

V1 does not perform heuristic three-way merges, fuzzy patches, semantic LLM rewrites, or conflict auto-resolution.

## 9. Read-Only Inspection and Planning

Planning must be a pure local inspection step with no project mutation.

Proposed public boundary:

```python
@dataclass(frozen=True)
class ProjectMigrationRequest:
    project_root: Path
    migration_id: str


@dataclass(frozen=True)
class ProjectMigrationOperation:
    path: str
    action: str
    ownership: str
    original_sha256: str | None
    replacement_content: bytes | None


@dataclass(frozen=True)
class ProjectMigrationPlan:
    project_root: Path
    migration_id: str
    source_baseline: str
    target_baseline: str
    operations: tuple[ProjectMigrationOperation, ...]
    manual_review: tuple[str, ...]
```

Exact type names may be refined, but the public contract must remain typed, deterministic, explicit, and read-only.

## 10. Planning Contract

Planning must:

- validate project root containment;
- positively identify the supported source baseline;
- resolve one exact migration id;
- inspect only migration-declared paths plus approved identity metadata;
- compute SHA-256 guards from exact original bytes where a write/delete depends on current content;
- produce a deterministic ordered operation list;
- separate automatic operations from manual-review blockers;
- expose complete replacement content for planned file writes;
- perform no filesystem mutation.

Identical project bytes and identical request inputs must produce an identical ordered plan.

## 11. Operation Types

V1 may support only explicitly required operation kinds:

- `create_file`;
- `replace_machine_owned_file`;
- `delete_machine_owned_file` only when the source bytes exactly match the approved source baseline;
- `create_directory` where required structurally;
- delegated bounded managed-section update through an existing authority.

Renames, arbitrary directory deletion, permission changes, symlink creation, executable-bit changes, and binary patching are excluded unless separately designed.

## 12. Manual-Review Boundary

AUTO-0004 must fail closed when any of the following applies:

- unsupported or ambiguous source baseline;
- unsupported migration id or migration path;
- local modification of a path the migration would replace/delete;
- target add-path already contains unrecognized content;
- unknown ownership;
- symlink/reparse-point behavior makes containment or preservation uncertain;
- path escapes the project root after resolution;
- required source path has an unsupported type;
- digest guard cannot be established;
- a delegated AUTO-0002/AUTO-0003 action reports manual review;
- target verification cannot be proven deterministically;
- any other condition makes preserve-originals guarantees uncertain.

If any required operation is blocked, V1 apply must perform no migration writes.

## 13. Apply Contract

Recommended public boundary:

```python
apply_project_migration(plan: ProjectMigrationPlan) -> ProjectMigrationResult
```

Before the first write, apply must revalidate the complete plan:

- project identity still matches;
- all guarded original digests still match;
- manual-review set is empty;
- all target paths still satisfy containment and expected type constraints;
- Git invariants required by the plan still hold where observed.

V1 apply is all-or-nothing for the migration operation set.

## 14. Atomic Write and Rollback Contract

AUTO-0004 must stage replacement material outside target paths before mutation.

During apply:

- no operation begins until every preflight guard passes;
- original bytes required for rollback must be retained for the transaction;
- if a later write fails, earlier writes from the same migration transaction must be restored;
- rollback failure is a distinct fatal verification state and must be surfaced explicitly;
- successful apply must leave no temporary migration files inside the project.

The implementation may choose a bounded transaction directory under the project or a safe external temporary location, but the path policy must be explicit and tested on Windows and Linux.

## 15. Deletion Safety

Automatic deletion is stricter than replacement.

A file may be deleted only when:

- the migration contract explicitly declares the path obsolete;
- ownership is `machine_owned`;
- exact current bytes match the approved expected source bytes;
- the path resolves inside the project root;
- deletion is included in the all-or-nothing plan and rollback set.

Directories are not recursively deleted in V1 merely because they become empty.

## 16. Documentation Handoff

AUTO-0004 must not duplicate AUTO-0002 or AUTO-0003 documentation logic.

If a migration changes project structure that affects managed documentation:

- AUTO-0004 may invoke AUTO-0003 only when marker initialization is explicitly required and eligible;
- AUTO-0004 may invoke AUTO-0002 planning/apply only through its public bounded authority;
- any manual-review result from those systems blocks the migration transaction before writes unless the migration is explicitly partitioned by a later design;
- post-migration verification must confirm AUTO-0002 ownership remains valid.

## 17. Git Boundary

AUTO-0004 never stages or commits automatically.

It must not:

- `git add`;
- commit;
- reset;
- checkout;
- switch branches;
- create branches or tags;
- push/fetch/pull;
- change remotes;
- modify `.git` metadata.

Automated verification must prove Git HEAD, current branch, index/staging, and configured remotes are unchanged by planning and successful apply.

Working-tree changes caused by approved migration writes are expected and must remain visible for human review.

## 18. Execution and Network Boundary

AUTO-0004 V1 does not execute project code during inspection, planning, or apply.

It must not:

- run project tests as part of mutation;
- import project modules for discovery;
- execute arbitrary shell commands;
- install dependencies;
- run package managers;
- access credentials;
- contact remote services;
- publish packages or releases.

Target verification must be structural/content-based unless a later approved task explicitly adds an execution stage with a separate safety contract.

## 19. Error Model

AUTO-0004 should expose bounded domain failures for at least:

- invalid project root;
- unsupported project identity;
- unsupported source baseline;
- unsupported migration;
- migration path gap;
- unknown ownership;
- local modification conflict;
- unexpected target content;
- path escape;
- unsupported file type/link state;
- stale plan / digest mismatch;
- write failure;
- rollback failure;
- verification failure;
- manual review required;
- unknown internal failure.

Expected domain failures must be controlled and testable.

## 20. Idempotency

AUTO-0004 must be idempotent for a completed migration.

After successful apply:

- re-planning the same migration must report the project as already at target or produce zero writes;
- no duplicate generated content may appear;
- AUTO-0002/AUTO-0003 ownership structures must remain valid;
- the project identity must resolve to the target baseline.

## 21. Migration Chain Rules

V1 migration execution is one explicit edge at a time.

If a project requires multiple migrations, the caller must apply an approved ordered chain such as:

```text
baseline-A -> baseline-B -> baseline-C
```

The framework may provide read-only chain resolution later, but V1 must not silently skip intermediate migration contracts or synthesize an unregistered composite migration.

## 22. CLI Direction

A later task may expose an additive CLI such as:

```text
ai-engineering project migrate check --project PATH --migration MIGRATION_ID
ai-engineering project migrate plan --project PATH --migration MIGRATION_ID
ai-engineering project migrate apply --project PATH --migration MIGRATION_ID
```

Exact syntax is not approved by AUTO-0004-01 alone.

Any CLI must remain an adapter over the public API and must not duplicate ownership, conflict, planning, or apply logic.

## 23. Automated Verification Matrix

Implementation must provide evidence for at least:

| Row | Required evidence |
|---|---|
| Supported identity | approved source project is recognized deterministically |
| Arbitrary repository | unsupported project fails closed |
| Exact migration id | only registered source->target migration is accepted |
| Dry-run planning | plan produces no writes |
| Deterministic plan | identical bytes produce identical ordered operations |
| Machine-owned unchanged file | safe replacement is planned |
| Human-owned file | never overwritten |
| Locally modified machine path | manual review / no writes |
| Unexpected target add-path | manual review / no writes |
| Missing approved generated path | safe create when migration permits |
| Safe deletion | only exact machine-owned source bytes may be deleted |
| Project-root containment | traversal/absolute/link escape rejected |
| Digest guard | stale target invalidates complete plan before writes |
| Multi-file atomicity | one blocked/stale path prevents all writes |
| Mid-apply failure | prior writes roll back |
| Rollback verification | restored bytes match originals |
| Idempotency | second run produces zero writes/already-target |
| AUTO-0002 handoff | documentation synchronization remains valid |
| AUTO-0003 handoff | ownership initialization semantics remain valid |
| Git invariants | HEAD/branch/index/remotes unchanged |
| No execution/network | no project-code/subprocess/package-manager/network behavior |
| Linux portability | full CI coverage |
| Windows portability | local/CI evidence for filesystem semantics as required |
| Existing regression suite | SDK/AUTO/SAFE/MCP/release tests remain green |

Repository-wide pytest, Ruff, mypy, distribution verification, and `git diff --check` must remain green.

## 24. Non-Goals

AUTO-0004 V1 explicitly excludes:

- arbitrary repository modernization;
- heuristic project detection;
- LLM-authored conflict resolution;
- three-way merges of locally modified files;
- rewriting human-owned source code;
- dependency upgrades merely because newer versions exist;
- package-manager execution;
- code-formatting or whole-repository normalization;
- Git staging/commit/branch/push automation;
- remote template downloads;
- GitHub/PyPI publication;
- OS-level sandboxing;
- migration of unsupported profiles;
- direct migration across unregistered baseline gaps;
- changing SAFE-0001/SAFE-0002 authority boundaries.

## 25. Proposed Atomic Implementation Sequence

### AUTO-0004-02 — Project Identity and Migration Registry

Implement typed project identity detection and an explicit migration registry. Read-only only; no mutation or CLI.

### AUTO-0004-03 — Deterministic Migration Planning

Implement ownership/change-state classification, operation planning, SHA-256 guards, conflict/manual-review behavior, and tests. Still no writes.

### AUTO-0004-04 — Guarded Atomic Apply and Rollback

Implement full-plan preflight, staged writes, safe deletion rules, rollback, post-apply structural verification, idempotency, and Git invariants. No CLI yet.

### AUTO-0004-05 — CLI and Installed-Distribution Verification

Freeze the exact CLI contract, expose check/plan/apply through the installed console script, and extend isolated-wheel verification.

Each task must remain atomic and stop if preserve-originals, rollback, portability, or compatibility guarantees cannot be proven.

## 26. Completion Criteria

AUTO-0004 is complete only when:

- this design is approved;
- project identity is explicit and fail-closed;
- migrations are registered exact source->target contracts;
- planning is deterministic and read-only;
- human/unknown/local-modification conflicts are never silently overwritten;
- every mutation is digest guarded;
- apply is all-or-nothing with verified rollback on failure;
- safe deletion follows the stricter deletion contract;
- repeated execution is idempotent;
- AUTO-0002/AUTO-0003 compatibility is verified;
- Git metadata/index invariants are verified;
- no project code, package manager, arbitrary shell, or network execution is introduced;
- Linux and Windows evidence satisfy the approved portability contract;
- installed-distribution behavior is verified when CLI scope lands;
- repository-wide quality gates remain green;
- final verification evidence and status reconciliation are committed separately.

Until those criteria are met, AUTO-0004 must not be described as implemented or verified.
