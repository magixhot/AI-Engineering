# AUTO-0009 — Multi-step Reconciliation Orchestration Design

**Status:** DESIGN / NOT YET IMPLEMENTED

## Purpose

AUTO-0009 defines a guarded orchestration layer for progressing through multiple reconciliation steps while preserving the permanent AUTO-0007 read-only planner boundary and the verified AUTO-0008 one-step executor authority boundary.

AUTO-0009 MUST compose existing planning and execution capabilities. It MUST NOT create a second mutation engine or broaden subsystem authority.

## Core Contract

A multi-step orchestration request is a sequence of individually re-planned and individually authorized AUTO-0008 executions. It is not an atomic transaction and it is not an `apply all` shortcut.

For every step, the orchestrator MUST:

1. inspect and build a fresh AUTO-0007 reconciliation plan;
2. stop with zero writes when the plan is unsupported, manual-review, stale, ambiguous, or otherwise non-executable;
3. select only the next eligible step permitted by policy;
4. delegate exactly that one step through the AUTO-0008 guarded executor;
5. require the executor result to be successful before continuing;
6. re-inspect and build a new plan before considering another write;
7. stop immediately on failure, refusal, unexpected state, or exhausted progress budget.

No future step may be authorized from a plan captured before a preceding mutation.

## Authority Boundary

AUTO-0009 may orchestrate only steps already executable through AUTO-0008. It adds no new writable documents, migration edges, ownership semantics, commands, publication behavior, arbitrary file writes, arbitrary command execution, or rollback guarantees.

AUTO-0007 remains permanently read-only.

AUTO-0008 remains the only reconciliation apply boundary and retains responsibility for one-step eligibility, stale-plan validation, delegated subsystem mutation, and one-step result reporting.

AUTO-0009 MUST NOT bypass, duplicate, weaken, or reach behind AUTO-0008 validation.

## Explicit Non-goals

AUTO-0009 does not authorize:

- `--force` or stale-plan bypasses;
- executing a caller-supplied list of arbitrary steps;
- applying all steps from one previously captured plan;
- parallel reconciliation writes;
- arbitrary shell or Python execution;
- new migration edges or new write primitives;
- Git commit, push, branch mutation, tag, release, TestPyPI, PyPI, or other publication;
- cross-project orchestration;
- claims of whole-run atomicity or guaranteed rollback.

## Progress Model

The orchestrator operates on one project per invocation and maintains a bounded in-memory execution trace.

Each successful write consumes one progress unit. A configurable implementation limit may be introduced, but the public contract MUST have a finite safe default and MUST reject invalid or unbounded limits.

A run terminates as one of:

- `complete` — fresh inspection reports no remaining executable reconciliation work;
- `stopped` — fresh inspection requires manual review, reports unsupported state, or reaches a non-executable boundary;
- `failed` — an AUTO-0008 execution fails or post-step state violates the contract;
- `limit_reached` — additional eligible work exists but the bounded progress budget is exhausted;
- `no_change` — initial fresh inspection has no executable work.

`complete` and `no_change` are successful terminal states. `stopped`, `failed`, and `limit_reached` are non-success terminal states unless a later stage explicitly defines a narrower machine-readable distinction.

## Determinism and Step Selection

Given identical project bytes, Git state, installed capability set, and configuration, the next-step selection and terminal result MUST be deterministic.

AUTO-0009 MUST follow the canonical ordering produced by AUTO-0007. It MUST NOT reorder steps for convenience or optimize by skipping required reinspection boundaries.

## Stale-state Safety

Every mutation requires a fresh plan immediately before AUTO-0008 delegation. If relevant project or Git state changes between planning and execution, AUTO-0008 stale-plan protection remains authoritative and the orchestration run MUST stop.

The orchestrator MUST NOT automatically retry a refused stale execution using the same intended step. A fresh orchestration decision is required from a newly inspected state.

## Failure and Rollback Semantics

AUTO-0009 is not a transaction manager. Successful earlier delegated steps remain successful if a later step fails unless the owning subsystem itself provides and performs a bounded rollback.

The orchestration result MUST preserve ordered evidence for each attempted step, including the AUTO-0008 result and the terminal reason. It MUST never claim whole-run rollback when only a delegated subsystem rollback was attempted or achieved.

## Git Invariants

Unless an already-approved delegated subsystem explicitly owns a documented Git mutation, AUTO-0009 MUST preserve Git HEAD, current branch, index, remotes, and repository configuration exactly as AUTO-0008 requires.

AUTO-0009 itself owns no Git mutation authority.

## Proposed Public CLI Boundary

A later implementation stage may expose:

```text
ai-engineering project reconcile run --project PATH
```

A bounded option such as `--max-steps N` may be considered only if it has a finite safe default and cannot disable the bound.

The public CLI MUST NOT expose `--force`, stale bypass, arbitrary step lists, parallel apply, publication, or hidden interactive write authority.

This stage does not implement or expose the command.

## Typed Result Shape

The implementation should define a typed orchestration result containing at minimum:

- terminal status;
- project path / identity evidence;
- ordered attempted-step results;
- successful step count;
- final freshly inspected reconciliation state or terminal issue evidence;
- deterministic human/machine-readable reason.

The result MUST distinguish no-write refusal from partial progress followed by failure.

## Verification Matrix

Implementation stages MUST verify at least:

- zero-work project produces `no_change` with zero writes;
- two or more eligible steps are executed only one at a time with fresh planning between them;
- canonical order is preserved;
- manual-review and unsupported states stop with zero additional writes;
- stale state stops the run and is never bypassed;
- failure on a later step preserves evidence for earlier successful steps without claiming global rollback;
- progress limit prevents unbounded execution;
- repeated runs from identical state are deterministic;
- Git invariants hold across success, refusal, failure, and limit termination;
- AUTO-0007 remains byte-for-byte/read-only in behavior;
- AUTO-0008 remains the sole apply authority;
- installed-wheel/public CLI behavior is verified outside the source checkout before milestone closure.

## Proposed Delivery Stages

1. **AUTO-0009-01 — Multi-step Orchestration Design** — this document; no production capability.
2. **AUTO-0009-02 — Guarded Orchestrator Core** — typed bounded loop composed over AUTO-0007 + AUTO-0008.
3. **AUTO-0009-03 — Safety / Progress / Failure Invariants** — test-only strengthening of replan, determinism, partial-progress, limit, and Git boundaries.
4. **AUTO-0009-04 — Public CLI** — expose the bounded orchestration command without new authority.
5. **AUTO-0009-05 — Installed Distribution Verification** — build/install wheel and verify the public path outside source checkout.
6. **AUTO-0009-06 — Final Evidence / Documentation Reconciliation** — reconcile authoritative docs only after all preceding gates pass.

Stages MUST execute in order. Each stage requires its normal pre-merge Quality gate and exact post-merge Quality gate before the next stage begins.

## Definition of Done

AUTO-0009 is complete only when:

- orchestration is bounded and deterministic;
- every mutation is delegated as one independently revalidated AUTO-0008 step;
- a fresh AUTO-0007 plan is required between writes;
- unsupported/manual-review/stale/failure states fail closed;
- partial progress is reported truthfully without invented transaction guarantees;
- Git invariants and permanent AUTO-0007 read-only boundaries remain verified;
- public and installed-distribution behavior are verified;
- authoritative documentation matches the exact final verified master baseline.
