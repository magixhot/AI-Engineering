# AUTO-0003-04 CLI Contract

Status: FROZEN FOR REVIEW

## Command Surface

`ai-engineering project docs ownership check --project <path>`

`ai-engineering project docs ownership plan --project <path>`

`ai-engineering project docs ownership apply --project <path>`

## Semantics

- `check` is read-only and returns success only when all eligible documents are already initialized.
- `plan` is read-only, deterministic, returns success for an initialization-ready plan, and returns failure when manual review is required.
- `apply` delegates to the guarded AUTO-0003 apply boundary and therefore refuses manual-review states, stale plans, invalid ownership states, or unsafe mutations.
- successful `apply` verifies AUTO-0002 handoff and AUTO-0003 idempotency before returning success.
- no ownership command stages, commits, pushes, tags, publishes, or otherwise mutates Git metadata.

## Output Contract

Output uses stable `key=value` records so humans, shell scripts, and tests can inspect project root, counts, document states, digests, changed documents, status, and verification outcome without parsing prose.

## Separation From AUTO-0002

AUTO-0003 ownership initialization is deliberately nested below `project docs ownership`. Existing AUTO-0002 commands remain `project docs check|plan|apply`; they do not silently initialize missing ownership markers.
