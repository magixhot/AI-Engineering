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
- AUTO-0016 portable workstation bootstrap/doctor behavior plus the narrow read-only Quality relay.

The control path is intentionally layered. GitHub is the external control/audit plane, the local
user-scoped worker is the execution bridge, and OpenCode remains a loopback-only local executor for
task classes that require it. The `quality_verify` path is deterministic and read-only and does not
require OpenCode.

## Vision

Build engineering infrastructure that lets humans and AI assistants collaborate using consistent,
testable tools, standards, workflows, and project structure.

## Current Objectives

- Maintain the completed MCP Foundation, SDK-0001, TOOL/SAFE/REL/CI foundations, and AUTO-0001
  through AUTO-0016 within their approved boundaries.
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
- Keep workstation-local paths, usernames, credentials, tokens, private environment values, and
  unrelated machine metadata out of public repository evidence.
- Keep package installation, workstation repair, service-control mutation, credential mutation,
  workflow rerun/cancel/dispatch, deployment/publication, and new remote write/apply authority behind
  separately approved contracts.
- Finish AUTO-0017 final evidence before beginning any AUTO-0018 implementation.

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

The canonical engineering baseline is the current `master` state after AUTO-0016 plus the reconciled
AUTO-0017 project-state documentation. AUTO-0017-01 through AUTO-0017-04 are COMPLETE / VERIFIED.
AUTO-0017-05 Final Evidence / Next-Milestone Selection is the active final stage.

The fresh post-reconciliation audit selects **AUTO-0018 — Read-Only Control Plane Reliability /
Observability Hardening** as the next design candidate. The reason is operational evidence from the
existing read-only relay: malformed/non-canonical requests fail closed but can be silently skipped,
expected-head mismatch is correct but difficult to diagnose remotely, and normal polling is too quiet
to distinguish healthy idle operation from repeated protocol rejection.

AUTO-0018 selection does not preapprove implementation. It must begin with a separate design/approval
gate and must preserve the current read-only authority boundary unless a later explicit approval says
otherwise.

## Reference Project

AI-Archive-Server remains the Reference Project for engineering processes and documentation
standards.
