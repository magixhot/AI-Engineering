# INFRA-0001-06 — Local-first routing and Codex escalation

## Purpose

Implement the local-first routing policy defined by INFRA-0001 without adding
hidden cloud fallback, GitHub authority, merge authority, or automatic Codex
execution.

This stage starts from verified `master`
`f8e8b0f8168153f73ccae20b9500c930bb71c954` after INFRA-0001-04.
INFRA-0001-05 was audited and found not required by current evidence; the local
coding-agent roles continue to have no general GitHub interaction surface.

## Routing contract

The deterministic decision order is:

```text
high-risk / authority-sensitive / architectural / non-deterministic
  -> CODEX_ESCALATE

bounded + deterministic + local runtime available
  -> LOCAL

local FAIL/BLOCKED or local unavailable
  + explicit external-fallback approval
  + exact external model identity
  -> EXTERNAL_EXPLICIT

local FAIL/BLOCKED or local unavailable
  without explicit external approval
  -> BLOCKED

local agent explicitly returns ESCALATE
  -> CODEX_ESCALATE
```

`CODEX_ESCALATE` is a handoff signal only. It does not authorize or invoke
Codex. The higher-level human/governed workflow remains responsible for the
actual escalation.

`EXTERNAL_EXPLICIT` similarly authorizes no hidden replay. It is returned only
when the request already contains explicit fallback approval and an exact model
identity. The router itself still does not execute that model.

## Why routing is deterministic

The router consumes explicit evidence rather than asking a model which model
should run. Its inputs are limited to:

- task class;
- whether deterministic verification exists;
- whether the local runtime is available;
- the terminal state of a prior local attempt, if any;
- whether external fallback was explicitly approved;
- the exact external model identity, when approved.

The output is a stable JSON-compatible decision containing the route, reason,
local-first evidence, and booleans showing whether external/Codex execution is
authorized by this decision.

Codex execution is never authorized by the router. A `CODEX_ESCALATE` result
requires a separate higher-level handoff.

## Task classes

Local-first candidates:

- `inspection`
- `mechanical_edit`
- `bounded_implementation`
- `verification`

Direct Codex-escalation classes:

- `architecture`
- `authority`
- `security`
- `nondeterministic_failure`

Write-capable local task classes additionally require a deterministic
verification path. Without one they produce `CODEX_ESCALATE` rather than
letting a local model improvise.

## Local failure and replay rule

A local `FAIL` or `BLOCKED` does not automatically cause another model call.
Without explicit external fallback approval the terminal routing result is
`BLOCKED`.

If a local model returns `ESCALATE`, the router produces `CODEX_ESCALATE`
directly. An already-approved external fallback does not override a model's
explicit statement that the task exceeds its reasoning boundary.

This preserves the existing INFRA failure contract: no hidden replay,
permission expansion, or automatic cloud fallback after terminal failure.

## Command surface

The router can be inspected without executing a model:

```bash
uv run python -m ai_engineering.local_agent_routing \
  --task-class inspection \
  --deterministic-verification
```

Example bounded external decision after an explicitly approved fallback:

```bash
uv run python -m ai_engineering.local_agent_routing \
  --task-class verification \
  --deterministic-verification \
  --local-state blocked \
  --external-fallback-approved \
  --external-model opencode/mimo-v2.5-free
```

The module performs no network access and no repository mutation.

## Cost objective

The routing policy reduces expensive-model use by making `LOCAL` the default
for bounded deterministic tasks while reserving stronger-model handoff for
classes whose evidence requires it. Cost reduction never overrides authority,
verification, or failure boundaries.

INFRA-0001-07 will provide representative shadow evidence comparing this policy
and local execution against existing deterministic gates. That future stage is
not authorized by completion of INFRA-0001-06.

## Portability boundary

The repository remains the canonical source of routing policy. Workstation
bootstrap and fresh-machine reproducibility are mandatory INFRA-0001 completion
requirements, but they remain part of the later enablement/rollback work rather
than this routing stage.

## Completion rule

INFRA-0001-06 completes only after exact PR-head Quality success,
expected-head-protected merge, and exact push-triggered post-merge Quality on
the resulting `master`.
