# AUTO-0002-04 — CLI and Installed-Distribution Verification

**Status:** CONTRACT / APPROVED FOR IMPLEMENTATION
**Parent:** AUTO-0002 — Project Documentation Synchronization

## Purpose

Freeze the exact V1 CLI contract required by AUTO-0002 before implementation of the CLI adapter.

The CLI is an adapter over the existing public inspection, drift, planning, and guarded-apply APIs.
It must not duplicate synchronization logic.

## Command Surface

AUTO-0002 V1 adds exactly these installed commands:

```text
ai-engineering project docs check --project PATH
ai-engineering project docs plan --project PATH
ai-engineering project docs apply --project PATH
```

`--project PATH` is required for every command and resolves to an absolute local project root before
calling the public API.

No aliases, interactive prompts, JSON mode, network mode, Git options, or implicit current-directory
mode are included in V1.

## Check Contract

`project docs check` is read-only.

It performs project inspection followed by drift detection and prints deterministic `key=value`
stdout in this order:

```text
project=<resolved absolute project root>
drift_count=<integer>
manual_review_count=<integer>
drift=<document>:<category>
...
status=<clean|drift>
```

`drift=` lines are emitted in the deterministic report order and are omitted when there is no drift.

Exit codes:

- `0` — check completed and no drift exists;
- `1` — check completed and drift exists, or an expected domain/operational failure occurred;
- `2` — argparse usage error;
- `3` — unexpected internal failure.

Detected drift is normal stdout evidence, not stderr. Expected domain failures use stderr with no
success/status output.

## Plan Contract

`project docs plan` is read-only.

It performs inspection, drift detection, and deterministic planning. It prints:

```text
project=<resolved absolute project root>
update_count=<integer>
manual_review_count=<integer>
update=<document>:<original_sha256>
...
status=<clean|ready|manual_review>
```

`update=` lines follow the deterministic plan order and never include replacement Markdown content.
The SHA-256 value is the digest already stored in the public plan object.

Status meanings:

- `clean` — no drift and no updates;
- `ready` — one or more deterministic updates exist and no manual-review item exists;
- `manual_review` — at least one `manual_review_required` item exists.

Exit codes:

- `0` — plan completed with `clean` or `ready` status;
- `1` — plan completed with `manual_review`, or an expected domain/operational failure occurred;
- `2` — argparse usage error;
- `3` — unexpected internal failure.

A manual-review result may still contain deterministic updates for other documents, but the CLI does
not mutate anything in `plan` mode.

## Apply Contract

`project docs apply` is the only mutating AUTO-0002 CLI command.

It performs a fresh inspection, drift detection, and plan creation in-process. Before calling the
public guarded apply API, it rejects the operation if any `manual_review_required` item exists. This
prevents a CLI invocation from silently applying only a subset of documents when another V1 document
requires human review.

On success it prints:

```text
project=<resolved absolute project root>
changed_count=<integer>
changed_document=<document>
...
verification=passed
```

`changed_document=` lines follow the result order. A clean project produces `changed_count=0`, no
`changed_document=` lines, and `verification=passed`.

Exit codes:

- `0` — guarded apply and post-apply verification succeeded, including the no-op clean case;
- `1` — manual review is required or another expected domain/operational failure occurred;
- `2` — argparse usage error;
- `3` — unexpected internal failure.

Expected errors are written to stderr and must not emit `verification=passed`.

## Manual-Review Boundary

Missing or malformed ownership markers remain a controlled manual-review condition. V1 does not add
an initialization or marker-insertion command.

Therefore an AUTO-0001-generated project that has never adopted AUTO-0002 ownership markers may be
successfully inspected, but `check` reports drift/manual review, `plan` reports manual review, and
`apply` refuses mutation.

Marker initialization remains a separate future design decision.

## Safety Boundary

The CLI must preserve all AUTO-0002 V1 constraints:

- writable documents remain exactly `CURRENT_STATUS.md`, `MASTER_INDEX.md`, and `PROJECT_MAP.md`;
- `check` and `plan` perform no writes;
- `apply` delegates writes to `apply_documentation_sync()`;
- SHA-256 stale-plan protection remains enforced by the public apply API;
- human-owned content outside markers remains protected;
- no Git stage, commit, branch, push, pull, remote, or GitHub action is performed;
- no project code is executed;
- no dependencies are installed;
- no network access is required by AUTO-0002 itself.

## Installed-Distribution Verification

The existing REL-0001 isolated-wheel release test must be extended to prove that the installed
console script exposes `project docs` and that installed-wheel behavior does not rely on the source
checkout or `PYTHONPATH`.

Required evidence:

1. installed `ai-engineering project --help` lists `docs`;
2. installed `ai-engineering project docs --help` lists `check`, `plan`, and `apply`;
3. installed `check` reports manual review for a bootstrap project without ownership markers;
4. an isolated local fixture with valid ownership markers produces a deterministic ready plan;
5. installed `apply` updates only the three approved documents and reports `verification=passed`;
6. a subsequent installed `check` reports `status=clean`;
7. the fixture Git HEAD is unchanged by synchronization and no Git staging/commit/push behavior is introduced.

## Completion Criteria

AUTO-0002-04 is complete only when the CLI adapter, unit tests, isolated installed-wheel evidence,
repository quality gates, and status documentation all match this frozen contract.
