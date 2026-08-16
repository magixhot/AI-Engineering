# AUTO-0003 CLI Verification

Status: ACTIVE

## Scope

AUTO-0003-04 exposes documentation ownership initialization as a dedicated CLI boundary:

`ai-engineering project docs ownership check|plan|apply --project <path>`

The ownership CLI remains separate from AUTO-0002 `project docs check|plan|apply` so that synchronization and ownership initialization keep distinct safety semantics.

## Verification Requirements

- ownership `check` and `plan` are read-only;
- deterministic planning output is preserved;
- manual-review states fail closed;
- ownership `apply` preserves human-authored content and Git HEAD/index invariants;
- successful apply hands the initialized documents directly to AUTO-0002 with zero remaining drift;
- repeated ownership apply is idempotent;
- the console entry point is verified from an isolated wheel installation rather than only from the source checkout.

## Explicit Exclusions

This task does not change project versioning, release tags, GitHub Releases, PyPI publication, MCP protocol behavior, or the approved AUTO-0003 ownership design contract.
