# AUTO-0004 — Engineering Project Update / Migration Verification Evidence

**Status:** COMPLETE / VERIFIED
**Milestone:** M3 — Engineering Automation
**Verified baseline:** `54355abf4b509e3fd72416a031152a6e7680dd13`

## 1. Scope

AUTO-0004 provides a bounded preserve-originals framework for deterministic updates and migrations of positively identified AI-Engineering projects.

The verified V1 implementation includes:

- positive project identity for the approved `python-engineering-v1` baseline;
- an explicit immutable migration registry and exact migration-id resolution;
- deterministic read-only migration planning;
- ownership and change-state classification;
- SHA-256 source guards and explicit manual-review blockers;
- guarded atomic apply for approved create/replace/delete operations;
- rollback and rollback verification after write or post-apply verification failure;
- Git HEAD/branch/index/remotes invariants;
- additive `ai-engineering project migrate check|plan|apply` CLI support;
- isolated installed-wheel verification.

The production `DEFAULT_MIGRATION_REGISTRY` intentionally remains empty. AUTO-0004 V1 establishes the framework and safety boundary without inventing or implicitly enabling a synthetic production migration edge.

## 2. Implemented Contract

The implementation verifies the following boundaries:

- project identity fails closed for arbitrary, unsupported, or altered machine-owned baseline evidence;
- human-authored project documentation may evolve without invalidating an otherwise supported project identity;
- migration contracts are explicit, named, profile-scoped, source-baseline-scoped, and deterministically ordered;
- planning is local-only and read-only;
- supported ownership classes are `machine_owned`, `human_owned`, `managed_section`, `generated_absent`, and `unknown`;
- supported change states include `unchanged_source`, `already_target`, `missing`, `locally_modified`, `unexpected_present`, `unsupported_type`, `outside_root`, and `manual_review`;
- automatic operations are limited to bounded declared create, machine-owned replace, and exact-source machine-owned delete operations;
- local modification, unexpected content, unsupported type, path escape, or ambiguous ownership blocks automatic apply;
- apply performs complete preflight before the first write and revalidates digest/absence guards;
- mid-apply failure rolls back prior writes;
- post-apply verification failure rolls back applied writes;
- rollback restoration is verified and rollback failure is a distinct fatal state;
- successful apply is idempotent and leaves no additional operations when the target state is already present;
- apply never stages, commits, resets, checks out, branches, tags, pushes, fetches, pulls, changes remotes, or edits `.git`;
- CLI apply delegates only to the guarded apply boundary;
- no package publication or release-state mutation is part of AUTO-0004.

## 3. Atomic Delivery Record

### AUTO-0004-01 — Design Contract

- PR #64 defined the project update/migration contract.
- PR Quality #97: SUCCESS.
- Post-merge Quality #98: SUCCESS.

### AUTO-0004-02 — Project Identity and Migration Registry

- PR #65 implemented positive project identity and the deterministic migration registry.
- Initial Quality #99 failed only on Ruff E501 formatting.
- The formatting defect was corrected without changing behavior.
- Quality #100: SUCCESS.
- Post-merge Quality #101: SUCCESS on merge commit `4342a45f6a576a9568c2178d3606f0dc9e185246`.

### AUTO-0004-03 — Deterministic Migration Planning

- PR #66 implemented ownership/change-state observations, deterministic operations, SHA-256 guards, and manual-review blocking.
- Quality #102: SUCCESS.
- Post-merge Quality #103: SUCCESS on merge commit `a9fe1c9ef853f50999c8651ffa31a708eefdb942`.

### AUTO-0004-04 — Guarded Atomic Apply and Rollback

- PR #67 implemented complete preflight, guarded writes, safe deletion, rollback, post-apply verification, idempotency, and Git invariants.
- Quality #104 failed only on Ruff E501 formatting and was corrected without logic changes.
- Quality #106 then passed Ruff and mypy but exposed a nondeterministic test-fixture `git commit` assumption before apply behavior executed.
- The fixture was corrected to create a deterministic baseline commit without weakening apply assertions.
- Quality #107: SUCCESS.
- Post-merge Quality #108: SUCCESS on merge commit `18e4eda0929da16bd4c15eb93568a88118296b31`.

### AUTO-0004-05 — CLI and Installed-Distribution Verification

- PR #68 added `project migrate check|plan|apply`, deterministic machine-readable output, exit-code behavior, unit verification, and isolated installed-wheel verification.
- The production default registry remains intentionally empty and therefore fails closed for unregistered migration ids.
- Quality #109: SUCCESS on head `43328eb89e5f731e1aecd22b4be79dac8276501c`.
- Post-merge Quality #110: SUCCESS on merge commit `54355abf4b509e3fd72416a031152a6e7680dd13`.

## 4. Verification Matrix

| Requirement | Evidence |
|---|---|
| Positive project identity | approved `python-engineering-v1` baseline detected from exact machine-owned/config evidence |
| Arbitrary repository | rejected / fail closed |
| Human documentation evolution | accepted without rewriting or guessing human content |
| Altered machine-owned evidence | rejected / fail closed |
| Exact migration registration | exact id/profile/source-baseline resolution only |
| Empty production registry | unregistered migration requests fail closed |
| Deterministic planning | stable observations and operation ordering |
| Read-only planning | project bytes remain unchanged during planning |
| SHA-256 guards | exact existing-source digest or absence expectation captured and revalidated |
| Local modification | automatic apply blocked |
| Unexpected target content | automatic apply blocked |
| Unsupported type / link escape | automatic apply blocked |
| Full-plan preflight | stale/manual-review state prevents writes before first mutation |
| Atomic replace/create/delete | verified through focused apply tests |
| Mid-apply failure | prior writes rolled back and restoration verified |
| Post-verification failure | applied writes rolled back |
| Idempotency | already-target state produces zero operations / zero changed paths |
| Git invariants | HEAD, branch, staged index, and remotes unchanged |
| CLI | installed `project migrate check|plan|apply` surface verified |
| Installed wheel | isolated virtual environment exercises migration CLI outside source checkout |
| Quality | final implementation passed Quality #109 and post-merge Quality #110 |

## 5. Distribution and Publication Boundary

AUTO-0004 extends the existing installed `ai-engineering` console script. The wheel is built from the repository, installed into an isolated virtual environment, and the migration command surface is exercised outside the source checkout.

The installed-distribution test confirms that `project migrate` is present and that an unregistered migration id fails closed under the intentionally empty production registry.

No version bump, Git tag, GitHub Release, TestPyPI, PyPI publication, publishing credential, or publishing automation is part of AUTO-0004.

## 6. Completion Statement

AUTO-0004 V1 is COMPLETE / VERIFIED for its approved framework scope.

The repository now has a bounded lifecycle sequence:

1. AUTO-0001 creates a verified engineering project;
2. AUTO-0003 initializes AUTO-0002 documentation ownership when safe;
3. AUTO-0002 synchronizes approved machine-owned documentation sections;
4. AUTO-0004 positively identifies supported project baselines and provides explicit deterministic migration planning plus guarded atomic apply for registered migration contracts.

AUTO-0004 does not mean that a production project migration is implicitly available. Concrete future source-to-target migration edges must be separately defined and registered; unsupported or ambiguous requests continue to fail closed.
