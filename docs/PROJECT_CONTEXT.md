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
- AUTO-0001 typed engineering bootstrap API, verification, and installed bootstrap CLI; and
- AUTO-0002 read-only project inspection, deterministic documentation drift/planning, guarded apply,
  and installed documentation synchronization CLI.

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
- Preserve CI-0001, SAFE-0001, REL-0001/0002, and installed-distribution evidence.
- Keep marker initialization, broader document synchronization, Git automation, and project migration
  behind separate approved contracts.
- Record additional client interoperability only when separately scoped and supported by evidence.

## Engineering Principles

- Documentation before implementation.
- Preserve originals; extend, never replace.
- Public API boundaries and explicit dependencies.
- Single responsibility and testability first.
- Small, reviewable, atomic changes.

## Release Boundary

Git tag `v0.1.0` and GitHub Release `AI-Engineering 0.1.0` are published for the approved historical
release commit. AUTO-0001 and AUTO-0002 were implemented later on `master` and are not retroactively
part of that immutable release. PyPI remains not approved and not published.

## Reference Project

AI-Archive-Server is the Reference Project for engineering processes and documentation standards.
