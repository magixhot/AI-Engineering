# AI-Engineering

**Status:** Active

**Version:** 0.1.0

---

## Overview

AI-Engineering is the engineering foundation of the AI Infrastructure ecosystem.

Its purpose is to provide the tools, standards, workflows and automation required to build, maintain and evolve AI projects in a consistent, reproducible and scalable way.

The first major component of this repository is the **Engineering MCP Server**, which enables AI assistants to interact with engineering projects through the Model Context Protocol (MCP) and uses the official Python `mcp` SDK.

---

## Mission

Build engineering infrastructure that allows humans and AI to work together using the same standards, workflows and project structure.

---

## Project Scope

Current scope includes:

* Engineering MCP Server
* Workspace Tools
* Git Tools
* Python Development Tools
* Documentation Templates
* Engineering Standards
* Project Bootstrap Tools
* SDK-0001 Project Templates V1
* SDK-0001.1 Standalone Python Project Scaffold
* SDK-0001.2 Project Template CLI (`ai-engineering project create`)
* AUTO-0001 Engineering Project Bootstrap (`ai-engineering project bootstrap`)
* AUTO-0002 Project Documentation Synchronization (`ai-engineering project docs check/plan/apply`)
* Local distribution verification
* Automated quality gates
* MCP Workspace path safety boundary

Future scope may include:

* Additional SDK capabilities
* Code Generators
* Automation Services
* Additional Engineering Utilities

---

## Project Principles

* Documentation before implementation.
* Preserve originals.
* Extend, never replace.
* Public API first.
* Atomic development.
* Testability.
* Reproducibility.
* Long-term maintainability.

---

## Repository Structure

```text
docs/          Project documentation
scripts/       Utility scripts
src/           Source code
tests/         Unit, integration, and release verification tests
```

---

## Getting Started

Every new engineering session starts with:

> Read `docs/AI_CHAT_START.md` and continue.

This document contains everything required to restore the current project context.

---

## Development Status

Current phase:

**MCP-0002/0003, SDK-0001, TOOL-0001, REL-0001/0002, CI-0001, SAFE-0001, AUTO-0001, and AUTO-0002 complete / verified for their approved scopes**

The official Python MCP SDK migration is complete. VS Code 1.132.1 and Antigravity interoperability are verified only for their recorded contracts. SDK-0001 Project Templates V1, the optional Python scaffold, and the installed `ai-engineering project create` CLI are implemented and verified. AUTO-0001 adds the bounded `python-engineering` bootstrap API and installed `ai-engineering project bootstrap` CLI with fail-closed post-generation verification.

AUTO-0002 adds deterministic local project inspection and documentation synchronization for exactly `CURRENT_STATUS.md`, `MASTER_INDEX.md`, and `PROJECT_MAP.md`. Its installed `project docs check` and `plan` commands are read-only; `project docs apply` performs SHA-256 guarded, ownership-marker-bounded writes and post-apply verification. Missing or malformed ownership markers require manual review; V1 does not initialize markers automatically.

TOOL-0001 verifies all 15 existing Workspace, Git, and Python operations. REL-0001 verifies local wheel/sdist artifacts and isolated installed CLI behavior. The isolated-wheel test now verifies installed create, bootstrap, and AUTO-0002 documentation check/plan/apply behavior outside the source checkout. CI-0001 runs Ruff, mypy, and full pytest on GitHub Actions/Linux/Python 3.11.

SAFE-0001 enforces `MCPConfig.workspace_root` for the active MCP Workspace handlers. Relative and in-root absolute paths are supported; traversal, outside-root absolute paths, link escapes, move escapes, and workspace-root move/delete are rejected according to the verified contract. This is a Workspace path-authorization boundary, not an OS-level sandbox or Git/Python subprocess sandbox.

Current Linux CI baseline: **pytest 142 passed, Ruff 0 findings, mypy 0 findings in 77 source files**. Windows-local SAFE verification remains **pytest 98 passed, 1 permitted symlink-fixture skip**, Ruff 0, mypy 0.

Git tag `v0.1.0` and GitHub Release `AI-Engineering 0.1.0` are published for the approved release commit. Post-release AUTO-0001 and AUTO-0002 work is verified on `master` but is not retroactively part of the immutable `v0.1.0` tag. PyPI remains not approved and not published. This project does not claim general production readiness or compatibility with ChatGPT/OpenAI, Claude Desktop, or other MCP clients without separate evidence.

---

## Related Projects

* AI-Archive-Server (Reference Implementation)
* AI Infrastructure
* Engineering MCP Server

---

## License

This project is licensed under the terms specified in the LICENSE file.
