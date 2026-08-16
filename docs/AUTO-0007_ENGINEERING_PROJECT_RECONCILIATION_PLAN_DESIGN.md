# AUTO-0007 — Engineering Project Reconciliation Plan

**Status:** PROPOSED

## 1. Purpose

AUTO-0007 defines a deterministic, read-only reconciliation planner for supported AI-Engineering projects.

Its purpose is to answer a broader question than AUTO-0006 health:

> Which already-approved engineering workflows, in what order, would move this supported project from its current state toward `healthy`?

AUTO-0007 does not apply changes. It does not add new write authority. It only composes existing verified workflow contracts into an explicit ordered plan.

## 2. Scope

AUTO-0007 may compose only already-approved capabilities:

- AUTO-0004/AUTO-0005 explicit project migration planning;
- AUTO-0003 documentation ownership initialization planning;
- AUTO-0002 documentation synchronization planning;
- AUTO-0006 project health/readiness aggregation;
- bounded read-only Git observations already used by AUTO-0006.

AUTO-0007 must not introduce a new migration edge, bootstrap profile, generated workflow, dependency upgrade policy, arbitrary command execution, release publication, TestPyPI, or PyPI behavior.

## 3. Core Contract

The public API returns an immutable reconciliation plan with:

- resolved project root;
- current AUTO-0006 health report;
- stable plan state;
- ordered reconciliation steps;
- deterministic blockers/manual-review issues;
- final expected state if all returned steps are successfully completed under their own existing contracts.

The planner itself remains read-only.

## 4. Plan States

Stable plan states are:

- `clean` — project is already healthy and no steps are required;
- `ready` — one or more approved workflows can be planned in deterministic order;
- `manual_review` — reconciliation cannot be safely planned without human review;
- `unsupported` — project identity or required inspection is unsupported.

Precedence is:

`unsupported > manual_review > ready > clean`

## 5. Allowed Step Types

AUTO-0007 may return only these step types:

1. `project migrate plan --migration python-engineering-v1-to-v2`
2. `project docs ownership plan`
3. `project docs plan`

No generic `upgrade latest`, no arbitrary shell command, and no implicit apply command is permitted.

## 6. Deterministic Ordering

For supported V1 projects:

1. evaluate the registered `python-engineering-v1-to-v2` edge first;
2. if migration planning is ready, migration is the first reconciliation step;
3. documentation ownership/synchronization steps that depend on the post-migration state are represented only when they can be determined safely from current approved contracts; otherwise the plan stops after migration with an explicit `reinspect_after_step=true` boundary.

For exact V2 projects:

1. documentation ownership initialization precedes documentation synchronization;
2. synchronization is included only when ownership is already initialized and drift can be safely planned from the current state;
3. if ownership initialization is required, later synchronization is represented as a reinspection boundary rather than guessed from hypothetical bytes.

This preserves fail-closed behavior and avoids speculative multi-step mutation simulation.

## 7. Step Model

Each reconciliation step is immutable and includes:

- `sequence`: 1-based deterministic order;
- `workflow`: exact approved workflow identifier;
- `state`: `ready` or `reinspect_required`;
- `reason`: stable bounded explanation;
- optional `migration_id`;
- optional affected document/path identifiers derived from existing plans;
- `reinspect_after_step`: boolean.

A `reinspect_required` boundary is not an executable workflow. It states that the project must be inspected again after the preceding approved workflow before additional work can be safely planned.

## 8. Relationship to AUTO-0006

AUTO-0006 remains the authoritative current-state health/readiness audit.

AUTO-0007 must call or reuse AUTO-0006 rather than redefine its overall-state policy.

AUTO-0006 answers:

> What is the current state and what single approved workflow should be considered next?

AUTO-0007 answers:

> What deterministic sequence can be safely planned now, and where must reinspection occur before further planning?

AUTO-0007 must never contradict AUTO-0006's current next-action recommendation for the first actionable step.

## 9. Read-Only and Git Invariants

Planning must preserve:

- project file bytes;
- Git HEAD;
- current branch;
- staged index;
- unstaged working-tree state;
- untracked files;
- remotes;
- local Git configuration.

AUTO-0007 may use only bounded read-only subprocess operations already approved for project inspection/readiness. It must use `shell=False`, capture output, and must not invoke hooks, project code, tests, builds, package managers, network publication, or dependency resolution.

## 10. Unsupported and Manual Review Behavior

Malformed or unapproved `.ai-engineering.toml` identity must fail closed and must not fall back to V1.

Partial/duplicate/malformed documentation ownership markers, unsupported file types/links, migration conflicts, containment failures, or other existing manual-review conditions must remain manual review.

AUTO-0007 must not downgrade an AUTO-0006 `unsupported` or `manual_review` result into a ready plan.

## 11. CLI Contract

Planned public command:

```text
ai-engineering project reconcile plan --project PATH
```

Output is deterministic `key=value` text.

Required top-level fields:

- `project=`
- `state=`
- `current_overall=`
- `step_count=`
- ordered `step=` records;
- `reinspect_required=`
- `issue_count=`
- ordered `issue=` records;
- `expected_state=`

Exit codes:

- `0` for `clean` or `ready`;
- `1` for `manual_review`, `unsupported`, or controlled planning failure.

Controlled failures must not emit a traceback.

## 12. Expected-State Semantics

`expected_state` is deliberately bounded:

- `healthy` only when the current project is already healthy;
- `reinspect_required` when one or more approved workflows must run before later readiness can be known safely;
- `manual_review` when blocked;
- `unsupported` when unsupported.

AUTO-0007 must not claim that an unapplied multi-step plan will definitely result in `healthy` without reinspection.

## 13. Verification Matrix

Verification must include at minimum:

- healthy V2 project => `clean`, zero steps;
- V2 with ownership initialization available => first step `project docs ownership plan`, reinspection boundary;
- V2 with initialized ownership and docs drift => first step `project docs plan`;
- V1 with registered production migration => first step exact V1-to-V2 migration plan, reinspection boundary;
- V1/V2 manual-review condition => `manual_review`, zero unsafe steps;
- malformed identity marker => `unsupported`, no V1 fallback;
- deterministic repeated plan equality;
- deterministic step/issue ordering;
- target project bytes unchanged;
- Git HEAD/branch/index/status/remotes invariants;
- controlled CLI output and exit codes;
- installed-wheel isolated-environment verification.

## 14. Delivery Sequence

AUTO-0007 should be delivered in bounded stages:

1. **AUTO-0007-01 — Design**
2. **AUTO-0007-02 — Typed Read-Only Reconciliation Planner**
3. **AUTO-0007-03 — Manual Review / Determinism / Git Invariant Coverage**
4. **AUTO-0007-04 — Public CLI**
5. **AUTO-0007-05 — Installed Distribution Verification**
6. **AUTO-0007-06 — Final Evidence / Status Reconciliation**

Each implementation stage requires the normal Quality gate before merge.

## 15. Compatibility and Publication Boundaries

AUTO-0007 must preserve all verified AUTO-0001 through AUTO-0006 contracts and SAFE-0001/SAFE-0002 boundaries.

The immutable published `v0.2.0` release remains unchanged. AUTO-0007 does not authorize a version bump, tag, GitHub Release, TestPyPI, or PyPI publication.
