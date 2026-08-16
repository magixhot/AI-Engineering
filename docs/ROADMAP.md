# AI-Engineering Roadmap

## Completed / Verified

The documentation foundation, MCP foundation, SDK-0001 project templates/scaffold/CLI, TOOL-0001, REL-0001/REL-0002/REL-0003, CI-0001, SAFE-0001/SAFE-0002, and AUTO-0001 through AUTO-0009 are COMPLETE / VERIFIED for their approved scopes.

AUTO-0007 remains the permanent read-only reconciliation planner. AUTO-0008 remains the guarded one-step apply boundary. AUTO-0009 is the bounded multi-step orchestration layer over those existing boundaries.

## AUTO-0009 — Multi-step Reconciliation Orchestration

**Status:** COMPLETE / VERIFIED

AUTO-0009 adds bounded deterministic orchestration over existing AUTO-0007 planning and AUTO-0008 one-step execution. It requires a fresh plan before every mutation and never authorizes all future steps from one captured plan.

Public command:

```text
ai-engineering project reconcile run --project PATH
ai-engineering project reconcile run --project PATH --max-steps N
```

The default progress limit is 8 and the hard maximum is 100. No `force`, stale bypass, arbitrary step lists, parallel apply, new migration edges, publication, direct Git mutation, or whole-run transaction/rollback guarantee is added.

### AUTO-0009-01 — Multi-step Orchestration Design

**Status:** COMPLETE / VERIFIED

PR #99; Quality #189; post-merge Quality #190.

### AUTO-0009-02 — Guarded Orchestrator Core

**Status:** COMPLETE / VERIFIED

PR #100; corrected Quality #193; post-merge Quality #194.

### AUTO-0009-03 — Safety / Progress / Failure Invariants

**Status:** COMPLETE / VERIFIED

PR #101; Quality #195; post-merge Quality #196.

### AUTO-0009-04 — Public CLI

**Status:** COMPLETE / VERIFIED

PR #102; corrected Quality #199; post-merge Quality #200. The installed console entry point routes through `ai_engineering.public_cli:main` while preserving legacy CLI commands.

### AUTO-0009-05 — Installed Distribution Verification

**Status:** COMPLETE / VERIFIED

PR #103; Quality #201; post-merge Quality #202 on exact master `9564f8ffdc869bb0d8058f74c78c1e5138e5a37c`.

Verification builds and installs the wheel outside the source checkout and exercises multi-step completion, bounded `limit_reached`, unsupported zero-write refusal, and Git invariants.

### AUTO-0009-06 — Final Evidence / Documentation Reconciliation

**Status:** COMPLETE / VERIFIED

PR #104; Quality #203; post-merge Quality #204 on exact master `87419229713c93e869d596ffcfabafb12aec4c00`.

## Delivery Gates

AUTO-0009 stages executed strictly in order:

`01 → 02 → 03 → 04 → 05 → 06`

All six stages completed their required pre-merge and post-merge Quality gates. Final verified AUTO-0009 baseline:

```text
master = 87419229713c93e869d596ffcfabafb12aec4c00
```

## Current Priority

Preserve AUTO-0007 read-only planning, AUTO-0008 sole guarded one-step apply authority, and AUTO-0009 bounded replan-between-writes orchestration. Any next capability milestone must be defined separately before new production capability work begins.
