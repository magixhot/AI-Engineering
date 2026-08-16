# AUTO-0005 — Python Engineering Baseline V2 and First Production Migration Edge

**Status:** DESIGN / PROPOSED
**Milestone:** M3 — Engineering Automation
**Scope:** define the first explicit `python-engineering-v2` baseline and register the first production AUTO-0004 migration edge from `python-engineering-v1`

## 1. Purpose

AUTO-0005 turns the verified AUTO-0004 migration framework into a useful production capability by defining one real successor baseline and one exact migration edge.

The milestone follows the project rule: **documentation before implementation**.

AUTO-0005 does not create a synthetic version merely to exercise migration machinery. V2 exists to solve two concrete baseline weaknesses:

1. `python-engineering-v1` has no explicit machine-readable project/profile/baseline identity marker and therefore must be recognized indirectly from scaffold evidence;
2. the V1 `.gitignore` omits cache directories produced by the baseline quality tools themselves (`pytest`, `mypy`, and Ruff).

V2 addresses only those bounded issues.

## 2. Relationship to Existing Contracts

AUTO-0005 must preserve these established authorities:

- SDK-0001 remains authoritative for the generic document-first template.
- SDK-0001.1 remains authoritative for the generic optional Python scaffold and its existing default behavior.
- AUTO-0001 remains authoritative for the `python-engineering` bootstrap workflow.
- AUTO-0002 and AUTO-0003 remain authoritative for their exact documentation ownership/synchronization boundaries.
- AUTO-0004 remains authoritative for project identity, migration registry, deterministic planning, preserve-originals behavior, guarded apply/rollback, Git invariants, and migration CLI semantics.
- SAFE-0001 and SAFE-0002 remain unchanged MCP authorization/execution boundaries.
- REL-0003 and published `v0.2.0` evidence remain immutable.

AUTO-0005 may extend the AUTO-0001 profile and AUTO-0004 registry, but must not weaken or reinterpret those contracts.

## 3. Approved Baseline Identifiers

The baseline identifiers are:

```text
source: python-engineering-v1
target: python-engineering-v2
migration id: python-engineering-v1-to-v2
profile: python-engineering
```

There is no alias such as `latest`, no automatic chain selection, and no implicit upgrade request.

## 4. V2 File-Level Delta

`python-engineering-v2` is intentionally a small evolution of V1.

Exactly two machine-owned baseline changes are approved.

### 4.1 Explicit identity marker

V2 adds one root-level file:

```text
.ai-engineering.toml
```

Exact V2 content:

```toml
schema = 1
profile = "python-engineering"
baseline = "python-engineering-v2"
```

The marker is fully machine-owned.

The root-level form is deliberate: AUTO-0004 V1 already supports guarded `create_file` operations for a file whose parent exists. AUTO-0005 must not expand migration semantics merely to create an identity subdirectory.

The marker contains no project name, package name, path, machine identifier, release version, credential, timestamp, or mutable runtime state.

### 4.2 Quality-tool cache ignores

V2 replaces the exact V1 machine-owned `.gitignore` with the same existing content plus these three relative entries:

```text
.pytest_cache/
.mypy_cache/
.ruff_cache/
```

The existing V1 entries remain unchanged and in their existing order. The three new cache entries are appended after the existing build-artifact entries and before editor-local entries.

No absolute path, OneDrive path, user path, platform-specific path, or generated environment path is permitted.

## 5. Explicit Non-Changes

V2 does **not** change:

- the nine SDK-0001 project documents;
- `pyproject.toml` project metadata, project version, dependencies, or tool configuration;
- `src/<package>/__init__.py`;
- `tests/test_smoke.py`;
- default branch `main`;
- package-name derivation;
- Git remote behavior;
- dependency installation behavior;
- project code generation;
- AUTO-0002/AUTO-0003 ownership markers;
- release/version/publication state.

In particular, generated project `version = "0.1.0"` is not the engineering baseline identifier and remains unchanged.

## 6. Why CI Workflow Generation Is Not Part of V2

A generated GitHub Actions workflow is not included in this baseline.

Adding `.github/workflows/...` would require nested-directory creation semantics that AUTO-0004 V1 does not currently implement. Expanding migration operation types merely to make the first production edge larger would violate the bounded-change goal.

CI-template evolution may be designed separately after the first production migration proves the existing framework against a real baseline.

## 7. V2 Bootstrap Contract

New `python-engineering` bootstraps must produce V2 once AUTO-0005 is complete.

