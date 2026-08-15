# AUTO-0001 — Engineering Project Bootstrap Design

**Status:** DESIGN / PROPOSED
**Milestone:** M3 — Engineering Automation
**Scope:** additive orchestration over the verified SDK-0001 project-template API

## 1. Purpose

AUTO-0001 defines the first bounded engineering-automation workflow for AI-Engineering after the
verified 0.1.0 baseline.

The capability creates a new standalone engineering project by orchestrating already-approved
project-template behavior and then verifying the resulting project. It is not a replacement for
SDK-0001 and must not duplicate template rendering, Python scaffold generation, or Git safety
logic.

The design follows the project rule: **documentation before implementation**.

## 2. Relationship to Existing Contracts

AUTO-0001 builds on, and must preserve, these contracts:

- **SDK-0001 V1** remains the authoritative document-first standalone project contract.
- **SDK-0001.1** remains the optional generic Python scaffold contract.
- **SDK-0001.2** remains the existing `ai-engineering project create` CLI contract.
- Existing nested-Git protection, empty-target validation, `main` branch initialization, and
  initial-commit behavior remain owned by SDK-0001.
- AUTO-0001 must consume the public typed SDK API rather than call `ProjectTemplateGenerator`
  internals.

Existing SDK behavior must remain unchanged when AUTO-0001 is not selected.

## 3. Objective

Provide one explicit **engineering bootstrap** operation that:

1. accepts a bounded project-bootstrap request;
2. delegates project creation to `create_standalone_project()`;
3. uses the verified Python scaffold when requested by the bootstrap profile;
4. performs post-generation verification;
5. returns a typed bootstrap result describing what was created and verified.

The initial implementation is local-only and deterministic from explicit inputs. It does not
contact GitHub or another remote service.

## 4. V1 Bootstrap Profile

AUTO-0001 V1 defines exactly one profile:

`python-engineering`

The profile is intentionally explicit rather than becoming the default behavior of SDK-0001.
It creates the SDK-0001 V1 document set plus the verified SDK-0001.1 Python scaffold.

The profile therefore requires the existing generated files:

- `README.md`
- `AI_CHAT_START.md`
- `PROJECT_CONTEXT.md`
- `PROJECT_MAP.md`
- `CURRENT_STATUS.md`
- `ROADMAP.md`
- `DECISIONS.md`
- `CODING_STANDARDS.md`
- `MASTER_INDEX.md`
- `pyproject.toml`
- `.gitignore`
- `src/<package_name>/__init__.py`
- `tests/test_smoke.py`

AUTO-0001 V1 does **not** introduce a second template set or rewrite these generated files after
SDK generation. Future automation-specific generated files require a separately approved design
extension.

## 5. Public API Contract

The proposed public API is additive:

```python
@dataclass(frozen=True)
class EngineeringBootstrapRequest:
    target_directory: Path
    project_name: str
    project_description: str
    author: str | None = None
    profile: str = "python-engineering"


@dataclass(frozen=True)
class EngineeringBootstrapResult:
    project: StandaloneProject
    profile: str
    package_name: str
    verification: EngineeringBootstrapVerification


@dataclass(frozen=True)
class EngineeringBootstrapVerification:
    required_files_present: bool
    git_repository: bool
    default_branch: str
    initial_commit_present: bool
    python_package_present: bool
    smoke_test_present: bool
```

The recommended entry point is:

```python
bootstrap_engineering_project(request: EngineeringBootstrapRequest) -> EngineeringBootstrapResult
```

Exact module placement is an implementation decision, but the public API should live under the
`ai_engineering` package and must not expose generator internals.

## 6. Request Mapping

For V1, `bootstrap_engineering_project()` maps its request to exactly one
`StandaloneProjectRequest`:

- `target_directory` → unchanged;
- `project_name` → unchanged;
- `project_description` → unchanged;
- `author` → unchanged;
- `include_python_scaffold=True`;
- `project_id=None`;
- `created_date=None`;
- `additional_documents={}`.

The function calls `create_standalone_project()` exactly once.

This prevents AUTO-0001 from becoming a parallel project generator.

## 7. Profile Validation

V1 accepts only the exact profile name `python-engineering`.

