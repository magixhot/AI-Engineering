# REL-0002-02 — Release Readiness Audit

**Status:** READY FOR EXPLICIT PUBLICATION DECISION
**Audit scope:** prepare an exact release candidate without publishing it

## Candidate

- Repository: `magixhot/AI-Engineering`
- Candidate branch: canonical `master`
- Candidate commit: `73929bd15fa7637db8162aac199697582bb25e67`
- Package version: `0.1.0`
- Candidate tag: `v0.1.0`
- Candidate GitHub Release title: `AI-Engineering 0.1.0`

The candidate commit is intentionally frozen before this audit branch. This audit PR must not be
merged before the publication decision, because merging it would move `master` and create a new
candidate SHA.

## Repository Publication State

At audit time:

- existing Git tags: none;
- existing GitHub Releases: none;
- PyPI publication: not approved and not performed;
- no release tag or release object was created by this audit.

## Version Consistency

`pyproject.toml` declares:

- distribution name: `ai-engineering`;
- version: `0.1.0`;
- Python requirement: `>=3.11`;
- console script: `ai-engineering = ai_engineering.cli:main`.

The REL-0001 distribution test on the candidate commit verifies:

- wheel filename pattern `ai_engineering-0.1.0-*.whl`;
- sdist filename `ai_engineering-0.1.0.tar.gz`;
- wheel METADATA name `ai-engineering`;
- wheel/installed version `0.1.0`;
- Python requirement `>=3.11`;
- MCP dependency range;
- installed console-script entry point.

Therefore candidate version `0.1.0` and proposed tag `v0.1.0` are consistent.

## Quality Evidence for Exact Candidate SHA

GitHub Actions Quality run `31884264560` executed on exact candidate commit
`73929bd15fa7637db8162aac199697582bb25e67` and completed successfully.

The workflow includes:

- locked dependency synchronization;
- Ruff;
- mypy;
- full pytest;
- REL-0001 distribution build/content/isolated-install verification as part of full pytest.

Current Linux baseline is 99 passing tests with Ruff and mypy passing.

Windows-local SAFE verification for the same release line records 98 passed / 1 permitted
symlink-fixture skip, Ruff 0, and mypy 0. The Windows skip is caused by missing local symlink
creation privilege (`WinError 1314`), while Linux CI executes the link fixture.

## Artifact Candidate Policy

If GitHub Release publication is explicitly approved, release assets should be rebuilt from the
exact candidate commit and must match the REL-0001 verified artifact contract.

Expected asset names:

- `ai_engineering-0.1.0-py3-none-any.whl` (or the exact REL-0001-compatible wheel filename emitted
  by the approved build backend for version 0.1.0);
- `ai_engineering-0.1.0.tar.gz`.

Artifacts must not be taken from an arbitrary developer `dist/` directory. They should be produced
from the frozen candidate commit, inspected, and attached only after publication approval.

## Included Release Scope

The candidate release line includes the verified engineering baseline accumulated before the
candidate SHA:

- official Python MCP SDK stdio/server boundary;
- MCP-0002 SDK boundary verification;
- MCP-0003 Antigravity interoperability evidence;
- VS Code 1.132.1 and Antigravity verification for their recorded contracts;
- all 15 Workspace/Git/Python tools with TOOL-0001 operation verification;
- corrected MCP snake_case dispatch mapping;
- corrected Git porcelain status-column handling;
- SDK-0001 Project Templates V1;
- SDK-0001.1 optional standalone Python scaffold;
- SDK-0001.2 installed `ai-engineering project create` CLI;
- REL-0001 wheel/sdist and isolated-install verification;
- CI-0001 GitHub Actions quality gates;
- SAFE-0001 MCP Workspace path safety boundary.

## Explicit Non-Claims

The candidate does not claim:

- general production readiness;
- compatibility with ChatGPT/OpenAI, Claude Desktop, or other unverified MCP clients;
- OS-level filesystem sandboxing;
- Git/Python subprocess containment by SAFE-0001;
- offline package build/install support;
- PyPI availability;
- automated release publishing.

## Publication Decision Matrix

| Surface | Audit state | Required next action |
|---|---|---|
| Git tag `v0.1.0` | READY / NOT CREATED | explicit user approval |
| GitHub Release `AI-Engineering 0.1.0` | READY TO PREPARE / NOT CREATED | explicit user approval after tag decision |
| GitHub Release assets | READY TO REBUILD / NOT UPLOADED | rebuild from candidate and verify after approval |
| PyPI | NOT APPROVED | separate ownership/authentication/support decision |

## Blockers

No technical blocker was found for preparing a `v0.1.0` Git tag and GitHub Release from the
candidate commit.

Publication is blocked only by the deliberate REL-0002 approval gate.

PyPI remains blocked by policy decisions and is not part of the proposed first publication.

## Recommended First Publication Boundary

If publication is approved, the smallest safe first public release is:

1. create immutable tag `v0.1.0` on exact candidate SHA
   `73929bd15fa7637db8162aac199697582bb25e67`;
2. rebuild and verify wheel/sdist from that tagged commit;
3. create GitHub Release `AI-Engineering 0.1.0` from `v0.1.0`;
4. attach the verified wheel and sdist;
5. use `RELEASE_NOTES_0.1.0_DRAFT.md` as the reviewed release-note basis;
6. do not publish to PyPI.

No publication action is authorized by this audit document itself.
