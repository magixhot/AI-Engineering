# AI-Engineering

<!-- canonical-project-state
{"schema_version":2,"completed_through":"AUTO-0022","active_milestone":null,"active_stage":null,"active_state":"QUIESCENT","release_line":"v0.2.0"}
-->

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
* AUTO-0018 read-only control-plane reliability / observability hardening
* AUTO-0019 deterministic terminal recovery for aged unresolved claims
* AUTO-0020 offline canonical project-state coherence enforcement
* AUTO-0021 repository landing-state coherence
* AUTO-0022 GitHub control-surface coherence
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

**No active milestone — terminal QUIESCENT state**

AUTO-0001 through AUTO-0022 are COMPLETE / VERIFIED for their approved scopes. No successor milestone or stage is approved or active; AUTO-0023 is not inferred from numbering.

REL-0004-01 records the release-governance design. REL-0004-02 selects intended next version `0.3.0` from the exact compatibility inventory, with candidate preparation still blocked on MCP-version alignment, complete CLI help-tree exposure, release notes, and fresh readiness evidence. Neither stage changes the canonical AUTO `QUIESCENT` state or authorizes publication.

The remote control plane remains bounded to the read-only task classes `status`, `inspect`, `plan`, `diff`, and `quality_verify`. AUTO-0018 hardened that plane with deterministic failure taxonomy, bounded diagnostics, read retry/backoff, low-noise transport observability, and non-mutating stale-workspace guidance.

AUTO-0019 adds bounded terminal recovery for aged unresolved claims. Recovery performs immediate reinspection and publishes a separate terminal envelope; it does not call the executor, OpenCode, or `quality_verify`, and it never replays the claimed request.

AUTO-0020 introduced the strict typed canonical project-state manifest and deterministic offline/read-only coherence validator. AUTO-0021 document-set v2 governs exactly `README.md` plus the historical six canonical documents under `docs/`, with README first in validation order. Document-set v1 retains exact six-document compatibility; the validator checks strict markers and does not interpret narrative prose.

AUTO-0021 terminal closure merged as exact `master` `3e3c2b32d0caf677d55be9f090d4a1d236716e42`, confirmed by pre-merge Quality #417 and push-triggered Quality #418.

AUTO-0022 issue-body update evidence merged as exact `master` `d541d751828d9d95a828799b4e3f0345c396b103`, confirmed by pre-merge Quality #423 and push-triggered Quality #424. The issue body exactly matches the approved artifact with SHA-256 `c99ffa0b885926a64db30c451eeb910ad5dc9b6449f1c4833908d94c43dc859e`.

The REL-0004-02 decision baseline is exact `master` `113e848d950629d501b5fef6e0ccdf1279d9e7f8`; immutable tag `v0.2.0` remains at `1faf14c121b7b5da7c8781e3de4e836f85838a76`. Intended `0.3.0` is selected, but package metadata, candidate freeze, tag, assets, and publication remain separately gated.

The current automation scope does not authorize new remote write/apply task classes, automatic repository or documentation repair, workflow rerun/cancel/dispatch, service-control mutation, credential mutation, deployment/publication/release changes, or expanded OpenCode authority.

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
