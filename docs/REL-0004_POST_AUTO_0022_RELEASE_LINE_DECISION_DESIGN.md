# REL-0004 — Post-AUTO-0022 Release-Line Decision and Readiness

## Purpose

Define the evidence and authority contract for deciding whether the verified
post-AUTO-0022 repository should become a new release line.

REL-0004-01 is design-only. It does not select or change a version, freeze a
release candidate, create a tag or GitHub Release, upload assets, publish to a
package registry, change credentials, or add publishing automation.

## Verified Baselines

The current repository baseline is exact `master`
`4914f3467c1f5e44b974d956f0ba8a18c40fd9f3`. AUTO-0022 terminal closure
merged through PR #206 after pre-merge Quality #425. Push-triggered Quality
#426 (run id `32520541220`) completed successfully for that exact `master`.

The immutable published baseline remains:

```text
release:       AI-Engineering 0.2.0
tag:           v0.2.0
tag_sha:       1faf14c121b7b5da7c8781e3de4e836f85838a76
wheel:         ai_engineering-0.2.0-py3-none-any.whl
sdist:         ai_engineering-0.2.0.tar.gz
PyPI:          not approved / not published
```

`pyproject.toml` still declares version `0.2.0`. That is correct until a new
version and exact candidate are separately approved; repository work after the
tag does not mutate the historical release.

## Fresh Delta Inventory

The exact `v0.2.0..master` audit records:

```text
commits:                  403
files_changed:            173
insertions:               29531
deletions:                462
source_python_files:      63 -> 98
test_python_files:        16 -> 72
release_test_files:       1 -> 10
```

The delta includes AUTO-0003 through AUTO-0022 delivery, including
documentation ownership, migration and reconciliation planning/apply/policy/
approval/evidence, read-only GitHub/OpenCode control, worker lifecycle,
exact-Quality verification, workstation doctor/relay, reliability and
no-replay claim recovery, and canonical documentation coherence.

The installed CLI entry point changed from `ai_engineering.cli:main` to
`ai_engineering.public_cli:main`, while the package dependency constraint
remains `mcp>=1.27,<1.28` and supported Python remains `>=3.11`. These are
release-relevant compatibility surfaces and must be audited, not assumed.

## Roadmap Decision

The fresh roadmap audit found no open defect/work PR and no unreconciled
AUTO/runtime gap. The only open issue is the intentional read-only control
channel. The material next decision is therefore release readiness for the
large verified post-v0.2.0 delta, not another automatically numbered AUTO
milestone.

REL-0004 does not assume that a release must occur. A later evidence stage may
conclude `NOT_READY` or recommend deferral without changing the published
release.

## Canonical-State Namespace Boundary

The schema-v2 canonical project-state manifest intentionally accepts only
`AUTO-NNNN` milestone/stage identities. REL release governance is a separate
namespace. REL-0004-01 therefore leaves the strict manifest unchanged at:

```text
completed_through: AUTO-0022
active_milestone:  null
active_stage:      null
active_state:      QUIESCENT
release_line:      v0.2.0
```

This design does not weaken or extend the parser, fabricate AUTO-0023, or
represent an unselected future release as active canonical AUTO work.

## Required Compatibility Decision

Before any version change, REL-0004 must classify the exact delta across:

- installed `ai-engineering` CLI commands, output contracts, and exit codes;
- importable public Python surfaces and typed models;
- MCP server/tool schemas and configuration behavior;
- reconciliation plans, policies, approvals, and receipt formats;
- control request/result/recovery envelopes and bounded task classes;
- project template and generated-project contracts;
- package metadata, dependencies, Python floor, wheel/sdist contents, and
  console entry point;
- compatibility claims already made by v0.2.0 documentation.

The version decision must be explicit and justified from that inventory. This
design does not choose `0.2.1`, `0.3.0`, `1.0.0`, or any other version.

## Required Candidate Gates

An approved future exact candidate must provide all of the following:

1. exact candidate commit on canonical `master` with a clean worktree;
2. exact PR-head and push-triggered post-merge Quality success;
3. canonical documentation coherence success;
4. Ruff, mypy, and the complete pytest suite;
5. wheel and sdist build plus metadata/content inspection;
6. isolated wheel installation and public CLI/MCP smoke verification;
7. all installed-distribution/release tests;
8. fresh Windows-local verification for the supported Python floor, with only
   explicitly justified privilege-dependent skips;
9. release notes bounded to the selected exact delta;
10. recorded asset names and hashes before publication approval.

The current GitHub Quality workflow runs Ubuntu and Python 3.11 only. It is
authoritative for its exact Linux gate but does not substitute for the required
fresh Windows-local release evidence.

## Publication Boundaries

The following remain separate, explicit actions:

- version metadata change;
- release-candidate selection;
- Git tag creation;
- GitHub Release creation;
- wheel/sdist upload;
- PyPI or TestPyPI publication;
- signing, provenance, credentials, or publishing-workflow changes.

Approval of design, version preparation, or readiness evidence grants none of
those actions. PyPI remains not approved.

## Delivery Stages

1. `REL-0004-01` — design, exact baselines, delta audit, and gate contract.
2. `REL-0004-02` — exact compatibility inventory and explicit version/scope
   decision; separately approved.
3. `REL-0004-03` — approved version metadata/release notes and candidate
   preparation; no publication.
4. `REL-0004-04` — exact Linux, distribution, installed-wheel, and
   Windows-local readiness evidence.
5. `REL-0004-05` — explicit publication decision and only the specifically
   approved tag/GitHub Release/assets actions; PyPI remains separate.
6. `REL-0004-06` — post-publication or deferred-release reconciliation.

Each repository-writing stage requires exact PR-head Quality,
expected-head-protected merge, and exact push-triggered post-merge Quality.
External publication actions require their own explicit confirmation.

## REL-0004-01 Completion Rule

The design stage is complete only when this contract and its exact inventory
pass exact PR-head Quality, expected-head-protected merge, and exact
push-triggered post-merge Quality. Completion authorizes no REL-0004-02 work,
version change, candidate selection, or publication action.

## REL-0004-02 Decision Record

REL-0004-02 completes the required exact compatibility inventory in
`REL-0004_02_COMPATIBILITY_INVENTORY_VERSION_DECISION.md` and selects intended
next version `0.3.0` with intended tag `v0.3.0`.

The decision does not change package/runtime metadata or freeze a candidate.
It identifies active MCP initialize-version alignment and complete public CLI
help-tree exposure as mandatory pre-candidate corrections. REL-0004-03 remains
separately approval-gated, and all publication boundaries above remain intact.
