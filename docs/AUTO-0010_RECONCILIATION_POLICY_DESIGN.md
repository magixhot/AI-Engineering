# AUTO-0010 — Reconciliation Policy Design

**Status:** COMPLETE / VERIFIED

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

The implemented policy vocabulary may constrain only already-observable properties:

- maximum successful write count;
- allowed reconciliation workflow / step kinds already recognized by AUTO-0008;
- denied reconciliation workflow / step kinds already recognized by AUTO-0008;
- whether a run may proceed when the project Git working tree is dirty;
- whether a run may proceed when untracked files are present;
- whether a run may proceed when the repository is detached from a branch;
- whether a run may proceed when the project is outside an explicitly supplied project root.

The implementation fails closed for unknown policy fields, unknown workflow identifiers, contradictory rules, malformed values, or policy data that cannot be evaluated deterministically.

## Default Behavior

Absence of an explicit policy preserves the verified AUTO-0008/AUTO-0009 behavior.

If an explicit policy is supplied, every candidate write must pass policy evaluation immediately before AUTO-0008 delegation.

A policy refusal is a zero-write terminal result for that candidate step. Earlier successful AUTO-0009 steps remain truthful partial progress; AUTO-0010 does not invent transaction rollback.

## Policy Source Boundary

The implementation supports an explicit caller-provided local TOML policy file only. It does not discover or trust arbitrary policy files from parent directories, user home directories, environment variables, network locations, or repository remotes.

## Implemented Policy Shape

```toml
version = 1
max_steps = 4
allow_dirty_worktree = false
allow_untracked_files = false
require_attached_branch = true
require_project_root_match = true

allowed_workflows = [
  "documentation-sync",
  "python-engineering-v1-to-v2",
]
```

Workflow identifiers come from existing AUTO-0008 authority mapping; AUTO-0010 does not invent aliases that widen scope.

## Evaluation Contract

For each candidate step, policy evaluation:

1. operates on fresh reconciliation/Git state for the next orchestration decision;
2. resolves the candidate to an already-known AUTO-0008 workflow identity;
3. validates policy syntax and semantic consistency before any write;
4. returns a typed allow/refuse/error result with deterministic issue codes;
5. produces zero writes on refusal or policy error;
6. leaves AUTO-0008 stale-plan and execution validation fully authoritative even after policy allows the step.

Policy allow means only "policy does not forbid this candidate." It is never sufficient authority to execute.

## Determinism and Git Safety

Given identical project bytes, Git state, candidate step, policy bytes, and installed capability set, policy evaluation is deterministic. Rule ordering does not change the semantic decision.

AUTO-0010 owns no Git mutation authority. Policy evaluation observes approved Git readiness evidence and does not modify HEAD, branch, index, remotes, configuration, hooks, refs, or working-tree bytes.

## Failure Semantics

Policy errors and policy refusals are distinct:

- `policy_error` — invalid, unknown, contradictory, unreadable, or unsupported policy input;
- `policy_refused` — valid policy explicitly denies the candidate state or step;
- existing AUTO-0009 terminal states remain authoritative for conditions outside policy authority.

Neither state authorizes fallback to ungoverned execution.

## Public CLI Boundary

```text
ai-engineering project reconcile run --project PATH --policy POLICY.toml [--max-steps N]
```

The existing `--max-steps` bound remains effective. If both CLI and policy specify a step limit, the effective limit is the more restrictive value.

The CLI exposes no `--ignore-policy`, `--force-policy`, stale bypass, policy-defined arbitrary commands, dynamic plugins, network policy retrieval, publication authority, or direct Git mutation.

## Typed Evidence

Policy decisions retain policy source identity, candidate workflow, allow/refuse/error state, deterministic issue codes, effective progress limit, and observed policy-relevant Git facts. AUTO-0009 orchestration results retain the decision associated with each evaluated candidate.

## Explicit Non-goals

AUTO-0010 does not authorize new reconciliation workflows or migration edges, arbitrary file write rules, shell/Python command definitions, scripts/expressions/templates/imports/plugins, remote/network policy retrieval, cross-project fleet policy, interactive approval prompts, Git commit/branch/tag/push/release/publication, bypass of AUTO-0007/AUTO-0008/AUTO-0009 safety gates, or global transaction/rollback guarantees.

## Delivery Evidence

1. **AUTO-0010-01 — Reconciliation Policy Design** — PR #106; Quality #207; post-merge #208.
2. **AUTO-0010-02 — Typed Policy Parser / Evaluator** — PR #107; corrected Quality #211; post-merge #212.
3. **AUTO-0010-03 — Safety / Determinism / Git Invariants** — PR #108; corrected Quality #214; post-merge #215.
4. **AUTO-0010-04 — Orchestration + Public CLI Integration** — PR #109; corrected Quality #220; post-merge #221.
5. **AUTO-0010-05 — Installed Distribution Verification** — PR #110; Quality #222; post-merge #223.
6. **AUTO-0010-06 — Final Evidence / Documentation Reconciliation** — PR #111; Quality #224; post-merge #225.

Final verified AUTO-0010 baseline:

```text
master = 1abd853da67cfb3954baa04f310837388b60b4f8
```

## Definition of Done

AUTO-0010 is COMPLETE / VERIFIED: policy remains restriction-only, invalid/unknown/contradictory policy fails closed, policy is freshly evaluated before candidate mutation, AUTO-0007/AUTO-0008/AUTO-0009 authority boundaries remain intact, Git safety/determinism and installed-wheel behavior are verified, and AUTO-0010-06 passed pre-merge Quality #224 plus exact post-merge Quality #225 on the final master baseline.
