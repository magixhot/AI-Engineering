# AUTO-0002 — Verification Evidence

**Status:** COMPLETE / VERIFIED

## Verified Contract Surface

AUTO-0002 V1 consists of four bounded layers:

1. read-only project inspection;
2. deterministic documentation drift detection and synchronization planning;
3. SHA-256 guarded apply with ownership preservation and post-apply verification;
4. installed CLI adaptation for `project docs check`, `plan`, and `apply`.

The V1 writable set remains exactly:

- `CURRENT_STATUS.md`
- `MASTER_INDEX.md`
- `PROJECT_MAP.md`

## CLI Contract

The installed console script exposes:

```text
ai-engineering project docs check --project PATH
ai-engineering project docs plan --project PATH
ai-engineering project docs apply --project PATH
```

`check` and `plan` are read-only. `apply` refuses mutation when any managed document requires manual
review and otherwise delegates mutation to the public guarded apply API.

Projects without valid AUTO-0002 ownership markers are not initialized or rewritten automatically.
They remain manual-review cases.

## Safety Evidence

Automated tests cover:

- deterministic inspection, drift detection, and planning;
- portable relative paths and no machine-specific generated paths;
- missing/stale map and index entries;
- bounded current-status facts;
- missing/malformed ownership markers as manual review;
- read-only check/plan behavior;
- stable plan output and original SHA-256 guards;
- stale-plan failure before writes;
- exact V1 target enforcement;
- human-owned prefix/suffix preservation;
- post-write exact-content verification;
- post-apply drift clearing;
- no Git staging, commit, push, or HEAD mutation by AUTO-0002;
- CLI manual-review refusal and clean no-op behavior;
- installed-wheel CLI discovery and isolated check/plan/apply behavior.

## Distribution Evidence

The REL-0001 isolated-wheel test builds the distribution outside the installed environment, installs
the wheel into a fresh external virtual environment, clears source-tree Python environment overrides,
and executes the installed console script outside the checkout.

AUTO-0002-04 extends that evidence to prove installed `project docs` command discovery, manual-review
behavior on an unmarked bootstrap project, deterministic planning on a marked fixture, guarded apply,
subsequent clean check, and unchanged Git HEAD/staging semantics.

## GitHub Actions Evidence

Implementation PR #46 completed the Quality workflow successfully on Linux/Python 3.11:

- pytest: **142 passed**;
- Ruff: **0 findings**;
- mypy: **0 issues in 77 source files**.

The PR was squash-merged as commit `a33a2861cd5519db8c62a144c48406a27adb5c31`.
Post-merge Quality run #59 (`31895093547`) also completed successfully with Ruff, mypy, full pytest,
and cleanup all passing.

## Completion Boundary

AUTO-0002 is **COMPLETE / VERIFIED** for the approved V1 scope.

This does not imply marker initialization, free-form documentation rewriting, additional writable
documents, Git staging/commit/push, remote services, project execution, dependency installation,
release publication, or PyPI support.
