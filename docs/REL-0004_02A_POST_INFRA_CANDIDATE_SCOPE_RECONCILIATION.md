# REL-0004-02A — Post-INFRA Candidate-Scope Reconciliation

**Status:** SCOPE RECONCILED / CANDIDATE NOT PREPARED

## Purpose

Reconcile the REL-0004-02 compatibility/version decision with the verified
INFRA-0001 delta that landed afterwards, before any REL-0004-03 version metadata,
release-note, or candidate-preparation work.

This stage is decision/documentation-only. It does not edit package/runtime
version metadata, freeze a candidate, create or move a tag, create a GitHub
Release, upload assets, publish to a registry, change credentials, or expand
runtime authority.

## Exact Baselines

Published historical boundary:

```text
release:  AI-Engineering 0.2.0
tag:      v0.2.0
tag_sha:  1faf14c121b7b5da7c8781e3de4e836f85838a76
PyPI:     NOT APPROVED / NOT PUBLISHED
```

REL-0004-02 decision baseline:

```text
113e848d950629d501b5fef6e0ccdf1279d9e7f8
```

Post-INFRA verified master used by this reconciliation:

```text
5672a661d5e34540fd476266a9c3c25d3aa00e45
```

The exact REL-0004-02-baseline-to-post-INFRA comparison is `ahead_by=42`,
`behind_by=0`. The exact v0.2.0-to-post-INFRA comparison is `ahead_by=447`,
`behind_by=0`.

A later accidental documentation placeholder write was immediately removed in a
separate compensating commit before this branch was created. The branch base is
therefore exact `master` `d4b1c76c10d9519484eb76ee6428d5219e700094`,
whose repository tree restores the intended post-INFRA content before this
REL-0004-02A document.

## Why Reconciliation Is Required

REL-0004-02 selected `0.3.0` before INFRA-0001 existed on master and bounded the
candidate scope to the verified post-v0.2.0 work through AUTO-0022 plus release
governance. INFRA-0001 subsequently added verified repository configuration,
governed local-agent roles, local-first routing/shadow modules, workstation
bootstrap/verification scripts, tests, and documentation.

Preparing a candidate directly from current master without classifying this
additional delta would make the release notes and compatibility decision no
longer describe the exact candidate lineage.

## Post-INFRA Surface Classification

### Package metadata and dependencies

`pyproject.toml` remains version `0.2.0`, Python `>=3.11`, dependency
`mcp>=1.27,<1.28`, and console entry point
`ai-engineering = ai_engineering.public_cli:main`.

INFRA-0001 does not add or change a package dependency, Python floor, console
entry point, build backend, or package-discovery rule.

### Importable Python surface

INFRA-0001 adds:

```text
src/ai_engineering/local_agent_routing.py
src/ai_engineering/local_agent_shadow.py
```

Because setuptools discovers the `src/ai_engineering` package automatically,
these modules are included in a normal source/wheel build unless a later
packaging change explicitly excludes them.

They are additive operational modules. This reconciliation does **not** promote
them to a promised stable public Python API. Release notes must identify them as
internal/operational local-agent support rather than general user-facing API.

### Public CLI and MCP behavior

INFRA-0001 does not add a new `ai-engineering` CLI route and does not modify the
published MCP tool registry or SAFE authority boundaries.

The two REL-0004-02 release blockers therefore remain unchanged:

1. align the active MCP initialize version with the selected package version;
2. make the public CLI parent help tree expose the already-supported
   `reconcile approve/run` and `workstation doctor` routes.

### Repository-local operational surface

INFRA-0001 adds repository/workstation-only operational assets including:

```text
AGENTS.md
opencode.json
.opencode/agents/{repo-reader,implementer,verifier}.md
scripts/local-opencode-run.sh
scripts/bootstrap-local-agent.sh
scripts/verify-local-agent.sh
```

