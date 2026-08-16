# AUTO-0008 — Guarded Project Reconciliation Apply

**Status:** PROPOSED

## 1. Purpose

AUTO-0008 defines a separate guarded execution layer for applying already-approved project reconciliation work.

AUTO-0007 remains permanently read-only and authoritative for reconciliation planning. AUTO-0008 does not mutate AUTO-0007's contract. Instead, AUTO-0008 consumes a validated reconciliation plan and may orchestrate only existing write-capabilities that already have their own approved contracts.

The purpose is to answer:

> Can this exact, previously planned reconciliation step be applied now without expanding authority, guessing future state, or bypassing existing safety contracts?

## 2. Scope

AUTO-0008 may orchestrate only already-approved write operations exposed by existing subsystems:

- AUTO-0002 guarded documentation synchronization apply;
- AUTO-0003 guarded documentation ownership initialization apply, if and only if the existing subsystem exposes a production apply path approved for the exact planned operation;
- AUTO-0004/AUTO-0005 registered project migration apply for an exact approved migration identifier.

AUTO-0008 must not introduce:

- arbitrary file writes;
- arbitrary command or shell execution;
- new migration edges;
- new writable document classes or ownership semantics;
- dependency-upgrade policy;
- bootstrap-profile expansion;
- release/tag creation;
- TestPyPI or PyPI publication;
- network publication of any kind;
- speculative execution of steps beyond an explicit reinspection boundary.

## 3. Authority Boundary

AUTO-0008 is a distinct write-authority boundary.

AUTO-0007 continues to provide planning only. AUTO-0008 may execute only an exact workflow represented by an eligible AUTO-0007 plan step and only by delegating to the existing subsystem that already owns that write operation.

AUTO-0008 must not implement direct writes that duplicate or bypass those subsystem APIs.

If a planned workflow has no existing approved apply primitive, AUTO-0008 must fail closed with `manual_review` rather than inventing one.

## 4. Execution Model

The core API receives:

- a target project root;
- an immutable reconciliation plan or a stable execution token derived from that plan;
- the exact sequence number of the step to execute;
- expected pre-execution state captured during planning.

Before any write, AUTO-0008 must re-inspect the project and verify that the selected step is still valid.

Only one actionable reconciliation step may be applied per executor call.

AUTO-0008 must never execute a `reinspect_required` boundary as if it were a workflow.

## 5. Stable Apply States

The executor returns one of these stable states:

- `applied` — the exact selected workflow completed and required post-apply verification passed;
- `no_change` — the selected workflow is no longer necessary and no write occurred;
- `stale_plan` — current project/Git state no longer matches the plan preconditions;
- `manual_review` — the operation cannot be applied safely under existing contracts;
- `unsupported` — project identity or required subsystem support is unavailable;
- `failed` — a controlled apply failure occurred and the executor reports bounded recovery/rollback evidence.

Precedence for pre-write refusal is:

`unsupported > manual_review > stale_plan > no_change > applied`

`failed` is a post-attempt terminal state and must not be collapsed into another state.

## 6. Eligibility Rules

A step is executable only when all of the following are true:

1. the project identity is supported;
2. the current AUTO-0007 plan is `ready`;
3. the selected sequence exists and has `state=ready`;
4. the selected workflow exactly matches a known allow-listed workflow;
5. all preconditions and expected digests/state still match current inspection;
6. the Git/workspace safety requirements for that workflow are satisfied;
7. the existing owning subsystem reports that its guarded apply operation is currently applicable.

If any rule fails, no write may occur.

## 7. Stale-Plan Detection

AUTO-0008 must detect plan staleness before delegating any write.

At minimum, stale-plan comparison covers every input that can affect whether the selected workflow remains valid, including as applicable:

- resolved project root and containment result;
- project identity/version marker;
- relevant documentation ownership markers;
- relevant document digests/expected bytes owned by the existing apply contract;
- migration identity and migration preconditions;
- bounded Git HEAD/branch/status observations required by the owning workflow;
- selected workflow identifier and sequence;
- reinspection-boundary semantics.

A stale plan must produce `stale_plan` with zero project writes and zero Git mutations.

## 8. Git and Workspace Safety

AUTO-0008 must preserve SAFE-0001/SAFE-0002 boundaries and each delegated subsystem's stronger requirements.

The executor itself must not run arbitrary shell commands or project code. Any subprocess use must already be approved by the delegated subsystem contract and must preserve `shell=False` and bounded argument construction.

AUTO-0008 must not create commits, switch branches, stage files, modify remotes, change Git configuration, push, fetch, tag, or publish.

If a delegated workflow requires a clean working tree or other Git precondition, AUTO-0008 must re-check it immediately before apply and fail closed if it is not satisfied.

## 9. One-Step and Reinspection Rule

AUTO-0008 applies at most one actionable step per call.

After a successful apply, the project must be re-inspected. If the AUTO-0007 plan indicated `reinspect_after_step=true`, no later step from the old plan may be executed without generating a fresh reconciliation plan.

AUTO-0008 must never simulate or assume hypothetical bytes/state for later steps.

## 10. Delegation Contract

AUTO-0008 delegates execution rather than owning subsystem-specific mutation logic.

