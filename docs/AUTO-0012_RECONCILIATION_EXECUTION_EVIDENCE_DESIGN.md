# AUTO-0012 — Deterministic Reconciliation Execution Evidence / Receipts Design

**Status:** DESIGN / CONTRACT ONLY

## Purpose

AUTO-0012 adds a deterministic, machine-readable execution receipt for reconciliation runs. The receipt records what the already-authorized reconciliation path observed and did; it does not authorize, replay, repeat, widen, or otherwise cause mutation.

This milestone follows the established authority sequence:

```text
AUTO-0007 plan
→ AUTO-0008 guarded one-step apply
→ AUTO-0009 bounded orchestration
→ AUTO-0010 restriction-only policy
→ AUTO-0011 optional single-candidate approval
→ AUTO-0012 deterministic execution evidence
```

AUTO-0012 is therefore an evidence capability, not a new execution capability.

## Existing authority boundaries

AUTO-0012 MUST preserve these boundaries:

- AUTO-0007 remains permanently read-only.
- AUTO-0008 remains the sole guarded one-step reconciliation mutation authority.
- AUTO-0009 remains bounded orchestration with fresh planning between writes.
- AUTO-0010 remains restriction-only and cannot grant authority.
- AUTO-0011 approval remains an additional necessary single-candidate gate when explicitly requested.
- AUTO-0012 MUST NOT create a new mutation implementation, mutation workflow, bypass, retry path, replay path, or execution authority.

A receipt is historical evidence about an invocation. Possession of a receipt MUST NOT be sufficient to authorize any later action.

## Proposed public shape

The existing `project reconcile run` behavior remains the execution surface. AUTO-0012 may add an explicit receipt-output mode that emits canonical JSON to standard output without writing a receipt file itself.

Conceptual shape:

```text
ai-engineering project reconcile run --project PATH [existing run options] --receipt-json
```

Exact CLI spelling is not implementation-approved by this design stage and may be refined later without weakening this contract.

Without the explicit receipt mode, existing public output and exit-code behavior MUST remain compatible.

AUTO-0012 itself MUST NOT add a receipt-path option that writes arbitrary files. Operators may redirect standard output externally if they choose; such redirection is outside AI-Engineering reconciliation authority.

## Receipt model

The receipt must be deterministic, typed, versioned, canonicalizable, and machine-readable. At minimum, version 1 must be able to represent the following authority-relevant observations when they exist:

- receipt schema/version and receipt kind;
- portable project identity, not checkout-path identity;
- requested orchestration bounds relevant to execution;
- initial reconciliation state relevant to the run;
- relevant Git HEAD and branch state captured for evidence;
- whether an explicit policy was used and its deterministic fingerprint, without embedding policy source paths as identity;
- ordered policy decisions relevant to candidate execution;
- whether explicit approval mode was used and the approval artifact digest/scope or equivalent non-secret identity evidence;
- ordered approval verification outcomes relevant to candidate execution;
- ordered delegated apply attempts, including sequence, workflow, state, whether a write was attempted, delegated subsystem, bounded issues, rollback evidence, and post-apply state;
- successful-step count;
- terminal orchestration state and bounded terminal issues;
- final reconciliation-plan state and deterministic remaining-work summary;
- a deterministic receipt digest over all authority-relevant receipt payload fields except the digest field itself.

The receipt MUST NOT contain credentials, tokens, private keys, environment secrets, arbitrary file contents, or raw policy/approval source bytes merely for convenience.

Absolute local checkout paths are presentation details and MUST NOT be used as portable project identity or digest authority.

## Canonicalization and digest

Canonical receipt serialization must be deterministic for semantically identical typed receipt values.

The contract requires:

- UTF-8 JSON;
- one supported schema version at a time, beginning with version 1;
- deterministic object-key ordering;
- compact representation without presentation-dependent whitespace;
- ordered arrays only where order has execution meaning, such as candidate/apply attempts;
- deterministic normalization of set-like evidence before serialization;
- SHA-256 digest over the canonical authority-relevant payload excluding the digest field itself.

The digest provides deterministic integrity evidence only. It is not a digital signature, signer identity, authentication mechanism, authorization token, timestamp authority, or non-repudiation proof.

## Evidence projection

Receipt construction must be a pure projection from already-observed run evidence plus explicitly defined read-only context.

Receipt construction MUST NOT:

- select a candidate;
- change candidate ordering;
- alter `max_steps` or effective policy limits;
- cause a policy decision;
- approve a candidate;
- call a mutation primitive;
- retry a refused/failed step;
- suppress a failure;
- convert a refusal into success;
- perform rollback;
- publish or commit evidence to Git.

When receipt mode is enabled, orchestration must still use exactly the existing AUTO-0008/AUTO-0009 mutation path and the same AUTO-0010/AUTO-0011 gates.

## Timing and truthfulness

Evidence should be captured from the same invocation that produced the terminal orchestration result.

The receipt must distinguish pre-write refusal/error from attempted writes and successful writes using the already-established typed execution evidence. It MUST NOT imply that a write occurred merely because a candidate existed or because approval/policy permitted it.

