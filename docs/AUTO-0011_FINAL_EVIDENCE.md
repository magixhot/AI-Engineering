# AUTO-0011 — Final Evidence

**Milestone:** Reconciliation Approval  
**Closure stage:** AUTO-0011-06 Final Evidence / Documentation Reconciliation  
**State:** COMPLETE / VERIFIED

## Scope Delivered

AUTO-0011 adds an explicit optional approval boundary without adding mutation authority.

The delivered public surface is:

```text
ai-engineering project reconcile approve --project PATH [--policy POLICY.toml]
ai-engineering project reconcile run --project PATH --approval APPROVAL.json [--policy POLICY.toml] [--max-steps N]
```

The approval artifact is deterministic, typed, canonicalized, SHA-256 digest-bound, and scoped to one candidate. It binds authority-relevant candidate inputs, portable project identity, Git HEAD/branch state, and explicit policy context when supplied.

When approval mode is requested, execution freshly plans and evaluates the existing guards, then verifies the artifact against the current candidate/context. Malformed, stale, unsupported, tampered, or mismatched approval fails closed before that candidate write.

AUTO-0011 does not implement a new write primitive. Successful mutation remains delegated only through the existing AUTO-0008/AUTO-0009 path. AUTO-0010 remains independently restrictive.

## Authority Boundary

The effective execution condition remains intersection-only:

```text
existing AUTO-0008/AUTO-0009 mutation authority
AND current Git safety guards
AND current AUTO-0010 policy permission (when policy is supplied)
AND matching AUTO-0011 approval (when approval mode is requested)
```

Approval cannot create a workflow, override policy refusal, weaken Git safety, increase progress bounds, or approve an entire orchestration run.

AUTO-0009 replans after each successful write. Therefore an approval can authorize at most its bound candidate; the next candidate requires a fresh matching approval.

## Staged Delivery Evidence

| Stage | Pull Request | Pre-merge Quality | Exact post-merge Quality | State |
|---|---:|---:|---:|---|
| AUTO-0011-01 Design / Contract | #113 | #228 SUCCESS | #229 SUCCESS | COMPLETE / VERIFIED |
| AUTO-0011-02 Typed Approval Model / Canonicalization | #114 | #232 SUCCESS | #233 SUCCESS | COMPLETE / VERIFIED |
| AUTO-0011-03 Approval Verification / Safety Invariants | #115 | #235 SUCCESS | #236 SUCCESS | COMPLETE / VERIFIED |
| AUTO-0011-04 Guarded Integration | #116 | #238 SUCCESS | #239 SUCCESS | COMPLETE / VERIFIED |
| AUTO-0011-05 Installed Distribution Verification | #117 | #240 SUCCESS | #241 SUCCESS | COMPLETE / VERIFIED |
| AUTO-0011-06 Final Evidence / Documentation Reconciliation | #118 | #242 SUCCESS | #243 SUCCESS | COMPLETE / VERIFIED |

Earlier failed corrective runs remain historical evidence: #230/#231 during stage 02, #234 during stage 03, and #237 during stage 04. Each was corrected before the successful pre-merge gate listed above.

## Final Verified Baseline

```text
master = 94449b8754bb0bd803b5d60f38292e1530b82b1e
```

This exact commit is the squash merge of PR #118. Post-merge Quality #243 completed successfully on the `push` event for that exact `master` SHA. This establishes AUTO-0011 stages 01–06 as COMPLETE / VERIFIED.

## Verification Coverage

Recorded unit and release verification covers:

- deterministic construction across equivalent candidate input ordering;
- canonical compact JSON serialization and digest round-trip;
- strict schema/version/unknown-field validation;
- authority-relevant drift changing or invalidating approval;
- candidate, project, Git, and policy mismatch evidence;
- deterministic mismatch ordering and pure read-only verification;
- guarded CLI integration through `approve` and `run --approval`;
- one approval authorizing at most the bound candidate;
- stale approval refusal before any candidate write;
- malformed approval error before any candidate write;
- installed-wheel behavior in an isolated virtual environment outside the source checkout;
- continued preservation of the existing planner, policy, orchestration, and apply boundaries.

## Installed Distribution Evidence

AUTO-0011-05 builds a wheel, installs it into an isolated virtual environment, removes source-checkout `PYTHONPATH` influence, and invokes the installed `ai-engineering` console entry point.

The installed tests verify deterministic/read-only approval generation, matching approval execution for only the bound candidate, stale approval fail-closed behavior, malformed approval fail-closed behavior, stable terminal evidence, and absence of tracebacks.

## Security and Safety Claims

The verified scope supports these claims only:

- approval is an additional necessary condition when explicitly requested;
- approval does not grant new mutation authority;
- approval refusal/error prevents the current candidate write;
- policy remains restriction-only and independent;
- Git/candidate/policy drift invalidates a stale approval;
- approval is single-candidate rather than whole-run authority;
- approval preparation/verification introduces no network dependency or remote signing service.

AUTO-0011 does **not** claim cryptographic signer identity, non-repudiation, remote approval service security, rollback, atomic multi-step transactions, arbitrary command authorization, or publication authority.

## Closure

AUTO-0011 is COMPLETE / VERIFIED. The exact capability baseline produced by stage 06 is `94449b8754bb0bd803b5d60f38292e1530b82b1e`, with post-merge Quality #243 SUCCESS. This final documentation-only reconciliation records that already-verified fact and does not change production behavior or authority.
