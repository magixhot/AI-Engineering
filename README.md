# AI-Engineering

**Status:** Active

**Version:** 0.1.0

---

## Overview

AI-Engineering is the engineering foundation of the AI Infrastructure ecosystem.

Its purpose is to provide the tools, standards, workflows and automation required to build, maintain and evolve AI projects in a consistent, reproducible and scalable way.

The first major component of this repository is the **Engineering MCP Server**, which enables AI assistants to interact with engineering projects through the Model Context Protocol (MCP) and now uses the official Python `mcp` SDK.

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

Future scope may include:

* SDK
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
tests/         Unit and integration tests
```

---

## Getting Started

Every new engineering session starts with:

> Read `docs/AI_CHAT_START.md` and continue.

This document contains everything required to restore the current project context.

---

## Development Status

Current phase:

**MCP-0002, MCP-0003, SDK-0001, TOOL-0001, and REL-0001 complete; planning CI**

The official Python MCP SDK migration and its MCP-0002 verification are complete. VS Code 1.132.1
and Antigravity interoperability are verified for their recorded stdio contracts. SDK-0001 Project
Templates V1 plus the optional SDK-0001.1 Standalone Python Project Scaffold are implemented and
verified. SDK-0001.2 adds the implemented `ai-engineering project create` CLI over that public API,
including the optional scaffold flow. TOOL-0001 Core Tool Operation Verification is COMPLETE /
VERIFIED for all 15 existing Workspace, Git, and Python operations. Current quality gates are
pytest: 90 passed, Ruff: 0 findings, and mypy: 0 findings. REL-0001 local distribution verification
is COMPLETE / VERIFIED: wheel and sdist contracts, an isolated wheel install, and the installed CLI
are verified for release line 0.1.0. GitHub Release creation, PyPI publishing, and CI have not been
performed. The next direction is CI planning only. This does not claim general production readiness
or compatibility with ChatGPT/OpenAI, Claude Desktop, or other MCP clients.

---

## Related Projects

* AI-Archive-Server (Reference Implementation)
* AI Infrastructure
* Engineering MCP Server

---

## License

This project is licensed under the terms specified in the LICENSE file.