Unknown, empty, differently cased, or whitespace-padded profile names fail with a controlled
bootstrap-domain error. Silent fallback to another profile is forbidden.

Additional profiles are not added until a real consumer need and a separate design contract exist.

## 8. Destination and Portability Contract

AUTO-0001 inherits destination rules from SDK-0001:

- target may be non-existent or empty;
- target inside an existing Git working tree is rejected;
- relative and absolute destination paths are supported by the underlying public API;
- generated content must not embed machine-specific absolute paths;
- no `C:\\Users\\...`, `D:\\...`, OneDrive-specific, home-directory-specific, or checkout-specific
  paths may be generated;
- no assumption is made about the machine on which the generated project will later run.

AUTO-0001 must not weaken SDK destination or Git protections.

## 9. Git Contract

Git repository creation remains delegated to SDK-0001.

For V1 the bootstrap result must verify:

- a Git working tree exists at the generated target;
- the default branch is `main`;
- an initial commit exists;
- the generated files are included in the SDK-created initial commit.

AUTO-0001 performs no remote creation, remote configuration, push, pull, fetch, credential
operation, GitHub API call, or branch publication.

It must not make a second bootstrap commit merely to label the automation workflow.

## 10. Post-Generation Verification

A successful bootstrap is more than successful file writing. After SDK generation, AUTO-0001 must
verify the bounded invariants it claims.

Required V1 verification:

1. every expected V1 document exists;
2. `pyproject.toml` and `.gitignore` exist;
3. the derived package directory and `__init__.py` exist;
4. `tests/test_smoke.py` exists;
5. the target is a Git repository;
6. the current branch is `main`;
7. at least one commit exists and the SDK reports successful project creation;
8. the result paths resolve beneath the generated project target.

Verification is read-only. It must not repair, rewrite, stage, commit, install dependencies, or
mutate the generated project after SDK generation.

## 11. Verification Failure Semantics

AUTO-0001 introduces a bootstrap-domain error type, provisionally
`EngineeringBootstrapError`.

Errors fall into two categories:

- **creation failure** — SDK-0001 rejects or fails project creation; the original actionable
  condition is preserved through the bootstrap boundary;
- **verification failure** — SDK creation returned but one or more required AUTO-0001 invariants
  cannot be proven.

The implementation must not claim success after a verification failure.

AUTO-0001 does not promise transactional rollback. Existing SDK behavior regarding files written
before a hard Git failure remains unchanged.

## 12. CLI Contract

AUTO-0001 may extend the installed CLI with one additive command:

```text
ai-engineering project bootstrap
```

The existing command remains unchanged:

```text
ai-engineering project create
```

Proposed V1 bootstrap inputs:

| Input | Classification | Mapping |
|---|---|---|
| `--name NAME` | REQUIRED | `project_name` |
| `--destination PATH` | REQUIRED | `target_directory` |
| `--description TEXT` | REQUIRED | `project_description` |
| `--author NAME` | OPTIONAL | `author` |
| `--profile python-engineering` | OPTIONAL | explicit profile; default is `python-engineering` |

The bootstrap command must call the public AUTO-0001 API and must not duplicate orchestration or
verification logic.

### Success output

The V1 success contract is concise `key=value` stdout:

```text
bootstrapped_project=<resolved absolute path>
project_name=<input name>
profile=python-engineering
package_name=<derived package name>
git_branch=main
initial_commit=created
verification=passed
```

Expected domain/operational failures go to stderr with no success output.

The exit-code contract should preserve SDK-0001.2 conventions:

- `0` — success;
- `1` — expected domain or operational failure;
- `2` — CLI usage error;
- `3` — unexpected internal failure.

## 13. No-Overwrite and Idempotency Policy

AUTO-0001 V1 is **create-only**, not convergent configuration management.

- It does not overwrite an existing project.
- It does not update an existing generated project.
- Re-running against a non-empty target fails through the SDK contract.
- It does not attempt to infer whether an existing project was previously generated by
  AI-Engineering.

A future `sync`, `upgrade`, or `repair` capability requires a separate milestone because it has a
materially different safety model.

## 14. Dependency and Environment Policy

AUTO-0001 creates project files but does not prepare the machine environment.

V1 does not:

- create a virtual environment;
- run `pip`, `uv sync`, or another installer;
- download dependencies;
- execute generated tests;
- modify shell profiles or environment variables;
- install Git hooks;
- require network access.

