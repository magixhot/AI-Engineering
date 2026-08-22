# INFRA-0001 — Local Coding Agent Integration

## Purpose

Define the authority, runtime, verification, escalation, cost, and rollback
contract for using OpenCode and local models as a bounded coding-agent layer in
AI-Engineering.

INFRA-0001-01 is design-only. It does not install or upgrade OpenCode, select or
download a local model, add repository-wide write authority, change GitHub
permissions, modify Quality, alter branch protection, create a merge path,
change credentials, or authorize publication/release actions.

The intent is local-first execution for work that is cheap, bounded, and
deterministically verifiable while preserving the repository governance and
Quality boundaries already established by AUTO and REL milestones.

## Verified Baseline

This design starts from exact `master`
`0c003035f3c507de95ef0d0f80c2507ee918396e`.

The repository already contains a bounded OpenCode surface:

```text
.opencode/agents/auto-0013-readonly.md
```

AUTO-0013 through AUTO-0019 define a separate read-only GitHub/OpenCode control
plane for `status`, `inspect`, `plan`, `diff`, and `quality_verify` request
classes. INFRA-0001 must not silently broaden, replace, or reinterpret that
control plane.

The new INFRA namespace instead defines local interactive/automation roles for
repository work. Any overlap with existing AUTO control behavior must remain at
least as restrictive as the existing authority contract.

## Governance Principle

Local-first is an execution preference, not an authority preference.

OpenCode and any local model are subordinate execution backends. They receive
only explicitly granted capabilities and may not derive additional authority
from task wording, model confidence, repository state, or tool availability.

The authority chain remains:

```text
human approval / approved roadmap
  -> repository governance and milestone contracts
  -> bounded execution backend (OpenCode or Codex)
  -> deterministic verification / Quality
  -> separately controlled merge or release authority
```

Neither OpenCode nor Codex is a merge authority merely because it can prepare
changes or run verification.

## Planned Repository Layer

The target repository layer is:

```text
AI-Engineering/
├── AGENTS.md
├── opencode.json
├── .opencode/
│   ├── agents/
│   │   ├── auto-0013-readonly.md
│   │   ├── repo-reader.md
│   │   ├── implementer.md
│   │   └── verifier.md
│   └── commands/
├── scripts/
│   ├── local-agent-check.ps1
│   └── local-agent-check.sh
└── ...
```

This is a target shape, not authority granted by this design stage. Existing
files remain authoritative until later implementation stages explicitly add or
change the listed surfaces.

`AGENTS.md` is intended to become the repository-level agent contract.
OpenCode-specific configuration must implement a subset of that contract, not
form a competing governance layer.

## Agent Roles

### repo-reader

`repo-reader` is read-only.

It may be allowed to:

- inspect repository files except explicitly denied sensitive paths;
- inspect documentation;
- list and grep repository content;
- inspect branch, exact HEAD, status, log, and diff through an explicit command
  allowlist;
- report evidence and uncertainty.

It must not:

- edit, create, move, rename, or delete repository files;
- modify Git state;
- access external directories unless a later stage explicitly authorizes a
  specific path;
- read credentials, tokens, environment-secret files, or unrelated workstation
  information;
- invoke mutation indirectly through scripts or subprocesses.

The existing `auto-0013-readonly.md` remains a valid narrower baseline and must
not be weakened by introducing `repo-reader`.

### implementer

`implementer` may modify the working tree only within an explicitly approved
task scope.

A future implementation may allow it to:

- perform repository inspection;
- edit or create files inside the approved scope;
- run explicitly approved deterministic development commands;
- inspect Git state and the resulting diff;
- prepare evidence for review.

It must not be allowed to:

- merge;
- force-push;
- push a protected branch;
- change branch protection;
- bypass, disable, weaken, or suppress Quality;
- reinterpret a failing Quality result as success;
- modify authority rules as part of an ordinary implementation task;
- expand its own permissions;
- retrieve or use credentials outside an explicitly approved integration
  boundary;
- perform release, publication, signing, credential, or deployment actions.

Write authority must be path/scope bounded where practical. A future agent
configuration must prefer explicit allowlists over broad shell access.

### verifier

`verifier` is read-only with respect to the repository and Git state.

A future implementation may allow it to run deterministic checks and read the
artifacts required to evaluate them.

It must report at minimum:

```text
branch
exact HEAD
dirty/clean worktree state
commands executed
exit codes
bounded check results
PASS / FAIL / BLOCKED
```

It must not:

- edit repository files;
- repair failures;
- mutate Git state;
- push, merge, label, approve, or otherwise alter GitHub state;
- conceal failed checks;
- convert non-deterministic or incomplete evidence into PASS.

Implementation and verification should remain separable so that verifier
results can be independently reproduced.

## Command Authority

OpenCode must not receive unrestricted shell authority by default.

Later implementation must define command classes and explicit allowlists. The
minimum policy is deny-by-default with narrowly enumerated commands for each
role.

Read-only Git examples may include forms equivalent to:

```text
git --no-optional-locks status
git branch
git rev-parse HEAD
git log ...
git diff ...
git grep ...
```

Mutation-capable commands require separate review and must be limited to the
minimum needed for the approved role. Shell patterns that enable arbitrary
command composition, indirect execution, or privilege escalation must not be
introduced merely for convenience.

## Local Runtime and Provider Boundary

INFRA-0001 does not preselect a local-model provider.

A later inventory stage must record:

