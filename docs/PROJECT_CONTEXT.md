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
- STDIO entry point; and
- IDE integration models and adapters for Antigravity and VS Code.

## Vision

Build engineering infrastructure that lets humans and AI assistants collaborate using consistent,
testable tools, standards, workflows, and project structure.

## Current Objectives

- Maintain the completed MCP Foundation, official SDK migration, and MCP-0002 evidence.
- Keep Runtime and Registry boundaries intact while maintaining diagnostics for investigation.
- Maintain the verified SDK-0001 Project Templates V1 and optional SDK-0001.1 Standalone Python
  Project Scaffold baseline; consider CLI and broader automation only through separate approval.
- Record additional client interoperability only when separately scoped and supported by evidence.
- Expand automated tests where verification identifies a gap.

## Engineering Principles

- Documentation before implementation.
- Preserve originals; extend, never replace.
- Public API boundaries and explicit dependencies.
- Single responsibility and testability first.
- Small, reviewable, atomic changes.

## Reference Project

AI-Archive-Server is the Reference Project for engineering processes and documentation standards.