Receipt materialization occurs only from truthful observed evidence. A serialization/output failure after execution MUST NOT rewrite historical execution state or claim rollback. Later implementation must expose a stable evidence-output failure instead of silently emitting partial or ambiguous JSON.

## Policy interaction

AUTO-0010 remains independently restrictive. A receipt may record a policy fingerprint and policy decisions, but it cannot create, modify, override, or reinterpret policy authority.

A receipt must record policy outcomes as evidence of what was evaluated during that invocation, not as permission reusable by another invocation.

## Approval interaction

AUTO-0011 remains single-candidate and fail-closed. AUTO-0012 may record approval artifact identity/digest and verification outcomes, but a receipt MUST NOT become an approval artifact and MUST NOT be accepted as a substitute for approval.

Because orchestration replans after successful writes, receipt evidence may contain multiple candidate observations while each approved mutation still requires the existing fresh matching approval semantics.

Receipt contents therefore describe a run; they do not authorize a future run or a future candidate.

## Git invariants

Receipt construction and receipt serialization are read-only with respect to the reconciled project and Git repository.

AUTO-0012 itself must not mutate:

- HEAD;
- branch/detached state;
- index;
- working-tree content;
- remotes;
- repository configuration;
- tags;
- commits;
- untracked files.

Any project writes recorded by a receipt must originate only from previously approved AUTO-0008 delegated execution, not from receipt generation.

## Determinism boundaries

AUTO-0012 receipts intentionally exclude volatile presentation data that would make equivalent observed evidence produce different receipts without semantic cause.

Version 1 should not require wall-clock timestamps, random identifiers, hostnames, process IDs, temporary paths, or network-derived identity.

If future milestones need trusted time, remote attestation, signing, or provenance identity, those require separate contracts.

## Failure model

Later implementation should expose stable typed evidence for receipt-specific failures, including at least:

- unsupported receipt schema/version;
- canonicalization failure for an invalid internal receipt value;
- receipt digest mismatch when parsing/verifying a serialized receipt;
- malformed/unknown receipt fields;
- unavailable required read-only context;
- output/materialization failure.

Receipt-specific failure MUST NOT silently change the underlying orchestration result.

## Compatibility

Existing reconciliation execution without receipt mode must retain existing behavior.

AUTO-0012 must not require receipt consumption by AUTO-0007 through AUTO-0011. Earlier planner/apply/orchestration/policy/approval contracts remain independently usable and testable.

Receipt parsing/verification, if exposed publicly, must itself be read-only.

## Non-goals

AUTO-0012 does not introduce:

- new reconciliation workflows;
- new project file mutation primitives;
- arbitrary receipt-file writes by the application;
- receipt-driven execution or replay;
- automatic retry or resume;
- rollback or transactional orchestration;
- cryptographic signer identity;
- signatures, PKI, certificates, key management, or non-repudiation;
- remote evidence services or network logging;
- trusted timestamps;
- policy grant authority;
- approval grant authority beyond AUTO-0011;
- Git commit/tag/push authority;
- package publication or release authority.

## Staged delivery contract

AUTO-0012 is delivered strictly in order:

1. **AUTO-0012-01 — Execution Evidence Design / Contract**: this document only; no production implementation.
2. **AUTO-0012-02 — Typed Receipt Model / Canonicalization**: typed versioned receipt, canonical JSON, digest, strict parser/validation, deterministic tests.
3. **AUTO-0012-03 — Evidence Projection / Safety Invariants**: pure receipt projection from orchestration evidence and read-only context; determinism, no-authority, and Git-invariant tests.
4. **AUTO-0012-04 — Public CLI Integration**: explicit canonical JSON receipt output on the existing run path without adding mutation authority or arbitrary receipt-file writes.
5. **AUTO-0012-05 — Installed Distribution Verification**: wheel/install tests outside the source checkout covering successful, refused, failed, policy-gated, and approval-gated evidence.
6. **AUTO-0012-06 — Final Evidence / Documentation Reconciliation**: authoritative documentation and historical verified closure evidence.

Each stage requires its own pre-merge Quality success and exact post-merge Quality success before the next stage begins.

## Acceptance invariants

AUTO-0012 is acceptable only if tests prove:

- typed equivalent receipt evidence produces identical canonical JSON bytes and digest;
- authority-relevant evidence changes the receipt digest;
- parser/verification fails closed on malformed, unknown, unsupported, or digest-mismatched receipts;
- receipt generation is a pure observational projection and cannot select or mutate reconciliation work;
- existing no-receipt execution behavior is unchanged;
- receipt evidence truthfully distinguishes refusal/error, attempted write, successful write, and terminal state;
- policy and approval evidence remains observational and cannot be reused as authority;
- receipt generation itself preserves Git/project state;
- receipt output contains no required secrets, random IDs, host-specific identity, or wall-clock timestamp dependency;
- installed-wheel behavior matches source behavior;
- existing AUTO-0007/0008/0009/0010/0011 tests remain green.

## Stage-01 completion rule

AUTO-0012-01 may be marked COMPLETE / VERIFIED only after this design-only change passes pre-merge Quality, is merged, and the exact resulting `master` commit passes post-merge Quality. Production implementation must not begin before that gate is complete.
