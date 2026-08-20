# AI-Engineering

## Project Purpose

AI-Engineering is the engineering platform for the AI Infrastructure ecosystem. Its primary
implementation is the Engineering MCP Server: a standards-based interface through which AI
assistants can participate in engineering workflows.

## Current Architecture

The official Python `mcp` SDK remains the protocol and server boundary. AI-Engineering preserves its
internal Runtime and Registry architecture behind that boundary. The current verified architecture
also includes a layered engineering-automation control plane:

- MCP bootstrap, server integration, configuration, diagnostics, Runtime, Registry, Discovery, and
  workspace/Git/Python tool subsystems;
- STDIO entry point and IDE integration models/adapters;
- SDK-0001 project templates, standalone Python scaffold, and installed project-create CLI;
- AUTO-0001 through AUTO-0006 bounded project bootstrap, documentation, ownership, migration, and
  safe-step inspection/planning capabilities;
- AUTO-0007 permanent read-only engineering reconciliation planning;
- AUTO-0008 guarded one-step apply;
- AUTO-0009 bounded multi-step orchestration;
- AUTO-0010 restrictive policy gating;
- AUTO-0011 optional explicit single-candidate approval;
- AUTO-0012 deterministic execution receipts/evidence;
- AUTO-0013 bounded remote read-only inspection/control transport through the GitHub control channel;
- AUTO-0014 user-scoped local worker lifecycle supervision without expanding remote task authority;
- AUTO-0015 deterministic exact post-merge Quality verification for the exact merged `master` SHA;
- AUTO-0016 portable workstation bootstrap/doctor behavior plus the narrow read-only Quality relay;
- AUTO-0017 canonical project-state/roadmap reconciliation with a fresh hardening audit;
- AUTO-0018 typed control-plane diagnostics, bounded read resilience/observability, non-mutating stale-workspace diagnosis, and installed/E2E hardening evidence.

The control path is intentionally layered. GitHub is the external control/audit plane, the local
user-scoped worker is the execution bridge, and OpenCode remains a loopback-only local executor for
task classes that require it. The `quality_verify` path is deterministic and read-only and does not
require OpenCode.

## Vision

Build engineering infrastructure that lets humans and AI assistants collaborate using consistent,
testable tools, standards, workflows, and project structure.

## Current Objectives

- Maintain the completed MCP Foundation, SDK-0001, TOOL/SAFE/REL/CI foundations, and AUTO-0001
  through AUTO-0017 within their approved boundaries.
- Preserve AUTO-0007 as the permanent read-only reconciliation planner and keep AUTO-0008 through
  AUTO-0012 execution authority layered, explicit, guarded, and evidence-producing.
- Preserve AUTO-0013 as bounded remote read-only control transport and AUTO-0014 as local worker
  lifecycle supervision without adding remote mutation authority.
- Preserve AUTO-0015 exact post-merge Quality verification as fail-closed and read-only: workflow
  `.github/workflows/quality.yml`, branch `master`, event `push`, exact target `head_sha`, terminal
  `completed`, successful conclusion.
- Maintain AUTO-0016 portable workstation bootstrap/doctor behavior, canonical worker identity
  `ai-engineering-worker.service`, discovery-before-action rules, deterministic `READY` / `NOT_READY`
  semantics, and the narrow read-only Quality relay.
- Preserve AUTO-0018 typed failure taxonomy, bounded protocol-rejection diagnostics, bounded read retry/backoff, low-noise transport state observability, and fail-closed stale-workspace diagnosis without hidden repository repair.
- Keep workstation-local paths, usernames, credentials, tokens, private environment values, and
  unrelated machine metadata out of public repository evidence.
- Keep package installation, workstation repair, service-control mutation, credential mutation,
  workflow rerun/cancel/dispatch, deployment/publication, and new remote write/apply authority behind
  separately approved contracts.
- Complete AUTO-0018-06 final reconciliation through exact PR-head and post-merge Quality gates before declaring the milestone complete.

## Engineering Principles

- Documentation before implementation.
- Preserve originals; extend, never replace.
- Public API boundaries and explicit dependencies.
- Single responsibility and testability first.
- Small, reviewable, atomic changes.
- Evidence over stale narrative for canonical current-state documents.
- Fail closed at authority and verification boundaries.

## Release Boundary

The current published release remains Git tag `v0.2.0` and GitHub Release `AI-Engineering 0.2.0`,
targeting exact candidate `1faf14c121b7b5da7c8781e3de4e836f85838a76`. Later AUTO milestones
were implemented on `master` and are not retroactively inserted into that immutable release.
Historical `v0.1.0` remains preserved. PyPI remains not approved and not published.

## Current Engineering Baseline

The last verified merged baseline before AUTO-0018-06 is exact `master`
`b59f651b4719f8463b3cde1132980a1cf340ad10`, after AUTO-0018-05 installed/E2E evidence.

AUTO-0018-01 through AUTO-0018-05 are COMPLETE / VERIFIED for their approved scopes. The installed
worker demonstrated typed `expected_head_mismatch` failure without automatic repository mutation and
successful exact-head Quality verification after explicit operator synchronization. The successful
post-merge relay for the current baseline used Quality run `32379177746`, workflow id `334955954`,
branch/event `master` / `push`, exact head `b59f651b4719f8463b3cde1132980a1cf340ad10`,
`completed/success`, `satisfies_gate=true`, and clean pre/post evidence.

AUTO-0018-06 is now the active documentation/evidence reconciliation stage. It does not add runtime
behavior or authority. AUTO-0018 becomes COMPLETE / VERIFIED only after this stage passes exact
PR-head Quality, merges with expected-head protection, and the exact merged `master` push passes the
read-only post-merge Quality relay.

The milestone continues to forbid new remote write/apply authority, automatic repository repair,
workflow rerun/cancel/dispatch, service-control mutation, credential mutation,
publication/deployment/release changes, and expanded OpenCode authority.

## Reference Project

AI-Archive-Server remains the Reference Project for engineering processes and documentation
standards.
