# INFRA-0001-07 — Shadow validation

## Purpose

Validate the local-first agent layer on representative repository tasks without
expanding authority, enabling automatic cloud fallback, or treating mocked
execution as evidence that the workstation-local LLM actually works.

This stage starts from verified `master`
`781fd6dbdef870386cab5d78cc4a086cf09a6c6b` after INFRA-0001-06.

## Validation layers

INFRA-0001-07 deliberately separates two evidence layers.

### Repository layer

Quality validates the deterministic shadow harness, routing expectations,
evidence schema, and fail-closed behavior. This layer may use unit tests, but it
must not claim that a mocked OpenCode/Ollama process proves real local-model
capability.

### Workstation layer

At least one real workstation shadow run must use the approved local profile
`ollama/qwen3:4b` through the governed OpenCode roles. The observation must be
validated by the repository harness before this stage can be considered fully
verified.

No workstation shadow task may merge, push, change GitHub state, alter
credentials, expand permissions, or perform release/publication actions.

## Representative cases

The initial representative set is intentionally small and deterministic:

1. `inspect-head` — `repo-reader` reports branch and exact HEAD.
2. `inspect-agent-contract` — `repo-reader` reads `AGENTS.md` and reports the
   four terminal outcomes.
3. `verify-routing-tests` — `verifier` runs the bounded routing test file and
   reports deterministic evidence.

All three are expected to route `LOCAL` under the INFRA-0001-06 production
routing policy.

The cases exercise repository inspection, governance-document inspection, and
deterministic verification without granting write authority.

## Workstation evidence contract

For every representative case the evidence records:

- exact `case_id`;
- exact model identity;
- role;
- terminal state;
- clean repository before the run;
- clean repository after the run;
- unchanged HEAD;
- deterministic check result.

The accepted model for this stage is exactly `ollama/qwen3:4b`.

The validator fails closed on missing or duplicate cases, unknown cases, wrong
model identity, wrong role, non-`PASS` result, dirty repository state, HEAD
mutation, or failed deterministic check.

## Commands

List the canonical representative cases:

```bash
uv run python -m ai_engineering.local_agent_shadow --list-cases
```

A workstation run should collect one JSON observation for each listed case and
then validate the evidence:

```bash
uv run python -m ai_engineering.local_agent_shadow \
  --evidence /path/to/shadow-evidence.json
```

A valid observation set returns exit code `0` and:

```json
{"issues": [], "valid": true}
```

The evidence file is an observation artifact. It must not contain secrets,
tokens, credentials, prompts containing sensitive workstation data, or broad
filesystem captures.

## Comparison boundary

The shadow result is accepted only when the local-agent observation agrees with
existing deterministic repository evidence. Local model confidence is never a
substitute for Git state, exact HEAD, bounded test results, or Quality.

A local failure, mutation, incomplete observation, or routing drift is evidence
against enablement and must remain visible as `FAIL`, `BLOCKED`, or escalation;
it must not trigger hidden replay or permission expansion.

## Cost evidence

This stage establishes qualitative cost evidence: each representative task that
completes locally with deterministic PASS demonstrates a task class that need
not consume Codex execution for routine handling. No invented token count or
monetary saving is recorded when the runtime cannot measure it directly.

## Portability boundary

Shadow validation is not the fresh-machine portability proof. The separate
INFRA-0001 completion requirement remains: repository-driven bootstrap and
verification must allow a new workstation to reach a governed OpenCode + local
LLM ready state. That belongs to INFRA-0001-08 enablement/rollback verification.

## Completion rule

Repository implementation requires exact PR-head Quality success,
expected-head-protected merge, and exact push-triggered post-merge Quality.

INFRA-0001-07 is not `COMPLETE / VERIFIED` from CI alone. After those gates,
at least one real workstation observation set covering all canonical cases must
validate successfully with the approved local model. Completion does not
authorize INFRA-0001-08.