The resulting project must contain the complete existing V1 file set plus `.ai-engineering.toml`, with the V2 `.gitignore` bytes.

All generated V2 files must be included in the same initial Git commit created for the bootstrap project.

AUTO-0005 must not implement V2 by creating a second bootstrap commit, silently amending history after a completed generic generation call, or leaving generated V2 files uncommitted.

Implementation may add a bounded pre-commit profile augmentation seam to the template-generation internals, provided that:

- it is used only by the approved `python-engineering` bootstrap path;
- ordinary SDK-0001 / SDK-0001.1 callers preserve their existing outputs and behavior;
- generic `ai-engineering project create --python-scaffold` does not receive the `python-engineering` identity marker;
- the complete generated-file set is validated before the initial commit;
- nested-Git and destination safety remain unchanged.

## 8. Generic SDK Compatibility Boundary

AUTO-0005 must not relabel every SDK Python scaffold as a managed engineering project.

The following behavior is required:

- generic SDK-0001 document-only generation remains unchanged;
- generic SDK-0001.1 Python scaffold generation remains unchanged;
- `project create --python-scaffold` remains generic and must not emit `.ai-engineering.toml`;
- only AUTO-0001 `project bootstrap --profile python-engineering` gains V2 profile assets.

This distinction is required because positive AUTO-0004 project identity must reflect explicit management authority, not merely similarity to a generic Python scaffold.

## 9. Project Identity Contract

AUTO-0004 identity detection must support both V1 and V2 during the migration era.

### V1

V1 continues to use the existing positively verified legacy evidence and exact V1 `.gitignore` contract.

A malformed, contradictory, or unsupported `.ai-engineering.toml` must **not** be ignored in order to fall back to V1.

### V2

V2 identity requires:

- exact `.ai-engineering.toml` content for schema/profile/baseline;
- exact V2 `.gitignore` bytes;
- the existing supported Python scaffold structure and metadata invariants;
- required project documents;
- project-root containment and regular-file checks.

If the marker claims V2 but required V2 evidence is missing or contradictory, identity detection fails closed.

## 10. First Production Migration Contract

`python-engineering-v1-to-v2` is the first production entry in `DEFAULT_MIGRATION_REGISTRY`.

The migration contains exactly two path rules:

1. create `.ai-engineering.toml` only when absent;
2. replace `.gitignore` only when its bytes exactly match the approved V1 source bytes.

Both paths are machine-owned.

No documentation file, source file, test file, or `pyproject.toml` mutation is part of this edge.

## 11. Preserve-Originals and Conflict Rules

The existing AUTO-0004 fail-closed rules remain mandatory.

The migration must require manual review / no writes when:

- `.ai-engineering.toml` already exists with content other than the exact V2 target bytes;
- `.gitignore` differs from both exact V1 and exact V2 bytes;
- either path has an unsupported type or link state;
- project identity is ambiguous or unsupported;
- path containment cannot be proven;
- any digest/preflight guard becomes stale before apply.

If `.ai-engineering.toml` already has exact V2 bytes and `.gitignore` is exact V2, planning must be idempotent and report no migration writes / already-target state.

## 12. Apply and Git Boundary

AUTO-0005 uses the existing AUTO-0004 guarded apply implementation.

Migration apply must:

- preflight the complete plan before the first write;
- preserve SHA-256 stale-plan guards;
- stage replacement material safely;
- roll back prior migration writes if a later write fails;
- verify exact V2 target state;
- preserve Git HEAD, current branch, index/staging, and remotes;
- leave approved working-tree migration changes visible for human review.

The migration itself must not `git add`, commit, amend, checkout, reset, push, pull, fetch, create tags, or change remotes.

The V2 **bootstrap** path is separate: it remains governed by AUTO-0001 creation semantics and must place its generated V2 assets in the bootstrap initial commit.

## 13. Execution and Network Boundary

AUTO-0005 migration inspection/planning/apply remains local-only.

It must not:

- execute project code;
- run project tests as part of migration mutation;
- install dependencies;
- run package managers;
- execute arbitrary shell commands;
- access credentials;
- contact network services;
- publish packages or releases.

Installed-distribution verification may invoke the AI-Engineering CLI and local Git in isolated test projects exactly as established by prior release tests.

## 14. CLI Contract

AUTO-0005 does not add a new CLI surface.

The existing AUTO-0004 commands are used with the production migration id:

