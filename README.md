# AI-Engineering

**Status:** Active

**Version:** 0.2.0

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
* AUTO-0003 Documentation Ownership Initialization (`ai-engineering project docs ownership check/plan/apply`)
* Local distribution verification
* Automated quality gates
* MCP Workspace path safety boundary
* MCP Git/Python execution safety boundary

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

**AUTO-0003 complete / verified — post-AUTO-0003 roadmap audit active**

The official Python MCP SDK migration is complete. VS Code 1.132.1 and Antigravity interoperability are verified only for their recorded contracts. SDK-0001 Project Templates V1, the optional Python scaffold, and the installed `ai-engineering project create` CLI are implemented and verified. AUTO-0001 adds the bounded `python-engineering` bootstrap API and installed `ai-engineering project bootstrap` CLI with fail-closed post-generation verification.

AUTO-0002 provides deterministic local project inspection and documentation synchronization for exactly `CURRENT_STATUS.md`, `MASTER_INDEX.md`, and `PROJECT_MAP.md`. Its installed `project docs check` and `plan` commands are read-only; `project docs apply` performs SHA-256 guarded, ownership-marker-bounded writes and post-apply verification.

AUTO-0003 provides the explicit ownership-initialization bridge for those same three documents. When the approved marker pair is completely absent and initialization is deterministic, `project docs ownership plan/apply` can initialize the managed section while preserving human-authored content and Git HEAD/index state. Partial, duplicate, malformed, unsupported, missing-document, mixed-newline, and stale-plan states fail closed. AUTO-0002 remains unchanged and never initializes ownership implicitly.

TOOL-0001 verifies all 15 existing Workspace, Git, and Python operations. REL-0001 verifies wheel/sdist artifacts and isolated installed CLI behavior. CI-0001 runs Ruff, mypy, and full pytest on GitHub Actions/Linux/Python 3.11. Current post-AUTO-0003 Quality #94 baseline is 174 passed, Ruff clean, and mypy clean in 83 source files.

SAFE-0001 enforces `MCPConfig.workspace_root` for the active MCP Workspace handlers. SAFE-0002 extends the active MCP authority-root policy to Git and path-taking Python operations. SAFE-0001 and SAFE-0002 are bounded authorization/execution contracts, not an operating-system sandbox.

The current published release is **AI-Engineering 0.2.0**, tag `v0.2.0`, targeting exact candidate commit `1faf14c121b7b5da7c8781e3de4e836f85838a76`. The approved release assets are `ai_engineering-0.2.0-py3-none-any.whl` and `ai_engineering-0.2.0.tar.gz`. Post-release engineering work on `master`, including AUTO-0003, does not retroactively change that immutable release. PyPI remains not approved and not published.

The immutable historical `v0.1.0` release remains preserved as prior release evidence. This project does not claim general production readiness or compatibility with ChatGPT/OpenAI, Claude Desktop, or other MCP clients without separate evidence.

---

## Related Projects

* AI-Archive-Server (Reference Implementation)
* AI Infrastructure
* Engineering MCP Server

---

## License

This project is licensed under the terms specified in the LICENSE file.