The generated Python scaffold continues to declare its existing dev dependencies according to
SDK-0001.1.

## 15. Security Boundary

AUTO-0001 is a local project-bootstrap workflow, not a sandbox.

It inherits SDK-0001 target and nested-Git safety rules. It does not expand SAFE-0001's MCP
Workspace authorization boundary to local CLI/API project generation, Git subprocesses, Python
subprocesses, or the operating system.

No remote credentials, tokens, secrets, or publication permissions are accepted by the V1 API.

## 16. Automated Verification Matrix

Implementation must provide automated evidence for at least:

| Row | Required evidence |
|---|---|
| Valid `python-engineering` request | project created and typed result returned |
| Exact generated file set | V1 docs + SDK-0001.1 scaffold present |
| Public API delegation | `create_standalone_project()` called exactly once |
| Default profile | resolves to `python-engineering` |
| Unknown profile | controlled failure before project creation |
| Existing/non-empty target | controlled SDK-derived failure |
| Nested Git target | controlled SDK-derived failure |
| Portable relative destination | succeeds without generated machine-specific paths |
| Absolute destination | succeeds subject to SDK rules |
| Git repository | repository exists at target |
| Default branch | `main` |
| Initial commit | present and contains generated files |
| Verification result | all claimed V1 invariants reported true |
| Verification failure | no success result is returned |
| Existing SDK create command | behavior unchanged |
| Existing SDK Python APIs | behavior unchanged |
| Bootstrap CLI help | command discoverable if CLI is implemented in this milestone |
| Bootstrap CLI success | stable stdout and exit `0` |
| Bootstrap CLI expected error | stderr, no success stdout, exit `1` |

Repository-wide pytest, Ruff, mypy, and `git diff --check` must remain green.

## 17. Implementation Boundaries

The smallest implementation should separate:

- public request/result/error models;
- bootstrap orchestration;
- read-only post-generation verification;
- CLI adaptation, if included in the implementation task.

It should reuse existing package-name derivation or expose an approved helper rather than create a
second normalization algorithm.

Implementation must not refactor unrelated MCP, Registry, Runtime, Workspace, Git, Python,
diagnostics, packaging, CI, or release code merely to introduce AUTO-0001.

## 18. Non-Goals

AUTO-0001 V1 explicitly excludes:

- GitHub repository creation;
- Git remotes, push, pull, or hosting integration;
- GitHub Actions generation;
- Docker or Compose generation;
- framework-specific application templates;
- multiple bootstrap profiles;
- dependency installation;
- virtual environment creation;
- executing generated tests;
- package publication;
- GitHub Releases or tags;
- PyPI;
- secrets or credential management;
- interactive prompts or TUI;
- JSON output;
- project update/sync/repair;
- documentation synchronization;
- application/business logic generation;
- changing the SDK-0001 V1 default output;
- changing the existing `ai-engineering project create` contract.

## 19. Proposed Atomic Implementation Sequence

After design approval, implementation should be split into bounded tasks:

### AUTO-0001-01 — Bootstrap Core API

Add typed request/result/error models, the single V1 profile, orchestration over
`create_standalone_project()`, and read-only verification. No CLI changes.

### AUTO-0001-02 — Bootstrap CLI Adapter

Add `ai-engineering project bootstrap` over the verified public bootstrap API. Do not change
`project create`.

### AUTO-0001-03 — Integration and Distribution Verification

Verify installed CLI bootstrap behavior from an isolated installed wheel and reconcile project
status/release evidence. Do not publish a new release automatically.

Each task must have its own test/evidence boundary and may stop if a real defect is discovered.

## 20. Completion Criteria

AUTO-0001 is complete only when:

- the design contract is approved;
- the public bootstrap API is implemented without duplicating SDK generation logic;
- `python-engineering` is the only V1 profile;
- post-generation verification is implemented and fail-closed;
- existing SDK APIs and `project create` behavior remain unchanged;
- the bootstrap CLI is implemented and verified if included in the approved implementation scope;
- isolated installed-package behavior is verified;
- repository quality gates are green;
- documentation records the verified behavior;
- no remote repository, publishing, dependency-installation, or update/sync behavior is implied.
