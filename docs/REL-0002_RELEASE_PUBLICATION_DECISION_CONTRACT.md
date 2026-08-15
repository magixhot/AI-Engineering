# REL-0002 — Release Publication Decision Contract

**Status:** DESIGN / DECISION CONTRACT

## 1. Purpose

REL-0002 defines the governance boundary for any public release publication of AI-Engineering.
It follows REL-0001 local distribution verification and does not itself publish anything.

The repository already verifies local wheel/sdist construction, isolated wheel installation,
installed metadata, the console entry point, GitHub Actions quality gates, and the current
Workspace safety boundary. Those facts establish artifact readiness evidence, not a public
release commitment.

## 2. Current Baseline

- Distribution name: `ai-engineering`.
- Current package version: `0.1.0`.
- Supported Python metadata: `>=3.11`.
- Local wheel and sdist verification: COMPLETE / VERIFIED under REL-0001.
- CI quality gates: COMPLETE / VERIFIED under CI-0001.
- Current Linux CI baseline: pytest 99 passed, Ruff 0, mypy 0.
- Current Windows-local baseline: pytest 98 passed, 1 permitted symlink-fixture skip, Ruff 0,
  mypy 0.
- No GitHub Release has been approved or created as part of REL-0001.
- No PyPI publication has been approved or performed.
- No repository-wide tag/version publication policy is currently approved.

## 3. Publication Surfaces

REL-0002 treats the following as separate publication surfaces. Approval of one does not imply
approval of another.

### 3.1 Git tag

A release tag identifies an exact repository commit. Creating a release tag is a public version
statement and therefore requires explicit approval.

If tagging is later approved, the initial convention should be `v<project-version>`; for the
current line this would be `v0.1.0`. The tag target must be the exact approved release commit on
`master`, after required quality evidence is green.

This document does not create `v0.1.0`.

### 3.2 GitHub Release

A GitHub Release is a separately approved publication surface built from an approved release tag.
It may contain release notes and verified distribution artifacts.

A GitHub Release must not be inferred from a successful merge, CI run, or local artifact build.
Its title, notes, tag, and attached-asset policy require explicit release approval.

### 3.3 PyPI

PyPI is a package-registry publication surface with a stronger external support and namespace
commitment. PyPI publication requires a separate explicit decision after package-name ownership,
authentication, publishing identity, credential/Trusted Publisher policy, and support expectations
are verified.

REL-0002 does not approve PyPI publication.

## 4. Version and Tag Consistency Contract

Before any release tag or GitHub Release is created:

1. `pyproject.toml` is the authoritative package-version declaration for the current packaging
   implementation.
2. The intended tag version must match the package version exactly after removing the leading
   `v` from the tag.
3. Built wheel and sdist filenames and installed distribution metadata must report that same
   version.
4. The release commit must be on canonical `master` and must not contain uncommitted or
   unpublished local-only changes.
5. Required CI and distribution verification for the release commit must be green.

A version mismatch is a release blocker, not a condition to repair during publication.

## 5. Release Evidence Contract

Before publication of an approved surface, evidence must record at least:

- exact `master` commit SHA;
- intended version and tag;
- successful GitHub Actions Quality result for the release commit;
- wheel and sdist verification result;
- installed metadata/version verification result;
- installed CLI smoke result;
- artifact filenames;
- release notes or change summary appropriate to the approved surface;
- explicit statement of which publication surfaces are approved.

Evidence must distinguish local verification from externally published state.

## 6. Artifact Policy for a Future GitHub Release

If GitHub Release publication is approved later, the default candidate assets are the REL-0001
verified wheel and sdist for the exact release version.

The release process must build artifacts from the approved release commit rather than attach
arbitrary local files. Asset names and metadata must match the approved package version.

Checksums, signatures, SBOMs, provenance attestations, and binary bundles are not required by the
current contract and require separate scope if desired.

## 7. PyPI Decision Gate

PyPI remains **NOT APPROVED** until a later explicit decision verifies all of the following:

- the intended public package name and namespace ownership;
- the publishing account/organization owner;
- authentication strategy, preferably without long-lived repository secrets when a supported
  trusted-publishing mechanism is selected;
- whether TestPyPI is required before production PyPI;
- who is authorized to publish;
- whether publication is manual or CI-driven;
- rollback/yank policy;
- public support and compatibility expectations for the package.

No credential should be added to the repository merely to satisfy this design task.

## 8. Automation Boundary

CI-0001 remains a quality-gate workflow. It must not silently become a release publisher.

Any future tag/release/PyPI automation requires a separate implementation milestone and explicit
permissions design. A workflow that can publish must use the minimum permissions necessary and
must not be introduced as an incidental extension of the existing `quality` job.

## 9. Approval Model

The following actions require explicit user approval immediately before execution:

- creating or moving a release tag;
- creating a GitHub Release;
- uploading release assets;
- publishing to TestPyPI or PyPI;
- adding or changing publication credentials/trusted-publisher configuration;
- enabling automated publication from GitHub Actions.

Design, validation, dry-run inspection, and preparation of release notes do not constitute
publication approval.

## 10. Failure Classes

Future publication work should classify failures as one of:

- version/tag mismatch;
- non-canonical release commit;
- failed quality gate;
- failed artifact verification;
- artifact/content mismatch;
- GitHub tag/release permission failure;
- package-registry namespace/ownership failure;
- authentication/trusted-publisher failure;
- upload/publication failure;
- release-note/evidence inconsistency;
- unknown.

A failed publication attempt must not be represented as a successful release.

## 11. Non-Goals

REL-0002 does not:

- create a Git tag;
- create a GitHub Release;
- publish to TestPyPI or PyPI;
- change version `0.1.0`;
- define a full semantic-versioning lifecycle;
- add release automation;
- add credentials or secrets;
- modify CI-0001;
- change package contents or runtime behavior;
- claim general production readiness.

## 12. Decision Outcome

The project is **ready to prepare a GitHub tag/Release proposal**, because local distribution,
quality gates, and current safety verification are established.

However, public publication remains an explicit user decision:

- Git tag: **NOT YET APPROVED**.
- GitHub Release: **NOT YET APPROVED**.
- PyPI: **NOT APPROVED; additional ownership/authentication/support decisions required**.

The smallest safe follow-up after this design is a release-readiness audit that prepares the exact
candidate commit, tag, release notes, and artifact evidence without publishing them.

## 13. Completion Criteria for REL-0002

REL-0002 design is complete when:

- publication surfaces are explicitly separated;
- version/tag consistency rules are documented;
- evidence requirements are documented;
- GitHub Release artifact policy is bounded;
- PyPI has an explicit decision gate;
- publication automation remains separately scoped;
- publication actions require explicit approval;
- no tag, release, registry publication, credential, or runtime behavior is changed by the design
  task.
