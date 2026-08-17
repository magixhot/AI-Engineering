# AUTO-0012 — Final Evidence

## Status

AUTO-0012 Deterministic Reconciliation Execution Evidence / Receipts is COMPLETE / VERIFIED for its approved scope through stages 01–05. Stage 06 reconciles the authoritative documentation against that verified implementation baseline.

Receipts are deterministic machine-readable execution evidence only. They are never authority tokens and cannot grant, widen, replay, resume, retry, or bypass reconciliation mutation authority.

## Delivery Evidence

| Stage | Scope | Evidence |
|---|---|---|
| AUTO-0012-01 | Execution Evidence Design / Contract | PR #121; Quality #248; post-merge Quality #249; merge `079324ac12305dbe682e3b22ceeeee306aafca3d` |
| AUTO-0012-02 | Typed Receipt Model / Canonicalization | PR #122; corrected Quality #251; post-merge Quality #252; merge `2d8f8b7215ee1f42dc8e8c475a3239b2fca860e4` |
| AUTO-0012-03 | Evidence Projection / Safety Invariants | PR #123; Quality #253; post-merge Quality #254; merge `7338f634ef5b4851514a1845e5395d84d0aa4eaa` |
| AUTO-0012-04 | Public CLI Integration | PR #124; corrected Quality #257; post-merge Quality #258; merge `0e54ddb68717ed5b855442b7a638a0603a62e548` |
| AUTO-0012-05 | Installed Distribution Verification | PR #125; corrected Quality #260; post-merge Quality #261; merge `2268f4c8278f3c81b5735e26337984aebd300c6b` |

Earlier failing Quality runs (#250, #255, #256, and #259) were corrected before the corresponding stage merge and are retained as historical CI evidence.

## Verified Implementation Baseline

The verified AUTO-0012 implementation baseline before final documentation reconciliation is:

```text
2268f4c8278f3c81b5735e26337984aebd300c6b
```

Exact post-merge Quality #261 completed successfully on that `master` commit. This SHA is historical verification evidence, not a requirement that future `master` remain equal to it.

## Public Surface

AUTO-0012 adds an explicit canonical receipt output mode to the existing orchestration command:

```text
ai-engineering project reconcile run --project PATH [--max-steps N] [--policy POLICY.toml] [--approval APPROVAL.json] --receipt-json
```

Without `--receipt-json`, the existing run output and exit behavior remain compatible.

Receipt v1 records bounded, already-observed execution evidence including portable project identity, requested bounds, initial reconciliation state, Git HEAD/branch, policy fingerprint and decisions, approval digest/scope and observed verification outcomes, delegated apply attempts, successful-step count, terminal state/issues, final plan state, remaining-work summary, and a SHA-256 digest over the canonical payload excluding the digest field.

Canonical receipt JSON is compact UTF-8 with sorted object keys. Execution-order arrays preserve order; set-like evidence is normalized deterministically. Volatile timestamps, random identifiers, hostnames, PIDs, temporary paths, credentials, secrets, raw policy bytes, and raw approval bytes are outside receipt v1.

## Authority and Safety Invariants

AUTO-0007 remains permanently read-only. AUTO-0008 remains the sole guarded one-step mutation authority. AUTO-0009 remains bounded orchestration with fresh replanning between writes. AUTO-0010 remains restriction-only policy. AUTO-0011 approval remains an additional necessary single-candidate gate, never sufficient mutation authority.

AUTO-0012 receipt construction is an observational projection from already-observed orchestration evidence plus defined read-only context. Receipt generation must not select or reorder candidates, alter bounds or policy, approve a candidate, invoke mutation, retry, suppress failure, convert refusal to success, perform rollback, or mutate Git/project state.

Receipt evidence cannot substitute for AUTO-0010 policy or AUTO-0011 approval. A receipt digest is evidence integrity material only and cannot be presented as execution permission.

## Installed Distribution Verification

Stage 05 builds the wheel, installs it into an isolated virtual environment without `PYTHONPATH`, invokes the installed console executable outside the source checkout, and verifies canonical receipt behavior for delegated execution, deterministic no-change evidence, policy refusal, stale-approval refusal, and malformed-approval terminal evidence.

The installed-distribution tests independently recompute the receipt SHA-256 digest, reject local project-path leakage in receipt JSON, and verify zero-write Git invariants for refusal/error cases.

## Explicit Non-Goals

AUTO-0012 does not add new workflows or write primitives, receipt-file application writes, replay/retry/resume, rollback authority, signatures/PKI/key management, remote logging, trusted timestamps, network identity, direct Git commit/tag/push authority, release/publication authority, force/stale bypass, policy grants, or approval expansion.

## Closure Semantics

AUTO-0012 is complete for deterministic execution receipts/evidence. Any later capability such as signed attestations, remote evidence services, replay/resume, or broader orchestration authority requires a separate design/contract and cannot be inferred from AUTO-0012.
