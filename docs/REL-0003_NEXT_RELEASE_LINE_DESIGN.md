# REL-0003 — Next Release Line Decision and Readiness

**Status:** DESIGN / DECISION CONTRACT

## 1. Purpose

REL-0003 defines the decision and readiness contract for the next AI-Engineering release line after the immutable `v0.1.0` publication.

The task is intentionally preparatory. It determines what a future release candidate must contain and prove before any version change, tag, GitHub Release, asset upload, or package-registry publication occurs.

REL-0003-01 does not publish anything.

## 2. Current Baseline

The current canonical `master` baseline at the start of this design is commit `99e487c22999ed255372fb3d083f6fa3760fc995`.

The published historical release remains:

- package/release version: `0.1.0`;
- tag: `v0.1.0`;
- GitHub Release: `AI-Engineering 0.1.0`;
- tagged commit: `73929bd15fa7637db8162aac199697582bb25e67`;
- PyPI: not approved and not published.

The following verified capabilities were completed after the immutable `v0.1.0` tag and therefore are not part of that published artifact:

- AUTO-0001 Engineering Project Bootstrap;
- AUTO-0002 Project Documentation Synchronization;
- SAFE-0002 Git/Python Execution Safety;
- associated cross-platform and integration hardening completed before this design.

Current quality evidence at the start of REL-0003 records:

- Linux GitHub Actions / Python 3.11: pytest 155 passed, Ruff 0 findings, mypy 0 findings in 79 source files;
- Windows-local: pytest 153 passed with 2 permitted privilege-dependent symlink-fixture skips, Ruff 0, mypy 0 in 79 source files, `git diff --check` passed, working tree clean.

These values are baseline evidence, not immutable future release numbers. A later release candidate must record fresh evidence for its exact candidate commit.

## 3. Release-Line Decision

REL-0003 does not assume the next version number merely from chronology.

Before implementation of a next release candidate, the project must explicitly approve:

1. the intended package version;
2. the corresponding Git tag name;
3. the exact set of verified milestones represented by that release;
4. whether the release is a GitHub-only publication or expands to another publication surface.

The candidate version must be chosen before changing `pyproject.toml`. A version bump is an implementation action, not a side effect of this design contract.

## 4. Candidate Scope

The minimum candidate scope for the next release line is the current verified post-`v0.1.0` baseline, including AUTO-0001, AUTO-0002, and SAFE-0002 in addition to the contracts already represented by `v0.1.0`.

A future readiness task must enumerate the exact included milestones and verify that their documentation statuses are consistent with the candidate source tree.

New functionality must not be added opportunistically during release preparation. If additional capabilities are desired, they must first complete their own design, implementation, verification, and reconciliation lifecycle before being admitted to the candidate.

## 5. Candidate Freeze Contract

A release candidate is identified by one exact commit SHA on canonical `master`.

Before that SHA can be approved for publication:

- the working release scope must already be merged to `master`;
- no required release change may exist only in a local checkout or unmerged branch;
- package version, distribution metadata, artifact filenames, installed metadata, and intended tag must agree;
- required quality and distribution evidence must be green for the exact candidate state;
- release notes must describe the actual delta from `v0.1.0` without claiming excluded work.

If any source, packaging, version, release-note-critical documentation, or verification-affecting change lands after candidate selection, the candidate SHA is invalidated and must be selected and verified again.

Documentation-only evidence recording after successful candidate verification may occur only when it does not alter the candidate artifact contents. The publication record must distinguish the artifact/tag target SHA from later evidence-only commits.

## 6. Version Consistency Contract

For an approved next release candidate:

1. `pyproject.toml` remains the authoritative package-version declaration for the current packaging implementation.
2. The intended Git tag must be `v<package-version>` unless a separately approved policy changes that convention.
3. Wheel and sdist filenames must report the approved version.
4. Built distribution metadata and isolated installed metadata must report the approved version.
5. The installed `ai-engineering` console entry point must resolve from the candidate wheel installation.
6. Repository documentation must not describe the historical `v0.1.0` artifact as containing post-tag functionality.

Any mismatch is a release blocker.

## 7. Artifact and Distribution Readiness

The next release candidate must reuse the REL-0001 distribution contract unless a separately approved packaging change supersedes it.

Required candidate evidence includes:

- successful wheel build;
- successful sdist build;
- inspected wheel contents;
- inspected sdist contents;
- fresh isolated wheel installation outside the source checkout;
- installed import verification;
- installed distribution metadata verification;
- installed `ai-engineering --help` verification;
- installed project command smoke sufficient to cover the currently supported release surface;
- recorded artifact filenames for the exact approved version.

Artifacts attached to a future GitHub Release must be built from the approved candidate source state and must not be arbitrary previously generated local files.

## 8. Quality and Cross-Platform Evidence

The exact candidate must have successful GitHub Actions Quality evidence on Linux/Python 3.11 under CI-0001, including Ruff, mypy, and the full pytest suite.

Because the current project contains path and subprocess safety contracts with Windows-specific filesystem behavior, the next release candidate must also record a fresh Windows-local verification result covering:

