# REL-0004-03 — 0.3.0 Candidate Preparation

**Status:** IMPLEMENTATION / CANDIDATE NOT YET VERIFIED

## Purpose

Prepare the bounded 0.3.0 release candidate selected by REL-0004-02 and
reconciled after INFRA-0001 by REL-0004-02A. This stage aligns version metadata,
corrects two audited release-readiness blockers, drafts release notes, and adds
regression coverage. It does not publish anything.

## Exact start

REL-0004-03 starts from exact verified `master`:

```text
9c5a52e640fad9acc9892960763f68a4b39146a3
```

REL-0004-02A completed on that SHA through push-triggered Quality #457.

## Approved changes

### Version contract

The selected version is exactly `0.3.0`, with intended future tag `v0.3.0`.
Candidate preparation aligns:

- `pyproject.toml` package version;
- the editable project record in `uv.lock`;
- `ai_engineering.version.VERSION`;
- `MCPConfig.server_version`;
- the version passed to the active MCP SDK `Server` constructor.

Runtime MCP versioning is sourced from the explicit runtime version constant
through `MCPConfig`; regression tests additionally require package metadata and
lockfile equality.

### MCP initialize blocker

The active SDK adapter no longer contains the stale literal `0.1.0` version.
`EngineeringMCPServer` passes `MCPConfig.server_version` into `SDKAdapter`, which
passes that value into the SDK `Server` constructor.

REL-0004-04 must still verify the exact installed-wheel MCP initialize response;
this implementation stage does not substitute source-level assertions for that
installed evidence.

### Public CLI help blocker

The public wrapper now exposes its wrapper-owned routes at the relevant parent
help boundaries:

```text
ai-engineering --help
ai-engineering project reconcile --help
ai-engineering workstation --help
```

The help hierarchy includes `reconcile approve`, `reconcile run`, and
`workstation doctor`. Existing execution routing for approve/run/doctor remains
unchanged; no new command authority is introduced.

### Release notes

`docs/REL-0004_0.3.0_RELEASE_NOTES.md` describes the intended candidate scope,
including verified INFRA-0001 as operational/internal local-agent integration
rather than a stable public Python API promise.

## Preserved boundaries

REL-0004-03 does not:

- create or move `v0.3.0`;
- create a GitHub Release;
- upload wheel/sdist assets;
- publish to TestPyPI or PyPI;
- change credentials or secrets;
- change publishing workflow permissions;
- expand MCP tools, local-agent authority, GitHub mutation authority, or
  protected-branch authority;
- change the canonical AUTO state from AUTO-0022 / QUIESCENT.

## Completion rule

REL-0004-03 is complete only after:

1. exact PR-head Quality succeeds;
2. expected-head-protected merge succeeds;
3. push-triggered Quality succeeds on the exact resulting `master` SHA.

The resulting exact master may then be treated as the prepared candidate for
REL-0004-04 readiness evidence. REL-0004-04 remains separately approval-gated,
and no publication action is implied by REL-0004-03 completion.
