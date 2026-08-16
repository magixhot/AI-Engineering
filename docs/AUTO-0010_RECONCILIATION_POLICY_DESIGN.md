# AUTO-0010 — Reconciliation Policy Design

**Status:** DESIGN / NOT YET IMPLEMENTED

## Purpose

AUTO-0010 defines a deterministic policy layer that can restrict which already-supported reconciliation actions may proceed through AUTO-0008 and AUTO-0009 without creating any new mutation authority.

The policy layer exists to make automation safer and more explicit as orchestration becomes more capable. It is a gate, not an executor.

## Permanent Authority Boundaries

AUTO-0007 remains permanently read-only and owns deterministic reconciliation planning.

AUTO-0008 remains the sole guarded one-step apply authority and continues to own stale-plan validation, eligibility revalidation, delegated subsystem execution, and one-step result reporting.

AUTO-0009 remains the bounded multi-step orchestration layer and requires a fresh AUTO-0007 plan before each independently revalidated AUTO-0008 apply.

AUTO-0010 MUST NOT add a mutation primitive, bypass AUTO-0008, reorder AUTO-0007 canonical steps, or convert AUTO-0009 into an `apply all` shortcut.

## Policy Model

A reconciliation policy is a typed, deterministic set of constraints evaluated against a fresh reconciliation plan and the candidate next step.

The initial policy vocabulary may constrain only already-observable properties, including:

- maximum successful write count;
- allowed reconciliation workflow / step kinds already recognized by AUTO-0008;
- denied reconciliation workflow / step kinds already recognized by AUTO-0008;
- whether a run may proceed when the project Git working tree is dirty;
- whether a run may proceed when untracked files are present;
- whether a run may proceed when the repository is detached from a branch;
- whether a run may proceed when the project is outside an explicitly supplied project root.

The implementation MUST fail closed for unknown policy fields, unknown workflow identifiers, contradictory rules, malformed values, or policy data that cannot be evaluated deterministically.

## Default Behavior

Absence of an explicit policy preserves the existing verified AUTO-0008/AUTO-0009 behavior. AUTO-0010 must not silently make previously valid execution broader.

If an explicit policy is supplied, every candidate write MUST pass policy evaluation immediately before AUTO-0008 delegation.

A policy refusal is a zero-write terminal result for that candidate step. Earlier successful AUTO-0009 steps remain truthful partial progress; AUTO-0010 does not invent transaction rollback.

## Policy Source Boundary

The first implementation should support an explicit caller-provided policy file only. It MUST NOT discover or trust arbitrary policy files from parent directories, user home directories, environment variables, network locations, or repository remotes.

A later stage may define a conventional project-local policy path only through a separate design amendment.

The policy file format should be TOML because the repository already uses TOML for project metadata and Python tooling. Parsing MUST use bounded local file reads and reject duplicate/ambiguous semantic rules.

## Proposed Policy Shape

Illustrative only:

```toml
version = 1
max_steps = 4
allow_dirty_worktree = false
allow_untracked_files = false
require_attached_branch = true

allowed_workflows = [
  "documentation-sync",
  "python-engineering-v1-to-v2",
]
```

The exact workflow identifiers must come from existing AUTO-0008 authority mapping; AUTO-0010 MUST NOT invent aliases that widen scope.

## Evaluation Contract

For each candidate step, policy evaluation MUST:

1. operate on the same fresh project/reconciliation state used for the next orchestration decision;
2. resolve the candidate step to an already-known AUTO-0008 workflow identity;
3. validate policy syntax and semantic consistency before any write;
4. return a typed allow/refuse result with deterministic issue codes;
5. produce zero writes on refusal or policy error;
6. leave AUTO-0008 stale-plan and execution validation fully authoritative even after policy allows the step.

Policy allow means only "policy does not forbid this candidate." It is never sufficient authority to execute.

## Determinism

Given identical project bytes, Git state, reconciliation plan, candidate step, policy bytes, and installed capability set, policy evaluation MUST produce byte-for-byte equivalent machine-readable decisions apart from explicitly documented path-normalization fields.

Rule ordering in the policy file MUST NOT change the semantic decision.

## Git Safety

AUTO-0010 itself owns no Git mutation authority.

Policy evaluation may observe bounded Git state already available through approved repository services. It MUST NOT execute arbitrary Git commands, modify HEAD, branch, index, remotes, configuration, hooks, refs, or working-tree bytes.

