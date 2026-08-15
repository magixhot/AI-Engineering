# AUTO-0001 — Engineering Project Bootstrap Verification Evidence

**Status:** COMPLETE / VERIFIED
**Evidence date:** 2026-08-15

## Scope

This document records implementation and verification evidence for AUTO-0001 after completion of its three approved atomic tasks:

- AUTO-0001-01 — Bootstrap Core API;
- AUTO-0001-02 — Bootstrap CLI Adapter;
- AUTO-0001-03 — Integration and Distribution Verification.

## Core API Evidence

The implemented AUTO-0001 core provides typed request, result, verification, and controlled-error models. V1 accepts exactly the `python-engineering` profile, maps the request to the existing SDK-0001 standalone-project API, calls that public generator path once, and verifies the generated project without repairing or mutating it after generation.

Verified invariants include the approved document/scaffold file set, target containment, Git repository root, `main` branch, initial commit and committed generated files, Python package presence, and smoke-test presence. Verification failure is fail-closed and does not return a successful bootstrap result.

## CLI Evidence

The installed console-script command family contains both:

- `ai-engineering project create` — existing SDK-0001.2 behavior;
- `ai-engineering project bootstrap` — additive AUTO-0001 behavior.

The bootstrap CLI uses the public AUTO-0001 API rather than duplicating orchestration or verification. The verified success output is the approved `key=value` contract containing project path/name, profile, package name, `main`, initial-commit state, and `verification=passed`.

Expected domain/operational failures use stderr and exit code 1, argparse usage errors retain exit code 2, and unexpected internal failures retain exit code 3.

## Installed Distribution Evidence

AUTO-0001-03 extends the existing REL-0001 release test rather than creating a parallel artifact pipeline.

The test:

1. copies a clean source tree outside the working checkout;
2. builds the 0.1.0 wheel and sdist;
3. creates a fresh external virtual environment;
4. installs the built wheel into that environment;
5. clears `PYTHONPATH` and `PYTHONHOME` for verification subprocesses;
6. confirms the imported package resolves inside the isolated environment;
7. confirms installed `project --help` exposes `bootstrap`;
8. executes installed `ai-engineering project bootstrap` from an external working directory;
9. verifies the generated `python-engineering` scaffold, Git repository, `main` branch, and initial commit.

This proves the bootstrap command is present in and functional from the built wheel without editable-install or source-tree import reliance.

## CI Evidence

PR verification run `31892172254` completed successfully on GitHub Actions / Linux / Python 3.11.

Observed quality result:

- pytest: **112 passed**;
- Ruff: **0 findings**;
- mypy: **0 issues in 71 source files**;
- installed wheel build/install/bootstrap smoke: PASS.

A final post-merge `master` Quality run is required before the merged repository state is treated as canonical AUTO-0001 completion evidence.

## Compatibility and Safety Boundaries

AUTO-0001 remains create-only and local-only. It does not add project update/sync/repair, dependency installation, virtual-environment preparation, remote repository creation, Git remotes/push, GitHub automation, publishing, credentials, or additional bootstrap profiles.

SAFE-0001 remains specifically an MCP Workspace path-authorization boundary. AUTO-0001 does not turn it into an OS-level, Git-subprocess, or Python-subprocess sandbox.

## Publication Boundary

Git tag `v0.1.0` and GitHub Release `AI-Engineering 0.1.0` are immutable historical publication evidence for commit `73929bd15fa7637db8162aac199697582bb25e67`.

AUTO-0001 was completed after that tag. Its implementation and installed-wheel verification are current `master` evidence and must not be represented as functionality contained in the already-published v0.1.0 tag/artifact.

PyPI remains not approved and not published.

## Completion Assessment

AUTO-0001 is **COMPLETE / VERIFIED** once this verification change is merged and its post-merge `master` Quality run succeeds. No additional implementation debt is required for the approved V1 scope.
