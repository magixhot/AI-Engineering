# CI-0001 — Quality Gate Automation Contract

**Status:** IMPLEMENTED / EXTERNAL VERIFICATION REQUIRED
**Scope:** GitHub Actions automation of existing repository quality gates

## Objective

CI-0001 automates the established quality gates on GitHub Actions without changing application
behavior, release policy, or the public package. Initial CI protects the verified baseline of 90
pytest tests, Ruff with no findings, and mypy with no issues.

## Platform

The CI platform is **GitHub Actions**. The repository is hosted on GitHub and its reviewed change
flow is pull-request based, so Actions is the smallest integrated platform choice. No repository
policy contradicts this choice. The initial workflow is implemented at
`.github/workflows/quality.yml`; GitHub Actions run evidence remains required before this contract
can be marked complete and verified.

## Trigger Policy

The initial workflow must trigger on:

- `pull_request` targeting exactly `master`; and
- `push` targeting exactly `master`.

Pull-request runs protect proposed changes before merge. Master-push runs record the post-merge
state, including changes merged outside a pull request. Duplicate runs for a merged pull request
are acceptable because they validate different refs and keep the initial policy simple. Scheduled,
nightly, manual-dispatch, tag, and release triggers are excluded.

## Python Baseline and Portability

Initial CI uses Python **3.11** on one GitHub-hosted Linux runner. Python 3.11 is the current
verified baseline and satisfies the package requirement of `>=3.11`. A multi-Python or multi-OS
matrix is a future separately designed expansion.

The job must not use Windows paths, OneDrive, developer directories, or a global project install.
Current tests use temporary fixtures, and the release test selects the platform venv script
directory at runtime. A Linux job therefore validates the supported portable path without adding
OS-specific workarounds.

## Dependency and Cache Strategy

CI uses the existing `uv` lockfile workflow:

```text
uv sync --locked --group dev
```

`uv.lock` is the reproducibility source for resolved dependencies; `--locked` must fail rather than
silently change it. This approach installs the project plus the existing development tools,
including the standard `build` frontend used by REL-0001. A pip/dev-extra alternative is not
selected because the repository has no extras-based development contract and already maintains
`uv.lock`.

An optional `uv` cache may improve speed, but correctness must not depend on its presence. Its key
must incorporate runner OS, Python version, `uv.lock`, and `pyproject.toml`. Normal dependency
resolution requires network access on a cold cache. In particular, REL-0001 currently needs index
access to provision `setuptools>=68` for its isolated build environment; offline support is not
claimed.

## Workflow and Job Structure

The implementation must add one workflow containing one required `quality` job in this order:

1. checkout with read-only repository access;
2. set up Python 3.11;
3. install or set up `uv`;
4. restore/save the optional `uv` cache;
5. run the locked dependency sync; and
6. run Ruff, mypy, and pytest.

The initial design intentionally avoids separate lint, type, and test jobs. Splitting only adds
setup duplication before there is evidence that parallel reporting or timing merits it.

## Quality-Gate Commands

After `uv sync`, CI runs the current commands through the synchronized environment:

```text
uv run python -m ruff check .
uv run python -m mypy src tests
uv run python -m pytest
```

The inner commands preserve the canonical repository semantics. Pytest must receive process-scoped
Git identity through `GIT_AUTHOR_NAME`, `GIT_AUTHOR_EMAIL`, `GIT_COMMITTER_NAME`, and
`GIT_COMMITTER_EMAIL`; no global runner Git configuration may be changed. CI may use the runner's
temporary filesystem for pytest and release-test artifacts, but it must not add CI-only behavior or
path assumptions.

## REL-0001 Placement

`tests/release/test_distribution.py` remains in the normal full pytest suite on every pull request
and master push. It is one bounded test and is already included in the 90-test baseline. Its wheel,
sdist, isolated-venv, import-path, metadata, console-script, and project-create smoke checks are
valuable regression coverage for packaging changes. Its normal dependency/build network requirement
is an expected pytest failure condition, not a reason to silently exclude or split it initially.

## Permissions and Concurrency

Initial workflow permissions are:

```text
contents: read
```

The workflow requires no write permissions, tokens beyond the default read checkout capability,
secrets, package permissions, release permissions, or publishing credentials.

The workflow should use one simple concurrency group scoped to workflow and ref, with
`cancel-in-progress: true`. Superseded runs for the same pull request or branch are cancelled; runs
for different refs proceed independently.

## Failure Semantics

Ruff, mypy, and pytest are required gates. Any nonzero exit status fails the job; no
`continue-on-error` and no accepted flaky-test policy applies. A REL-0001 artifact, isolated-build,
or isolated-install failure is a normal pytest failure and must retain its command output for
diagnosis.

Before changing workflows, tests, source, or dependency configuration, implementation must collect
evidence and classify the first applicable failure:

| Class | Required evidence |
|---|---|
| A. WORKFLOW SYNTAX | Workflow file, GitHub validation/error location, and event/ref context. |
| B. RUNNER/PYTHON SETUP | Runner image, selected Python, setup action output, and executable version. |
| C. DEPENDENCY INSTALL | `uv` command, lockfile state, resolver output, and index/cache context. |
| D. CACHE | Cache key, hit/miss state, restore/save output, and uncached reproduction. |
| E. GIT IDENTITY | Scoped environment/configuration, Git command error, and fixture location. |
| F. RUFF | Exact finding and affected file. |
| G. MYPY | Exact diagnostic and affected module. |
| H. PYTEST | Failing test, command output, and fixture/isolation evidence. |
| I. REL-0001 DISTRIBUTION TEST | Build/install command output, artifact state, dependency/index context, and isolated paths. |
| J. PATH/OS PORTABILITY | Runner OS, path values, expected portability behavior, and minimal reproduction. |
| K. UNKNOWN | Complete job log, commit/ref, environment summary, and concise unresolved question. |

## Non-Goals

CI-0001 excludes release publishing, PyPI, GitHub Releases, release tags, changelog automation,
signing/provenance, multi-OS and multi-Python matrices, scheduled builds, deployments, Docker
builds, MCP client interoperability tests, secret-dependent tests, and workflow dispatch.

## Completion Criteria

CI-0001 becomes **COMPLETE / VERIFIED** only when:

1. a GitHub Actions workflow exists with the approved pull-request and master-push triggers;
2. it uses Python 3.11 and installs dependencies from the lockfile reproducibly;
3. Ruff, mypy, and the full pytest suite all pass;
4. REL-0001 distribution verification remains part of the normal pytest evidence;
5. only read permissions are required, with no secrets or write/publish behavior;
6. representative pull-request and post-merge/master evidence is captured;
7. local quality gates remain green; and
8. documentation records only verified CI behavior, with no release or publishing claim.

## Implementation Record

`.github/workflows/quality.yml` implements the initial contract with one `quality` job on
`ubuntu-latest` using Python 3.11. It triggers for pull requests targeting `master` and pushes to
`master`, grants only `contents: read`, and cancels superseded runs for the same workflow/ref.

The workflow runs `uv sync --locked --group dev`, then the approved Ruff, mypy, and full pytest
commands through `uv run`. Its job-scoped environment supplies Git author and committer identity
for tests that create real commits. The full pytest invocation includes REL-0001 distribution
verification because it does not exclude any test path.

This is implementation evidence only. A real successful pull-request GitHub Actions run, followed
by the required master-push evidence, is still needed for **COMPLETE / VERIFIED** status.