These establish a governed OpenCode/Ollama local execution layer. They do not
grant package users, MCP clients, or remote control callers additional
authority. Automatic cloud fallback, protected-branch mutation, merge,
publication, credential mutation, and release authority remain forbidden.

GPU acceleration is not a release requirement. The verified baseline accepts
CPU-only `ollama/qwen3:4b` when the deterministic local-agent checks pass.

### Distribution and release evidence impact

The new Python modules are expected to be present in wheel/sdist package
contents through normal package discovery. The repository-local OpenCode agent
configuration and workstation shell scripts are not claimed as installed CLI
interfaces merely because they exist in the source repository.

REL-0004-04 readiness must therefore explicitly inspect the built artifacts and
verify the intended boundary rather than infer it:

- confirm the two `local_agent_*.py` modules have the expected wheel/sdist
  presence;
- confirm no new console-script entry point is introduced;
- confirm installed public CLI/MCP behavior remains bounded to the separately
  documented release interfaces;
- preserve workstation-local INFRA evidence separately from installed-package
  compatibility claims.

## Candidate-Scope Decision

**Decision: INCLUDE INFRA-0001 in the intended 0.3.0 candidate lineage as
verified additive operational/internal scope.**

Rationale:

1. current verified master already contains INFRA-0001;
2. its two Python modules naturally enter the distribution under existing
   setuptools discovery;
3. excluding them would require a new packaging or history/candidate-boundary
   change, which is neither required by evidence nor authorized by REL-0004-02;
4. INFRA-0001 is complete/verified and does not expand public CLI/MCP authority;
5. the added surfaces are compatible with the existing pre-1.0 `0.3.0`
   rationale when release notes clearly distinguish public contracts from
   operational/internal modules.

The intended next version remains **`0.3.0`** and intended tag remains
**`v0.3.0`**.

No claim is made that every importable post-v0.2.0 module is permanently stable.

## Revised REL-0004-03 Scope

After this stage is verified, REL-0004-03 may be separately approved to perform
only bounded candidate preparation on the then-current exact master:

1. establish one explicit `0.3.0` version contract across package metadata,
   lockfile, MCP configuration, active SDK initialize metadata, documentation,
   and expected tag;
2. correct the public CLI parent help tree for `reconcile approve/run` and
   `workstation doctor` without changing their established behavior/exit codes;
3. draft exact v0.3.0 release notes covering the previously approved
   post-v0.2.0 scope **plus verified INFRA-0001**, with INFRA classified as
   operational/internal local-agent integration;
4. add/adjust release tests necessary for the exact version/help/distribution
   boundaries;
5. keep tag creation, GitHub Release/assets, registry publication, credentials,
   and publishing automation unchanged and unauthorized.

REL-0004-03 still does not itself authorize publication.

## Revised REL-0004-04 Evidence Requirement

In addition to the existing Linux/full-suite, distribution, isolated-wheel,
installed MCP/CLI, Windows-local, and asset-hash requirements, readiness must
cover the exact INFRA distribution boundary described above. Workstation-local
OpenCode/Ollama verification may support operational evidence, but it does not
replace installed-wheel or MCP/CLI release evidence.

## Namespace and Authority Boundary

The canonical AUTO state remains:

```text
completed_through: AUTO-0022
active_milestone:  null
active_stage:      null
active_state:      QUIESCENT
release_line:      v0.2.0
```

REL-0004 remains a separate governance namespace. This stage does not fabricate
AUTO-0023 or change the canonical release line before a separately approved and
completed publication action.

## Result

**REL-0004-02A result: `0.3.0` RECONFIRMED / INFRA-0001 INCLUDED AS VERIFIED
OPERATIONAL-INTERNAL SCOPE / CANDIDATE NOT PREPARED / NOT PUBLISHED.**

REL-0004-03 remains separately approval-gated after exact PR-head Quality,
expected-head-protected merge, and exact push-triggered post-merge Quality for
this reconciliation stage.
