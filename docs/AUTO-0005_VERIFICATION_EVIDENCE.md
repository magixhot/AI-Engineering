# AUTO-0005 Verification Evidence

## Status

**Milestone:** AUTO-0005 — Python Engineering Baseline V2 / First Production Migration

**Result:** COMPLETE / VERIFIED

**Verified implementation baseline:** `8a2ea40ff61873c91c9bfb77529f2486068dab2c`

## Approved Contract

AUTO-0005 defines the production `python-engineering-v2` baseline and the first registered production migration edge, `python-engineering-v1-to-v2`, while preserving the generic SDK-0001 / SDK-0001.1 scaffold contract.

The V2 baseline adds exactly two machine-owned changes over the legacy V1 engineering baseline:

- `.ai-engineering.toml` as the explicit V2 identity marker;
- `.gitignore` cache hygiene entries for `.pytest_cache/`, `.mypy_cache/`, and `.ruff_cache/`.

No dependency upgrade, Python-version change, generated CI workflow, release/version/tag change, TestPyPI publication, or PyPI publication is part of AUTO-0005.

## Implementation Evidence

### AUTO-0005-01 — Design

The V2 and first-production-edge contract was approved and merged before implementation. The design requires the `python-engineering` bootstrap profile to create V2 directly in its initial commit while leaving generic SDK project creation unchanged.

Quality evidence:

- PR Quality #113 — PASS
- post-merge Quality #114 — PASS

### AUTO-0005-02 — V2 Baseline / Bootstrap

The engineering bootstrap now emits the V2 identity marker and V2 `.gitignore` as deterministic UTF-8/LF machine-owned bytes in the same initial Git commit. Generic SDK scaffold behavior remains separate and compatible with the legacy V1 fixture contract.

Quality evidence:

- corrected PR Quality #120 — PASS
- post-merge Quality #121 — PASS

The earlier failing #115 exposed stale tests that incorrectly used engineering bootstrap as a legacy V1 fixture. Those fixtures were corrected to create V1 through the generic SDK scaffold; production behavior was not reverted.

### AUTO-0005-03 — Dual Identity / Production Registry Edge

Project identity now positively recognizes both supported baselines. A malformed or unapproved V2 marker fails closed. `DEFAULT_MIGRATION_REGISTRY` contains exactly the approved production edge `python-engineering-v1-to-v2`.

That edge uses only existing AUTO-0004 operation types and touches only:

- create `.ai-engineering.toml`;
- exact machine-owned replace of `.gitignore`.

The same migration id resolves on the exact target baseline only to support deterministic idempotent no-op verification. Unrelated baselines and unsupported migration ids still fail closed.

Quality evidence:

- corrected PR Quality #123 — PASS
- post-merge Quality #124 — PASS

The earlier #122 failure was formatting-only Ruff E501 and did not change migration semantics.

### AUTO-0005-04 — Installed Distribution Verification

The release test builds the current wheel, installs it into an isolated virtual environment, creates a legacy V1 project through the installed public CLI, and exercises the real production migration using:

```text
ai-engineering project migrate check --project PATH --migration python-engineering-v1-to-v2
ai-engineering project migrate plan --project PATH --migration python-engineering-v1-to-v2
ai-engineering project migrate apply --project PATH --migration python-engineering-v1-to-v2
```

The installed-wheel test verifies:

- V1 planning exposes only the two approved migration paths;
- apply creates the approved marker and V2 `.gitignore` target;
- Git HEAD remains unchanged;
- the staged index remains unchanged;
- only approved working-tree paths change;
- repeated plan/apply is an idempotent no-op;
- unsupported migration ids remain controlled fail-closed errors without traceback.

Quality evidence:

- PR Quality #125 — PASS
- post-merge Quality #126 — PASS on exact master `8a2ea40ff61873c91c9bfb77529f2486068dab2c`

## Preserved Boundaries

AUTO-0004 guarded planning/apply/rollback and Git invariants remain the migration execution boundary. AUTO-0005 does not add new migration operation types or broaden execution authority.

The published `v0.2.0` release remains immutable at tag target `1faf14c121b7b5da7c8781e3de4e836f85838a76`. Post-release AUTO-0005 work does not alter that release evidence or assets.

PyPI remains explicitly not approved and not published.

## Final Result

AUTO-0005 is complete and verified for its approved scope: new `python-engineering` bootstraps use the explicit V2 baseline, legacy V1 projects can be positively identified and safely migrated through the first registered production edge, and the full public migration path is verified from an isolated installed wheel.
