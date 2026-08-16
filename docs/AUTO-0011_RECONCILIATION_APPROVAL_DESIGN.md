# AUTO-0011 — Reconciliation Approval Design

**Status:** DESIGN / CONTRACT ONLY

## Purpose

AUTO-0011 adds an explicit, typed approval boundary between reconciliation planning/policy evaluation and any guarded mutation. It is intended for operators who want a reviewed plan to be approved before execution without expanding the workflows or mutation authority already established by AUTO-0007 through AUTO-0010.

## Existing authority boundaries

AUTO-0011 MUST preserve these boundaries:

- AUTO-0007 remains the permanent read-only reconciliation planner.
- AUTO-0008 remains the sole guarded one-step mutation authority.
- AUTO-0009 remains bounded multi-step orchestration with replanning between writes.
- AUTO-0010 remains restriction-only policy and cannot grant authority.
- AUTO-0011 approval MUST NOT create a new mutation implementation or bypass any earlier guard.

Approval is therefore an additional necessary condition when explicitly requested, never a sufficient condition for mutation.

## Proposed capability

A read-only approval preparation operation produces a canonical approval request for the current reconciliation candidate. A separate execution invocation may consume that approval only if it still matches the freshly replanned candidate and current guarded context.

Conceptual public shape:

```text
ai-engineering project reconcile approve --project PATH [--policy POLICY.toml]
ai-engineering project reconcile run --project PATH --approval APPROVAL.json [--policy POLICY.toml] [--max-steps N]
```

Exact CLI spelling is not implementation-approved by this design stage; later stages may refine it without weakening the contract below.

## Typed approval request

The approval artifact must be deterministic and machine-readable. At minimum it binds:

- a schema/version identifier;
- project identity in a portable, non-secret form;
- the exact typed reconciliation candidate/workflow;
- canonical candidate inputs sufficient to detect semantic drift;
- the observed Git HEAD and branch state relevant to guarded execution;
- the effective policy decision or policy fingerprint when policy is supplied;
- an explicit approval scope of one candidate only;
- a deterministic digest over the canonical approval payload.

The artifact MUST NOT contain credentials, tokens, private keys, or hidden mutation authority.

## Approval semantics

Approval is single-candidate and fail-closed.

Before every candidate mutation, execution must freshly perform the existing planning, Git safety checks, and policy evaluation. The supplied approval may authorize continuation only when the fresh candidate and bound context match the approval exactly according to the typed contract.

An approval MUST be rejected when any bound field has changed, including candidate/workflow drift, relevant Git state drift, policy drift, malformed/unknown approval fields, unsupported schema versions, digest mismatch, or ambiguity.

A rejected or invalid approval causes zero writes for that candidate.

## Multi-step orchestration

AUTO-0011 does not approve an entire AUTO-0009 run in advance. Because orchestration replans after each successful write, each newly selected candidate requires its own matching approval when approval mode is enabled.

A previous candidate's approval MUST NOT be reusable for the next candidate, even if the workflow type is identical.

This preserves bounded authority and prevents an approval artifact from becoming a batch mutation capability.

## Policy interaction

AUTO-0010 remains restriction-only and is evaluated freshly before mutation. Approval cannot override policy refusal, increase `max_steps`, permit an unknown workflow, or weaken any Git guard.

The effective rule is intersection-only:

```text
existing mutation authority
AND current Git guards
AND current policy permission (when policy is supplied)
AND matching current approval (when approval mode is requested)
```

Any false/invalid/unknown term fails closed.

## Determinism and portability

Canonical serialization must be deterministic across equivalent input ordering. Digest calculation must exclude presentation-only variation and include all authority-relevant approval fields.

Approval verification must work from the installed distribution outside the source checkout.

No network service, remote signing authority, GitHub API, or local daemon is required by AUTO-0011. Cryptographic identity/signature infrastructure is explicitly out of scope unless introduced by a later separately approved milestone.

## Git invariants

Approval preparation is read-only.

Approval verification itself is read-only. On approval error/refusal, the implementation must preserve at least:

- HEAD;
- current branch/detached state;
- index bytes/state;
- working-tree bytes;
- remotes;
- repository configuration;
- untracked files.

Successful mutation remains delegated only to the existing AUTO-0008/AUTO-0009 path and therefore remains subject to their established invariants.

## Failure model

Later implementation should expose typed evidence distinguishing at least:

- approval missing when required;
- approval malformed;
- approval schema unsupported;
- approval digest invalid;
- approval candidate mismatch;
- approval Git-context mismatch;
- approval policy-context mismatch;
- approval refused for another deterministic contract reason.

Errors must be stable enough for CLI JSON/evidence tests and must not silently fall back to unapproved execution.

## Non-goals

AUTO-0011 does not introduce:

- new reconciliation workflows;
- new file mutation primitives;
- autonomous approval;
- interactive prompts that implicitly approve;
- approval of arbitrary shell commands;
- remote execution;
- background execution;
- network-based identity or signatures;
- whole-run/batch approval;
- bypass of dirty/staged/untracked/detached safeguards;
- bypass of AUTO-0010 policy.

## Staged delivery contract

AUTO-0011 is delivered strictly in order:

1. **AUTO-0011-01 — Design / Contract**: this document only; no production implementation.
2. **AUTO-0011-02 — Typed Approval Model / Canonicalization**: read-only model, parsing, canonical serialization, digest, validation tests.
3. **AUTO-0011-03 — Approval Verification / Safety Invariants**: read-only matching against fresh planner/Git/policy context; fail-closed and zero-write tests.
4. **AUTO-0011-04 — Guarded Integration**: integrate approval as an additional gate into the existing reconciliation run path without adding mutation authority.
5. **AUTO-0011-05 — Installed Distribution Verification**: wheel/install tests outside source checkout.
6. **AUTO-0011-06 — Final Evidence / Documentation Reconciliation**: authoritative docs and exact verified baseline.

Each stage requires its own pre-merge Quality success and exact post-merge Quality success before the next stage begins.

## Acceptance invariants

AUTO-0011 is acceptable only if tests prove:

- approval preparation and verification are deterministic and read-only;
- malformed, unknown, ambiguous, stale, or mismatched approval fails closed;
- refusal/error performs zero writes for the candidate;
- approval never expands workflow or mutation authority;
- policy remains independently restrictive;
- orchestration replans and requires a fresh matching approval per candidate;
- equivalent canonical inputs produce identical approval digests;
- authority-relevant drift changes or invalidates the digest/match;
- installed-wheel behavior matches source behavior;
- existing AUTO-0007/0008/0009/0010 tests remain green.

## Stage-01 completion rule

AUTO-0011-01 may be marked COMPLETE / VERIFIED only after this design-only change passes pre-merge Quality, is merged, and the exact resulting `master` commit passes post-merge Quality. Production implementation must not begin before that gate is complete.
