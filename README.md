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
* AUTO-0004 through AUTO-0012 bounded migration/reconciliation planning, guarded execution, policy, approval, and execution evidence
* AUTO-0013 bounded read-only remote inspection/control transport
* AUTO-0014 local worker lifecycle supervision
* AUTO-0015 exact post-merge Quality verification
* AUTO-0016 workstation bootstrap/doctor and narrow read-only Quality relay
* AUTO-0017 project-state / roadmap reconciliation
* AUTO-0018 read-only control-plane reliability / observability hardening design
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

**AUTO-0018-01 design / contract active**

AUTO-0001 through AUTO-0017 are COMPLETE / VERIFIED for their approved scopes. The current automation stack includes permanent read-only reconciliation planning, guarded one-step apply, bounded multi-step orchestration, restrictive policy and optional explicit approval gates, deterministic execution evidence, bounded read-only remote control, local worker lifecycle supervision, exact post-merge Quality verification, portable workstation bootstrap/doctor behavior with a narrow read-only Quality relay, and reconciled canonical project-state documentation.

AUTO-0018 is the next selected milestone after AUTO-0017. AUTO-0018-01 is documentation-only and defines reliability/observability hardening for the existing read-only control plane: deterministic failure taxonomy, safe protocol-rejection diagnostics, low-noise liveness observability, bounded transport resilience, and stale-workspace diagnosis without automatic repository mutation.

AUTO-0018 does not authorize new remote write/apply task classes, automatic repository repair, workflow rerun/cancel/dispatch, service-control mutation, credential mutation, deployment/publication/release changes, or expanded OpenCode authority. Runtime implementation stages require explicit approval after the design gate.

The current exact post-merge Quality gate requires workflow `.github/workflows/quality.yml`, branch `master`, event `push`, the exact target `head_sha`, terminal `completed` status, and successful conclusion. Verification fails closed when the required evidence is missing or inconsistent.

SAFE-0001 enforces `MCPConfig.workspace_root` for the active MCP Workspace handlers. SAFE-0002 extends the active MCP authority-root policy to Git and path-taking Python operations. SAFE-0001 and SAFE-0002 are bounded authorization/execution contracts, not an operating-system sandbox.

The current published release is **AI-Engineering 0.2.0**, tag `v0.2.0`, targeting exact candidate commit `1faf14c121b7b5da7c8781e3de4e836f85838a76`. The approved release assets are `ai_engineering-0.2.0-py3-none-any.whl` and `ai_engineering-0.2.0.tar.gz`. Later engineering work on `master` does not retroactively change that immutable release. PyPI remains not approved and not published.

The immutable historical `v0.1.0` release remains preserved as prior release evidence. This project does not claim general production readiness or compatibility with ChatGPT/OpenAI, Claude Desktop, or other MCP clients without separate evidence.

---

## Related Projects

* AI-Archive-Server (Reference Implementation)
* AI Infrastructure
* Engineering MCP Server

---

## License

This project is licensed under the terms specified in the LICENSE file.
