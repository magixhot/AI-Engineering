# AI-Engineering

## Project Purpose

AI-Engineering is the engineering platform for the AI Infrastructure ecosystem. Its primary
implementation is the Engineering MCP Server: a standards-based interface through which AI
assistants can participate in engineering workflows.

## Current Architecture

The official Python `mcp` SDK is the protocol and server boundary. AI-Engineering preserves its
internal Runtime and Registry architecture behind that boundary. The implemented architecture
includes:

- MCP bootstrap, server integration, configuration, and diagnostics;
- Runtime, Registry, and Discovery;
- Workspace, Git, and Python tool subsystems;
- STDIO entry point;
- IDE integration models and adapters for Antigravity and VS Code;
- SDK-0001 standalone project templates, Python scaffold, and installed create CLI;
- AUTO-0001 typed engineering bootstrap API, verification, and installed bootstrap CLI;
- AUTO-0002 read-only project inspection, deterministic documentation drift/planning, guarded apply,
  and installed documentation synchronization CLI; and
- AUTO-0003 ownership-state classification, deterministic ownership initialization planning, guarded
  atomic apply, AUTO-0002 handoff verification, and installed ownership CLI.

## Vision

Build engineering infrastructure that lets humans and AI assistants collaborate using consistent,
testable tools, standards, workflows, and project structure.

## Current Objectives

- Maintain the completed MCP Foundation, official SDK migration, and MCP-0002/0003 evidence.
- Keep Runtime and Registry boundaries intact while maintaining diagnostics for investigation.
- Maintain the verified SDK-0001 Project Templates V1 public Python API, optional SDK-0001.1
  Standalone Python Project Scaffold, and SDK-0001.2 CLI frontend (`ai-engineering project create`).
- Maintain AUTO-0001's bounded `python-engineering` bootstrap API and installed
  `ai-engineering project bootstrap` workflow without changing SDK-0001 default behavior.
- Maintain AUTO-0002's exact three-document writable set, ownership-marker boundary, deterministic
  inspection/planning, guarded apply, and installed `project docs check/plan/apply` behavior.
- Maintain AUTO-0003's exact same three-document eligibility boundary, fail-closed ownership-state
  model, deterministic initialization, digest guards, Git invariants, and installed
  `project docs ownership check/plan/apply` behavior.
- Preserve CI-0001, SAFE-0001, SAFE-0002, REL-0001/0002/0003, and installed-distribution evidence.
- Keep broader document synchronization, Git automation, project migration/update behavior,
  additional bootstrap profiles, and new execution surfaces behind separate approved contracts.
- Record additional client interoperability only when separately scoped and supported by evidence.

## Engineering Principles

- Documentation before implementation.
- Preserve originals; extend, never replace.
- Public API boundaries and explicit dependencies.
- Single responsibility and testability first.
- Small, reviewable, atomic changes.

## Release Boundary

The current published release is Git tag `v0.2.0` and GitHub Release `AI-Engineering 0.2.0`, targeting
exact candidate `1faf14c121b7b5da7c8781e3de4e836f85838a76`. AUTO-0003 was implemented later on `master`
and is not retroactively part of that immutable release. Historical `v0.1.0` remains preserved.
PyPI remains not approved and not published.

## Current Engineering Baseline

Post-AUTO-0003 Quality #94 passed on `master` commit
`a3a8716f861e568d0444f49aebc5c0ea6c7c4fc9`: pytest 174 passed, Ruff clean, and mypy clean in 83
source files. The next milestone must be selected through a fresh roadmap audit rather than by
implicitly expanding existing AUTO, SAFE, MCP, or release boundaries.

## Reference Project

AI-Archive-Server is the Reference Project for engineering processes and documentation standards.
