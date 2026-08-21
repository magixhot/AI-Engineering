# AI-Engineering

<!-- canonical-project-state
{"schema_version":2,"completed_through":"AUTO-0021","active_milestone":"AUTO-0022","release_line":"v0.2.0"}
-->

## Project Purpose

AI-Engineering is the engineering platform for the AI Infrastructure ecosystem.
Its primary implementation is the Engineering MCP Server: a standards-based
interface through which AI assistants can participate in engineering workflows.

## Current Architecture

The official Python `mcp` SDK remains the protocol/server boundary. The
internal Runtime and Registry architecture remains behind it. The verified
platform includes:

- MCP bootstrap, configuration, diagnostics, discovery, runtime, registry,
  workspace, Git, Python, STDIO, and IDE integrations;
- SDK-0001 project templates, standalone scaffold, and project-create CLI;
- AUTO-0001 through AUTO-0006 bounded bootstrap, documentation, ownership,
  migration, and safe-step inspection/planning;
- AUTO-0007 read-only reconciliation planning;
- AUTO-0008 guarded one-step apply;
- AUTO-0009 bounded multi-step orchestration;
- AUTO-0010 restriction-only policy;
- AUTO-0011 optional explicit single-candidate approval;
- AUTO-0012 deterministic execution receipts;
- AUTO-0013 bounded GitHub-channel read-only control transport;
- AUTO-0014 user-scoped local worker lifecycle supervision;
- AUTO-0015 deterministic exact post-merge Quality verification;
- AUTO-0016 portable workstation bootstrap/doctor plus the narrow read-only
  Quality relay;
- AUTO-0017 canonical project-state reconciliation and hardening audit;
- AUTO-0018 typed control-plane failures, bounded read resilience,
  low-noise observability, and non-mutating stale-workspace diagnosis;
- AUTO-0019 bounded no-replay terminal recovery for aged unresolved claims;
- AUTO-0020 a strict project-state manifest, offline/read-only coherence
  validator, document-set v2 Quality enforcement for seven canonical
  documents, and exact document-set v1 compatibility.

GitHub is the external control/audit plane. The installed user-scoped worker is
the local bridge. OpenCode remains loopback-only for task classes that require
it. `quality_verify` is deterministic/read-only and does not require OpenCode.
AUTO-0019 recovery does not call either path.

## Current Objectives

- Preserve all completed foundations and AUTO-0001 through AUTO-0021 within
  their approved authority boundaries.
- Complete AUTO-0022 design-first coherence of exact external issue #130
  without adding protocol or worker authority.
- Keep `docs/CANONICAL_PROJECT_STATE.json` strict, minimal, and typed.
- Keep coherence validation deterministic, offline, read-only, fail-closed,
  and limited to declared document projections.
- Keep workstation-local paths, usernames, credentials, tokens, private
  environment values, and unrelated machine metadata out of public evidence.
- Keep package installation, workstation repair, service-control mutation,
  workflow rerun/cancel/dispatch, deployment/publication, and new remote
  write/apply authority behind separately approved contracts.

## Engineering Principles

- Documentation before implementation.
- Preserve originals; extend rather than replace public contracts.
- Public API boundaries and explicit dependencies.
- Single responsibility and testability first.
- Small, reviewable, atomic changes.
- Typed evidence over stale narrative for current-state claims.
- Fail closed at authority and verification boundaries.

## Verified Baselines

AUTO-0019 final reconciliation is verified on exact `master`
`c287e5cceef4e72148de7674f4095fedb78bd302` through push-triggered Quality
#394 (run id `32484748127`).

AUTO-0020-06 final audit is verified on exact `master`
`143ccdcbd9b39e89188cbad63577b0dc1e353941` through pre-merge Quality #405
and push-triggered Quality #406. AUTO-0020 is COMPLETE / VERIFIED.

The AUTO-0020 terminal state is verified on exact `master`
`c72c79a477de630f50532a454e11d513e9727a79` through Quality #407/#408.
AUTO-0021-01 merged through PR #198 as exact `master`
`8121e3d1b2b38c4088e32a7128c58686e459542a` after Quality #409/#410.
AUTO-0021-02 merged through PR #199 as exact `master`
`8363f50e86470092cdccf116e8dc00dcc8f9d43c` after Quality #411/#412.
AUTO-0021-03 merged through PR #200 as exact `master`
`ad30d3155ee1561e0c6e37c3e4ffd5996b55dd72` after Quality #413/#414.
AUTO-0021-04 merged through PR #201 as exact `master`
`965e2722ee9d232d526e716edbdabd6d9f8a0197` after Quality #415/#416.
AUTO-0021 terminal closure merged through PR #202 as exact `master`
`3e3c2b32d0caf677d55be9f090d4a1d236716e42` after Quality #417/#418.
AUTO-0021 is COMPLETE / VERIFIED. AUTO-0022-01 is the active design stage.

Document-set v2 adds only repository-root `README.md` to the exact governed
set while document-set v1 retains its historical six-document compatibility.
AUTO-0022 governs only the body coherence of open control issue #130. It does
not alter the offline repository-byte contract or add generic issue automation.

## Release Boundary

Git tag `v0.2.0` and GitHub Release `AI-Engineering 0.2.0` remain the
published historical boundary, targeting exact candidate
`1faf14c121b7b5da7c8781e3de4e836f85838a76`. Later AUTO milestones are on
`master` and are not retroactively inserted into that immutable release.
Historical `v0.1.0` remains preserved. PyPI remains not approved/not
published.

## Reference Project

AI-Archive-Server remains the Reference Project for engineering processes and
documentation standards.
