# REL-0004-04 — 0.3.0 Release Readiness Evidence

**Status:** EVIDENCE COLLECTION IN PROGRESS / NOT READY FOR PUBLICATION

## Purpose

Collect the exact release-readiness evidence required by REL-0004 after the
0.3.0 candidate preparation completed. This stage verifies the candidate; it
does not publish it.

## Exact start

REL-0004-04 starts from exact verified `master`:

```text
17e5c0bc869bff788332423aec57658449fc2f6a
```

That SHA completed REL-0004-03 through push-triggered Quality #462.

## Required evidence

The stage requires all of the following before a readiness decision:

1. exact PR-head Quality success, including canonical coherence, Ruff, mypy,
   and the complete pytest suite on Linux/Python 3.11;
2. wheel and sdist build/content inspection;
3. isolated wheel installation and public CLI help verification;
4. installed-wheel MCP STDIO initialize returning server version `0.3.0`;
5. explicit INFRA-0001 distribution-boundary verification:
   - `ai_engineering/local_agent_routing.py` is present in wheel and sdist;
   - `ai_engineering/local_agent_shadow.py` is present in wheel and sdist;
   - exactly one package-owned console entry point exists:
     `ai-engineering = ai_engineering.public_cli:main`;
6. fresh Windows-local verification against the exact PR head using the
   supported Python floor when available;
7. wheel/sdist asset names and SHA-256 hashes recorded before any publication
   approval;
8. expected-head-protected merge followed by push-triggered Quality success on
   the exact resulting `master`.

## Deterministic distribution gate

`tests/release/test_rel_0004_distribution_boundary.py` performs the artifact,
isolated-install, CLI, installed MCP, INFRA distribution-boundary, and SHA-256
evidence checks. Run it with output visible:

```text
uv run python -m pytest -s tests/release/test_rel_0004_distribution_boundary.py
```

Successful output includes:

```text
REL0004_WHEEL=<wheel name>
REL0004_WHEEL_SHA256=<sha256>
REL0004_SDIST=<sdist name>
REL0004_SDIST_SHA256=<sha256>
REL0004_INSTALLED_MCP=PASS
REL0004_INFRA_DISTRIBUTION_BOUNDARY=PASS
```

The hashes are evidence for the artifacts built by that exact verification run;
they do not create or upload release assets.

## Windows-local evidence procedure

On Windows PowerShell, from a clean checkout of the exact PR head:

```powershell
git rev-parse HEAD
git status --porcelain
py -3.11 --version
uv sync --locked --group dev
uv run --python 3.11 python -m pytest -s tests/release/test_rel_0004_distribution_boundary.py
uv run --python 3.11 python -m pytest
```

If Python 3.11 is unavailable locally, that fact must be recorded explicitly;
using another Python version may provide supplemental compatibility evidence but
does not silently satisfy the required supported-floor Windows check.

The final evidence record must include the exact tested HEAD, Python version,
clean-worktree result, distribution-gate result and hashes, and full-suite
result.

## Current evidence

Repository implementation of the readiness gate is present on branch
`rel/0004-04-release-readiness`.

Linux PR-head Quality: **PENDING**.

Windows-local exact-head verification: **PENDING**.

Artifact names/hashes: **PENDING exact verification run**.

## Preserved boundaries

REL-0004-04 does not:

- create or move tag `v0.3.0`;
- create a GitHub Release;
- upload wheel/sdist assets;
- publish to TestPyPI or PyPI;
- change credentials, secrets, signing, provenance, or workflow permissions;
- expand AUTO, MCP, local-agent, GitHub mutation, or protected-branch authority.

The canonical AUTO state remains AUTO-0022 / QUIESCENT until separately
authorized release reconciliation changes it.

## Completion rule

REL-0004-04 may be declared `COMPLETE / VERIFIED / READY FOR PUBLICATION
DECISION` only after the required Linux, distribution, installed-wheel, Windows,
exact-head, and post-merge evidence is recorded and all required gates pass.

Completion of this stage authorizes only proceeding to the separately approved
REL-0004-05 publication decision. It does not itself authorize a tag, GitHub
Release, asset upload, or PyPI publication.
