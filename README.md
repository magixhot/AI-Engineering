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

**MCP-0002/0003, SDK-0001, TOOL-0001, REL-0001, CI-0001, and SAFE-0001 complete / verified for their approved scopes**

The official Python MCP SDK migration is complete. VS Code 1.132.1 and Antigravity interoperability are verified only for their recorded contracts. SDK-0001 Project Templates V1, the optional Python scaffold, and the installed `ai-engineering project create` CLI are implemented and verified. TOOL-0001 verifies all 15 existing Workspace, Git, and Python operations. REL-0001 verifies local wheel/sdist artifacts and isolated installed CLI behavior. CI-0001 runs Ruff, mypy, and full pytest on GitHub Actions/Linux/Python 3.11.

SAFE-0001 enforces `MCPConfig.workspace_root` for the active MCP Workspace handlers. Relative and in-root absolute paths are supported; traversal, outside-root absolute paths, link escapes, move escapes, and workspace-root move/delete are rejected according to the verified contract. This is a Workspace path-authorization boundary, not an OS-level sandbox or Git/Python subprocess sandbox.

Current Linux CI baseline: **pytest 99 passed, Ruff 0 findings, mypy 0 findings**. Windows-local SAFE verification: **pytest 98 passed, 1 permitted symlink-fixture skip**, Ruff 0, mypy 0.

GitHub Release creation and PyPI publishing have not been performed. This project does not claim general production readiness or compatibility with ChatGPT/OpenAI, Claude Desktop, or other MCP clients without separate evidence.

---

## Related Projects

* AI-Archive-Server (Reference Implementation)
* AI Infrastructure
* Engineering MCP Server

---

## License

This project is licensed under the terms specified in the LICENSE file.
