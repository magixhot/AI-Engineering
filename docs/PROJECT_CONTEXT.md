# AI-Engineering

<!-- canonical-project-state
{"schema_version":1,"completed_through":"AUTO-0019","active_milestone":"AUTO-0020","release_line":"v0.2.0"}
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
  validator, and Quality enforcement for six canonical documents.

GitHub is the external control/audit plane. The installed user-scoped worker is
the local bridge. OpenCode remains loopback-only for task classes that require
it. `quality_verify` is deterministic/read-only and does not require OpenCode.
AUTO-0019 recovery does not call either path.

## Current Objectives

- Preserve all completed foundations and AUTO-0001 through AUTO-0019 within
  their approved authority boundaries.
- Complete AUTO-0020-05 by reconciling the six governed documents with exact
  verified AUTO-0019 closure and active AUTO-0020 state.
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

AUTO-0020-04 Quality integration is verified on exact `master`
`e62f69d4db2f288bb072cfa38108d5872d5ebdb4` through pre-merge Quality #401
and push-triggered Quality #402. AUTO-0020-05 is the active documentation and
repository-wide evidence stage.

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