A policy requiring a clean working tree must distinguish tracked modifications, staged changes, and untracked files when the existing Git observation layer provides those facts.

## Failure Semantics

Policy errors and policy refusals must be distinguishable:

- `policy_error` — invalid, unknown, contradictory, unreadable, or unsupported policy input;
- `policy_refused` — valid policy explicitly denies the candidate state or step;
- existing AUTO-0009 terminal states remain unchanged for conditions outside policy authority.

Neither state authorizes fallback to ungoverned execution.

## Proposed Public CLI Boundary

A later implementation stage may extend orchestration with:

```text
ai-engineering project reconcile run --project PATH --policy POLICY.toml
```

The existing `--max-steps` bound remains effective. If both CLI and policy specify a step limit, the effective limit MUST be the more restrictive value.

The CLI MUST NOT expose `--ignore-policy`, `--force-policy`, stale bypass, policy-defined arbitrary commands, dynamic plugins, network policy retrieval, publication authority, or direct Git mutation.

This design stage does not implement the command.

## Typed Evidence

Policy evaluation should produce typed evidence containing at minimum:

- policy version;
- normalized policy source identity;
- candidate step / existing workflow identity;
- allow/refuse/error state;
- deterministic issue code(s);
- effective progress limit when applicable;
- observed policy-relevant Git facts;
- no-write evidence on refusal/error.

AUTO-0009 orchestration results should retain the policy decision associated with each attempted or refused candidate step.

## Explicit Non-goals

AUTO-0010 does not authorize:

- new reconciliation workflows or migration edges;
- arbitrary file write rules;
- shell/Python command definitions in policy;
- policy scripts, expressions, templates, imports, or plugins;
- remote/network policy retrieval;
- cross-project fleet policy;
- interactive approval prompts;
- Git commit, branch, tag, push, release, TestPyPI, PyPI, or publication;
- bypass of AUTO-0007, AUTO-0008, or AUTO-0009 safety gates;
- global transaction or rollback guarantees.

## Verification Matrix

Implementation stages MUST verify at least:

- no-policy execution preserves existing AUTO-0009 behavior;
- valid allow policy permits only already-authorized workflows;
- valid deny policy stops before the denied candidate write;
- unknown fields and workflow identifiers fail closed;
- contradictory allow/deny rules fail closed;
- policy file mutation between plan and execution cannot bypass fresh evaluation;
- CLI and policy step limits resolve to the stricter bound;
- dirty/staged/untracked/detached Git rules are deterministic and zero-write on refusal;
- earlier successful orchestration steps remain reported when a later candidate is policy-refused;
- AUTO-0008 stale-plan checks still execute after policy allowance;
- Git HEAD/branch/index/remotes/config remain unchanged by policy evaluation;
- installed-wheel behavior is verified outside the source checkout;
- repeated identical runs produce deterministic decisions and issue ordering.

## Proposed Delivery Stages

1. **AUTO-0010-01 — Reconciliation Policy Design** — this document; no production capability.
2. **AUTO-0010-02 — Typed Policy Parser / Evaluator** — bounded TOML parsing and deterministic policy decisions; no CLI integration.
3. **AUTO-0010-03 — Safety / Determinism / Git Invariants** — tests for malformed policies, contradiction, Git-state rules, stale state, and no-write refusals.
4. **AUTO-0010-04 — Orchestration + Public CLI Integration** — optional `--policy` gate over AUTO-0009 without new authority.
5. **AUTO-0010-05 — Installed Distribution Verification** — wheel/install verification outside source checkout.
6. **AUTO-0010-06 — Final Evidence / Documentation Reconciliation** — authoritative closure after all preceding gates pass.

Stages MUST execute in order. Each stage requires its normal pre-merge Quality gate and exact post-merge Quality gate before the next stage begins.

## Definition of Done

AUTO-0010 is complete only when:

- policy can only restrict existing reconciliation authority, never widen it;
- invalid/unknown/contradictory policy fails closed with zero unauthorized writes;
- policy is freshly evaluated before every candidate mutation;
- AUTO-0007 remains read-only, AUTO-0008 remains sole one-step apply authority, and AUTO-0009 remains bounded replan-between-writes orchestration;
- Git safety and deterministic evidence are verified;
- public and installed-wheel behavior are verified;
- authoritative documentation matches the exact final verified master baseline.