- full pytest;
- any focused safety suite required by the candidate scope;
- Ruff;
- mypy;
- `git diff --check`;
- clean working tree.

Privilege-dependent symlink fixture skips are acceptable only when they are explicitly identified as environment limitations and equivalent link-escape behavior is executed successfully in Linux CI. Unexpected skips or failures are release blockers until classified.

## 9. Release Notes Contract

Release notes for the next line must be prepared before publication and must include at least:

- the version and tag;
- the exact candidate/tag target SHA;
- a concise delta from `v0.1.0`;
- AUTO-0001 bootstrap capability;
- AUTO-0002 bounded documentation synchronization capability;
- SAFE-0002 Git/Python execution-safety boundary;
- relevant compatibility or behavioral boundaries;
- quality/distribution verification summary;
- explicit statement that the safety boundaries are not an operating-system sandbox;
- publication surfaces actually approved.

Release notes must not claim PyPI availability unless PyPI has separately been approved and publication has actually succeeded.

## 10. GitHub Publication Surface

REL-0003 treats Git tag creation, GitHub Release creation, and release-asset upload as explicit publication actions.

A future implementation task may prepare the exact tag, release title, release notes, and verified assets, but publication still requires explicit user approval immediately before execution.

Successful CI, a version bump, or a merged readiness PR does not itself authorize publication.

## 11. PyPI Boundary

PyPI remains **NOT APPROVED** under REL-0003.

This contract does not:

- reserve or claim the public package namespace;
- configure PyPI or TestPyPI credentials;
- configure Trusted Publishing;
- add publishing secrets;
- publish to TestPyPI;
- publish to PyPI;
- imply that approval of a Git tag or GitHub Release also approves PyPI.

Any future PyPI work requires a separate explicit decision covering ownership, authentication, publisher identity, support expectations, and rollback/yank policy.

## 12. CI and Automation Boundary

CI-0001 remains a quality-gate workflow and must not become a publisher as part of REL-0003-01.

No release-on-tag workflow, release asset uploader, registry publisher, deployment permission, OIDC publication permission, or repository secret is introduced by this design.

Release automation, if desired later, requires its own design and minimum-permission review.

## 13. Required Readiness Evidence

Before a next release can be proposed for publication, the readiness record must contain at least:

- approved version;
- intended tag;
- exact candidate SHA;
- exact included milestone list;
- successful Linux Quality run for the candidate;
- fresh Windows-local evidence;
- wheel and sdist filenames;
- artifact-content verification;
- isolated wheel install/import/metadata/CLI evidence;
- version consistency result;
- release notes draft;
- explicit publication-surface approval state;
- explicit PyPI `NOT APPROVED / NOT PUBLISHED` state unless a later decision supersedes it.

## 14. Failure Classes

Release-readiness failures should be classified as one of:

- version decision not approved;
- version/tag mismatch;
- candidate SHA invalidated by later change;
- milestone/documentation scope inconsistency;
- failed Linux quality gate;
- failed or unexplained Windows verification;
- build configuration failure;
- artifact-content failure;
- isolated installation failure;
- installed metadata/version failure;
- console entry-point failure;
- release-note/evidence inconsistency;
- publication approval missing;
- GitHub publication failure;
- PyPI boundary violation;
- unknown.

No failed or incomplete readiness state may be represented as a successful release.

## 15. Non-Goals

REL-0003-01 does not:

- choose or change the package version;
- create or move a Git tag;
- create a GitHub Release;
- upload release assets;
- publish to TestPyPI or PyPI;
- modify package source or runtime behavior;
- add new bootstrap profiles;
- initialize AUTO-0002 ownership markers;
- expand AUTO-0002 writable documents;
- add new MCP clients or execution tools;
- change SAFE-0001 or SAFE-0002 authority semantics;
- add release automation, credentials, secrets, signing, SBOM, provenance, or deployment workflows;
- claim general production readiness.

## 16. Completion Criteria for REL-0003-01

REL-0003-01 design is complete when:

- the historical `v0.1.0` boundary is preserved;
- the minimum post-`v0.1.0` candidate scope is documented;
- version selection is explicitly deferred to approval rather than assumed;
- candidate freeze/invalidation rules are defined;
- artifact and version consistency requirements are defined;
- Linux and Windows evidence requirements are defined;
- release-note requirements are defined;
- GitHub publication actions remain approval-gated;
- PyPI remains explicitly excluded;
- no source, packaging, workflow, version, tag, release, asset, credential, or registry state is changed by this task.

## 17. Smallest Safe Follow-Up

After this design is merged, the smallest safe implementation task is:

**REL-0003-02 — Select Version and Prepare Release Candidate**

That task should first obtain explicit approval of the next version, then make only the approved version/release-readiness changes, select the resulting exact `master` candidate SHA, and gather fresh Linux, Windows, distribution, installed-wheel, and release-note evidence.

It must still stop before tag creation, GitHub Release creation, asset upload, or PyPI publication unless those publication actions receive separate explicit approval.
