# AUTO-0017 — Project State / Roadmap Reconciliation Design

Status: DESIGN / PENDING GATE

## Purpose

Reconcile the repository's canonical project-state documentation with the verified engineering state that exists on exact `master` after AUTO-0016.

This milestone is documentation-first and read-only in authority. It does not add runtime behavior, mutation authority, workflow authority, service-control authority, publication scope, or new remote task classes.

## Fresh roadmap audit finding

The audit was performed against exact master:

```text
445c080fad5ac89653f89414893e99ded207f841
```

The implementation/evidence history is ahead of the canonical state documents:

- AUTO-0014 is no longer active; its lifecycle work was completed and reconciled.
- AUTO-0015 exact post-merge Quality verification was delivered and verified.
- AUTO-0016 workstation bootstrap/doctor and the bounded read-only Quality relay were delivered and verified.
- `docs/ROADMAP.md` still describes AUTO-0014-06 as active and describes the exact post-merge verifier as only a future milestone.
- `docs/PROJECT_CONTEXT.md` still describes the current engineering baseline as post-AUTO-0003 and omits the later AUTO architecture and verified control-plane/workstation capabilities.

Therefore the next safest milestone is not a new execution feature. The repository first needs a canonical project-state reconciliation so future milestone selection is based on the state that actually exists.

## Scope

AUTO-0017 will reconcile documentation only.

In scope:

1. Update `docs/ROADMAP.md` to reflect completed/verified milestones through AUTO-0016.
2. Update `docs/PROJECT_CONTEXT.md` so the current architecture and engineering baseline reflect the verified repository state without rewriting immutable release history.
3. Reconcile any directly conflicting current-priority/current-milestone statements in other canonical start/context documents when necessary.
4. Preserve exact historical evidence and authority boundaries.
5. Perform a post-reconciliation roadmap audit and select the next milestone explicitly rather than implicitly expanding an earlier scope.

Out of scope:

- runtime or CLI behavior changes;
- new AUTO task classes;
- repository write/apply execution authority;
- workflow rerun/cancel/dispatch authority;
- new merge/ref mutation authority;
- OpenCode lifecycle control;
- worker lifecycle mutation;
- package installation or workstation repair;
- credential/authentication mutation;
- deployment, release, publication, or PyPI scope;
- retroactive changes to immutable release boundaries.

## Reconciliation rules

### Evidence over stale narrative

Canonical current-state documents must match exact verified repository evidence. Historical statements remain historical, but they must not be presented as the current state when later verified milestones supersede them.

### Preserve immutable release history

The existing published release boundary remains historical fact. AUTO milestones implemented later on `master` are not retroactively inserted into an immutable prior release.

### Preserve authority layering

The reconciliation must keep the established boundaries explicit:

- AUTO-0007 remains the permanent read-only reconciliation planner.
- AUTO-0008 remains the guarded one-step apply boundary.
- AUTO-0009 remains bounded multi-step orchestration.
- AUTO-0010 remains the restrictive policy gate.
- AUTO-0011 remains the optional explicit single-candidate approval gate.
- AUTO-0012 remains deterministic execution receipts/evidence.
- AUTO-0013 remains bounded remote read-only inspection/control transport.
- AUTO-0014 remains local worker lifecycle supervision without expanding task authority.
- AUTO-0015 remains exact post-merge Quality verification without workflow mutation authority.
- AUTO-0016 remains workstation bootstrap/doctor plus the narrow read-only Quality relay, with no hidden repair or service-control authority.

### Public-safety boundary

Reconciled public documents must not publish workstation-local usernames, absolute private paths, credentials, tokens, private environment values, or unrelated local-machine metadata.

## Proposed delivery stages

1. AUTO-0017-01 — Design / Contract.
2. AUTO-0017-02 — Canonical Roadmap Reconciliation.
3. AUTO-0017-03 — Project Context / Start-State Reconciliation.
4. AUTO-0017-04 — Cross-Document Consistency Audit.
5. AUTO-0017-05 — Final Evidence / Next-Milestone Selection.

Each stage follows the normal repository gate: exact pre-merge Quality success, merge with expected-head protection, and exact post-merge push Quality verification through the existing read-only relay.

## Completion rule

AUTO-0017 is complete only when the canonical current-state documentation agrees with the verified repository state through AUTO-0016, conflicting current-priority statements are reconciled, public/private boundaries remain intact, and a fresh post-reconciliation roadmap audit selects the next milestone from the corrected state.
