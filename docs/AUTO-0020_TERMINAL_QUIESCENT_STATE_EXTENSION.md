# AUTO-0020 — Terminal Quiescent State Extension

## Decision

After the verified AUTO-0020-06 audit, option 1 was explicitly approved:
represent a completed milestone with no approved successor without fabricating
AUTO-0021.

The exact input baseline is `master`
`143ccdcbd9b39e89188cbad63577b0dc1e353941`, verified by pre-merge Quality
#405 and push-triggered Quality #406 (run id `32493445761`).

## Schema v2 Contract

Schema v2 adds one lifecycle value:

```json
{
  "schema_version": 2,
  "completed_through": "AUTO-0020",
  "active_milestone": null,
  "active_stage": null,
  "active_state": "QUIESCENT"
}
```

`QUIESCENT` means:

- every milestone through `completed_through` is complete for its approved
  scope;
- no successor milestone is approved or active;
- no active stage exists;
- the state grants no execution, mutation, publication, or deployment
  authority.

The parser accepts `QUIESCENT` only for schema v2 and only when both active
identity fields are JSON `null`. Non-null active identity in a quiescent state
fails closed.

## Compatibility

Schema v1 active manifests remain accepted with their original rules:

- `active_milestone` must be exactly `completed_through + 1`;
- `active_stage` must belong to that milestone;
- the lifecycle value must be one of the existing active states.

Schema v2 also accepts active state using the same rules. It does not weaken
validation, infer a successor, or accept unknown lifecycle values.

## Coherence Projection

The six canonical document projections remain unchanged. Fields projected from
a quiescent manifest carry JSON `null` for `active_milestone` and
`active_stage`, plus `"QUIESCENT"` for `active_state`. Missing, stale,
invented, or non-null successor claims fail with the existing bounded
diagnostics.

## Boundaries

This extension does not start AUTO-0021 and does not add:

- repository/document repair or automatic editing;
- remote write/apply task classes;
- workflow mutation;
- service or credential mutation;
- deployment, publication, release, or PyPI scope;
- broader OpenCode authority.

AUTO-0019 recovery remains no-replay and never invokes executor/OpenCode/
`quality_verify`.

## Verification

Focused tests cover:

- schema v1 active compatibility;
- schema v2 quiescent construction;
- rejection of schema v1 quiescent state;
- rejection of non-null active identity with `QUIESCENT`;
- rejection of null active identity for active lifecycle values;
- coherent schema v2 document projections;
- rejection of a fabricated AUTO-0021 marker;
- tracked repository coherence and read-only behavior.

The extension is accepted only after exact PR-head Quality,
expected-head-protected merge, and push-triggered Quality success for the exact
merged `master` SHA.
