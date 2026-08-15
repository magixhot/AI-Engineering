# AI-Engineering

**Status:** Active

**Version:** 0.2.0 (candidate / not yet published)

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

**REL-0003 0.2.0 candidate preparation over the complete / verified MCP, SDK-0001, TOOL-0001, REL-0001/0002, CI-0001, SAFE-0001/0002, AUTO-0001, and AUTO-0002 baseline**

The official Python MCP SDK migration is complete. VS Code 1.132.1 and Antigravity interoperability are verified only for their recorded contracts. SDK-0001 Project Templates V1, the optional Python scaffold, and the installed `ai-engineering project create` CLI are implemented and verified. AUTO-0001 adds the bounded `python-engineering` bootstrap API and installed `ai-engineering project bootstrap` CLI with fail-closed post-generation verification.

AUTO-0002 adds deterministic local project inspection and documentation synchronization for exactly `CURRENT_STATUS.md`, `MASTER_INDEX.md`, and `PROJECT_MAP.md`. Its installed `project docs check` and `plan` commands are read-only; `project docs apply` performs SHA-256 guarded, ownership-marker-bounded writes and post-apply verification. Missing or malformed ownership markers require manual review; V1 does not initialize markers automatically. The synchronization logic preserves the source document's LF/CRLF convention.

TOOL-0001 verifies all 15 existing Workspace, Git, and Python operations. REL-0001 verifies local wheel/sdist artifacts and isolated installed CLI behavior. The isolated-wheel test verifies installed create, bootstrap, and AUTO-0002 documentation check/plan/apply behavior outside the source checkout. CI-0001 runs Ruff, mypy, and full pytest on GitHub Actions/Linux/Python 3.11.

SAFE-0001 enforces `MCPConfig.workspace_root` for the active MCP Workspace handlers. Relative and in-root absolute paths are supported; traversal, outside-root absolute paths, link escapes, move escapes, and workspace-root move/delete are rejected according to the verified contract.

SAFE-0002 extends the active MCP authority-root policy to Git and path-taking Python operations. MCP Git requires `workspace_root` itself to be the Git repository top level, preventing parent-repository discovery above the authority root. Python syntax/package/test targets must resolve inside the root; outside, traversal, and supported link escapes are rejected. Authorized pytest runs use the current interpreter, workspace-root cwd, `shell=False`, `stdin=DEVNULL`, captured output, and a bounded timeout.

SAFE-0001 and SAFE-0002 are bounded authorization/execution contracts, not an operating-system sandbox. SAFE-0002 does not contain malicious code that is already authorized to execute inside the workspace.

The next package version has been explicitly selected as **0.2.0** under REL-0003. This is a candidate line only: no `v0.2.0` tag or GitHub Release has been created, no assets have been uploaded, and PyPI remains not approved/not published. Fresh candidate-specific Linux, Windows, distribution, installed-wheel, and release-note evidence is required before any publication proposal.

Current pre-candidate Linux CI baseline: **pytest 155 passed, Ruff 0 findings, mypy 0 findings in 79 source files**. Final pre-candidate Windows-local SAFE-0002 verification: **pytest 153 passed, 2 permitted symlink-fixture skips**, Ruff 0, mypy 0 in 79 source files; `git diff --check` passed and the working tree was clean. The Windows skips are limited to symlink fixtures blocked by process privilege (`WinError 1314`); equivalent link-escape coverage executes in Linux CI.

Git tag `v0.1.0` and GitHub Release `AI-Engineering 0.1.0` remain the latest published historical release for the approved release commit. Post-release AUTO-0001, AUTO-0002, SAFE-0002, and the 0.2.0 candidate preparation are not retroactively part of the immutable `v0.1.0` tag. PyPI remains not approved and not published. This project does not claim general production readiness or compatibility with ChatGPT/OpenAI, Claude Desktop, or other MCP clients without separate evidence.

---

## Related Projects

* AI-Archive-Server (Reference Implementation)
* AI Infrastructure
* Engineering MCP Server

---

## License

This project is licensed under the terms specified in the LICENSE file.