- OpenCode version and installation/runtime mode;
- Windows and/or WSL execution boundary;
- provider and model candidates;
- local resource requirements;
- context-window and tool-calling capabilities;
- structured-output behavior where required;
- offline/local assumptions and any network use;
- reproducible startup/configuration method;
- model fallback behavior.

A model/provider is not acceptable solely because it can complete a sample
edit. It must fit the command, authority, evidence, and failure contracts in
this design.

## GitHub Interaction Boundary

Local coding-agent integration does not automatically grant GitHub write
access.

Read access may be introduced later when needed for bounded issue/PR context.
Any GitHub mutation must be separately enumerated and reviewed.

The following remain forbidden without later explicit authority:

- merging a PR;
- pushing protected branches;
- modifying branch protection or repository settings;
- altering required checks;
- dismissing or bypassing failed Quality;
- creating releases/tags/publication artifacts;
- changing secrets or credentials.

The pre-existing AUTO-0013 through AUTO-0019 GitHub control plane remains a
separate contract and is not implicitly converted into a general coding-agent
write channel.

## Deterministic Local Verification

Later implementation must add a deterministic local guard/check surface, with
Windows and WSL/Linux entry points when both environments are supported.

The check must be able to establish, as applicable:

- current branch and exact HEAD;
- worktree cleanliness before and after a role run;
- changed paths versus approved scope;
- forbidden-path mutations;
- presence of authority/configuration drift;
- execution of the required deterministic lint/type/test subset;
- exact exit status and bounded evidence.

`local-agent-check` is a guard and evidence producer. It is not a replacement
for repository Quality unless a later milestone explicitly changes the Quality
contract.

## Codex Escalation Policy

OpenCode/local models should absorb bounded work for which a deterministic
verification path exists.

Expected local-first classes include:

```text
repository grep / inventory
document inspection
bounded mechanical edits
small scope-constrained implementation
format/lint/type/unit checks
repeatable evidence collection
```

Escalation to Codex is required when the task depends materially on:

```text
architectural ambiguity
authority interpretation
roadmap or milestone selection
security-sensitive changes
unclear or non-deterministic failures
cross-cutting design with uncertain blast radius
local-model/tool failure or incomplete evidence
review requiring stronger reasoning than the approved local profile provides
```

A local agent must return `ESCALATE` or an equivalent bounded terminal result
rather than improvise beyond its authority.

## Token and Cost Reduction Policy

The cost objective is to reduce expensive model usage without reducing
verification quality or repository governance.

Cost reduction must therefore come from routing appropriate work locally, not
from skipping required reasoning, tests, review, Quality, or evidence.

A later implementation should measure at least:

- task class;
- local versus escalated execution;
- number of failed/retried local attempts;
- deterministic verification outcome;
- approximate external-model usage avoided where observable;
- cases where local execution increased rather than reduced total work.

No cost target may justify weakening an authority or Quality boundary.

## Failure Contract

Local-agent failure states must be explicit. At minimum the implementation must
support distinctions equivalent to:

- `PASS` — requested bounded work completed and required deterministic evidence
  passed;
- `FAIL` — requested bounded work or a required check failed;
- `BLOCKED` — precondition, environment, permission, or evidence requirement
  prevents execution;
- `ESCALATE` — task exceeds the approved local role/model boundary.

A failure must not trigger hidden repair, replay, permission expansion, or
fallback mutation.

## Rollback

The integration must be removable without changing repository semantics or the
existing AUTO/REL/Quality authority model.

A future enablement stage must prove that OpenCode/local-agent execution can be
disabled by removing or disabling the integration configuration while leaving:

- source behavior;
- tests;
- Quality;
- canonical project-state validation;
- release governance;
- protected-branch rules;
- existing AUTO control contracts

functionally intact.

Rollback must not require rewriting project history or relaxing verification.

## Delivery Stages

1. `INFRA-0001-01` — design-only authority/runtime/verification/escalation/cost/
   rollback contract.
2. `INFRA-0001-02` — exact OpenCode/runtime/provider inventory and provider
   decision; no generalized write authority.
3. `INFRA-0001-03` — repository agent layer: `AGENTS.md`, `opencode.json`,
   bounded role configurations, and command definitions.
4. `INFRA-0001-04` — deterministic local-agent guard/check implementation and
   failure coverage.
5. `INFRA-0001-05` — constrained GitHub interaction contract/implementation if
   still required by the evidence; no merge or protected-branch authority.
6. `INFRA-0001-06` — Codex escalation and cost-routing policy implementation
   with evidence.
7. `INFRA-0001-07` — shadow validation on representative repository tasks,
   comparing local execution against existing deterministic gates.
8. `INFRA-0001-08` — bounded enablement and rollback verification.

Every repository-writing implementation stage remains separately approval
gated. Where a stage changes executable repository behavior, exact PR-head
Quality and exact push-triggered post-merge Quality remain required.

## Namespace and Roadmap Boundary

INFRA is a separate governance namespace. INFRA-0001 does not fabricate
`AUTO-0023`, modify the schema-v2 canonical AUTO project-state representation,
or change the current REL-0004 release-governance state.

REL-0004-03 through REL-0004-06 remain separately approval-gated. INFRA work
must not silently become part of a release candidate merely because it lands in
`master`; candidate scope and release readiness remain governed by REL.

## INFRA-0001-01 Completion Rule

INFRA-0001-01 is complete only when this design passes exact PR-head Quality,
expected-head-protected merge, and exact push-triggered post-merge Quality.

Completion of the design authorizes no INFRA-0001-02 runtime/provider decision,
installation, model download, agent-role implementation, GitHub write access,
Quality change, or release action.