```text
ai-engineering project migrate check --project PATH --migration python-engineering-v1-to-v2
ai-engineering project migrate plan --project PATH --migration python-engineering-v1-to-v2
ai-engineering project migrate apply --project PATH --migration python-engineering-v1-to-v2
```

Existing controlled error and exit-code behavior remains unchanged.

## 15. Verification Matrix

Implementation must verify at least:

| Requirement | Evidence |
|---|---|
| Generic document template compatibility | unchanged SDK-0001 output |
| Generic Python scaffold compatibility | unchanged SDK-0001.1 output and no engineering marker |
| New bootstrap baseline | AUTO-0001 bootstrap creates V2 marker and V2 `.gitignore` |
| Single bootstrap initial commit | every generated V2 file is included in the initial commit |
| V1 identity | legacy supported project remains recognized as V1 |
| V2 identity | exact marker + target scaffold recognized as V2 |
| Contradictory marker | fail closed, never silently treated as V1 |
| Production registry | exact `python-engineering-v1-to-v2` edge is registered |
| Migration dry run | planning performs no writes |
| Marker creation | absent marker is safely planned/created |
| `.gitignore` replacement | only exact V1 bytes are replaceable |
| Locally modified `.gitignore` | manual review / no writes |
| Unexpected marker content | manual review / no writes |
| Stale plan | digest mismatch blocks all writes |
| Rollback | mid-apply failure restores prior project bytes |
| Target verification | exact V2 identity proven after apply |
| Idempotency | second plan/apply produces no changes |
| Git invariants | migration preserves HEAD/branch/index/remotes |
| Installed CLI | installed wheel migrates a real V1 bootstrap fixture to V2 |
| No publication | no version bump, tag, release, TestPyPI, or PyPI action |
| Regression | repository Ruff, mypy, pytest, and distribution verification remain green |

## 16. Proposed Atomic Implementation Sequence

### AUTO-0005-02 — V2 Baseline Assets and Bootstrap Generation

Add the exact marker/V2 `.gitignore` asset contract and make new `python-engineering` bootstrap output V2 in a single initial commit while preserving generic SDK outputs.

No migration registry mutation in this task.

### AUTO-0005-03 — Dual V1/V2 Identity and Production Registry Edge

Extend positive identity detection to V2, preserve V1 legacy detection, reject contradictory markers, and register exact `python-engineering-v1-to-v2` in `DEFAULT_MIGRATION_REGISTRY`.

Planning remains delegated to existing AUTO-0004 machinery.

### AUTO-0005-04 — Production Migration Apply Verification

Verify real V1 -> V2 planning/apply, conflicts, stale-plan protection, rollback, target identity, idempotency, and Git invariants using the registered production edge.

No new mutation operation type is introduced.

### AUTO-0005-05 — Installed-Distribution End-to-End Verification

Build/install the wheel in isolation and verify:

- new installed bootstrap produces V2;
- a V1 fixture is migrated through installed `project migrate check|plan|apply`;
- repeated migration is clean/idempotent;
- generic installed `project create --python-scaffold` remains generic.

### AUTO-0005-06 — Final Evidence and Status Reconciliation

Record exact quality/evidence results and reconcile project status/index/roadmap.

## 17. Non-Goals

AUTO-0005 explicitly excludes:

- changing generated project PEP 621 version;
- dependency upgrades;
- Python-version upgrades;
- generated GitHub Actions workflows;
- new bootstrap profiles;
- arbitrary `pyproject.toml` rewrites;
- migration of human-owned documentation;
- new AUTO-0004 operation types;
- heuristic/fuzzy conflict resolution;
- Git staging or commit during migration;
- remote repository creation;
- publication automation;
- version bump/tag/GitHub Release/TestPyPI/PyPI publication;
- changes to SAFE-0001 or SAFE-0002 boundaries.

## 18. Completion Criteria

AUTO-0005 is complete only when:

- this V2 contract is approved and merged;
- new `python-engineering` bootstraps produce exact V2 assets in one initial commit;
- generic SDK project/scaffold behavior remains compatible;
- V1 and V2 identity are both deterministic and fail closed;
- contradictory markers cannot downgrade to V1 detection;
- `python-engineering-v1-to-v2` is the first explicit production migration registry edge;
- migration touches only the two approved machine-owned paths;
- local modifications and unexpected content require manual review;
- existing AUTO-0004 preflight, rollback, idempotency, and Git invariants remain verified;
- installed-wheel end-to-end migration succeeds outside the source checkout;
- repository-wide quality gates remain green;
- final verification evidence is recorded;
- no release or PyPI action occurs.