Expected delegation mapping is bounded to approved capabilities, for example:

- reconciliation workflow `project docs apply` -> AUTO-0002 guarded documentation apply API;
- reconciliation workflow for exact registered migration `python-engineering-v1-to-v2` -> AUTO-0004/AUTO-0005 guarded migration apply API;
- any ownership-initialization execution path -> only an existing explicitly approved AUTO-0003 apply primitive, otherwise `manual_review`.

The final mapping must be derived from the actual production APIs present when AUTO-0008-02 begins. The design does not authorize creating missing write primitives merely to satisfy orchestration.

## 11. Failure and Rollback Semantics

AUTO-0008 must preserve the delegated subsystem's rollback guarantees and may not claim stronger atomicity than the subsystem provides.

For every execution attempt, the result must report:

- whether any write was attempted;
- which approved workflow owned the write;
- whether post-apply verification passed;
- whether rollback was attempted;
- rollback outcome when applicable;
- whether reinspection is required before further work.

A controlled failure must not emit a traceback through the public CLI.

If rollback cannot restore the owning subsystem's expected pre-state, the result must be `failed` with explicit manual-review evidence and no attempt to continue to another reconciliation step.

## 12. Determinism

Given identical project bytes, identity, relevant Git observations, selected plan, and environment inputs allowed by existing contracts, pre-write eligibility and refusal results must be deterministic.

AUTO-0008 must preserve stable ordering for issues/evidence fields and stable machine-readable output.

Execution side effects themselves are delegated and must remain bounded by the existing subsystem contracts.

## 13. Core Result Model

The typed core result should be immutable and include at minimum:

- resolved project root;
- selected plan sequence;
- selected workflow identifier;
- apply state;
- `write_attempted`;
- delegated subsystem identifier;
- stable ordered issues/evidence;
- rollback status where applicable;
- `reinspect_required`;
- post-apply overall health/reconciliation state when it can be determined safely from fresh inspection.

No result field may imply publication, commit creation, or multi-step completion when those actions did not occur.

## 14. Public CLI Contract

Planned public command for a later stage:

```text
ai-engineering project reconcile apply --project PATH --step SEQUENCE
```

The final CLI shape is not approved until AUTO-0008-04, but the design reserves the following requirements:

- deterministic `key=value` output;
- no interactive hidden confirmation path;
- controlled failures without traceback;
- exit `0` only for `applied` or `no_change`;
- exit `1` for `stale_plan`, `manual_review`, `unsupported`, or `failed`;
- no option that means `apply all`, `force`, `ignore stale`, or arbitrary workflow execution.

## 15. Verification Matrix

Verification must include at minimum:

- healthy/clean project => no executable apply, zero writes;
- exact eligible docs synchronization step => delegate only to guarded documentation apply;
- exact eligible registered migration step => delegate only to guarded migration apply;
- ownership step without approved apply primitive => `manual_review`, zero writes;
- `reinspect_required` selected as a step => refusal, zero writes;
- plan/project identity mismatch => `stale_plan` or `unsupported`, zero writes as appropriate;
- relevant project byte changed after planning => `stale_plan`, zero executor writes;
- required Git state changed after planning => `stale_plan`/manual-review refusal, zero writes;
- unsupported/malformed identity => fail closed;
- deterministic repeated eligibility/refusal output;
- delegated apply failure => controlled `failed`, bounded rollback evidence, no later step execution;
- successful apply => fresh reinspection before reporting final state;
- project/Git invariants outside the delegated write scope remain unchanged;
- installed-wheel isolated-environment verification;
- CLI controlled output and exit codes.

## 16. Delivery Sequence

AUTO-0008 is delivered in bounded stages:

1. **AUTO-0008-01 — Apply Design / Authority Contract**
2. **AUTO-0008-02 — Guarded Executor Core**
3. **AUTO-0008-03 — Stale Plan / Failure / Git Safety Invariants**
4. **AUTO-0008-04 — Public CLI**
5. **AUTO-0008-05 — Installed Distribution Verification**
6. **AUTO-0008-06 — Final Evidence / Documentation Reconciliation**

Each stage requires the normal Quality gate before merge and a successful post-merge Quality gate before the next stage begins.

## 17. Definition of Done

AUTO-0008 is complete only when:

- AUTO-0007 remains unchanged and read-only;
- the executor can apply only explicitly allow-listed, already-approved write primitives;
- stale/manual-review/unsupported conditions are proven fail-closed with zero unauthorized writes;
- one-step execution and reinspection boundaries are enforced;
- failure/rollback reporting is verified against the delegated subsystem guarantees;
- public CLI behavior is deterministic and controlled;
- installed-wheel behavior is verified outside the source checkout;
- production, Quality, post-merge, and authoritative documentation evidence agree.

## 18. Compatibility and Publication Boundaries

AUTO-0008 must preserve all verified AUTO-0001 through AUTO-0007 contracts and SAFE-0001/SAFE-0002 boundaries.

The immutable published `v0.2.0` release remains unchanged. AUTO-0008 does not authorize a version bump, tag, GitHub Release, TestPyPI, PyPI, or any other publication.
