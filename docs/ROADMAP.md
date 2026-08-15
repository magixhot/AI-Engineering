# AI-Engineering Roadmap

## Completed

### Sprint 0 — Documentation Foundation

**Status:** COMPLETED

The core project documentation foundation has been established.

## Implemented / Verified

### Sprint 1 — MCP Foundation

**Status:** IMPLEMENTED / VERIFIED

Implemented repository components include MCP bootstrap, the official SDK adapter, Composite
Registry, Runtime, Discovery, STDIO, diagnostics, and registered Workspace/Git/Python tool
subsystems. Runtime and Discovery remain repository subsystems, not steps in the active SDK request
path.

### Official Python MCP SDK Migration

**Status:** COMPLETE

The official Python MCP SDK is integrated as the protocol/server boundary. MCP-0002 automated
contracts, VS Code 1.132.1 manual interoperability, and the separately recorded Antigravity contract
are verified. This does not replace the internal Runtime, Registry, or Discovery subsystems.

### SDK-0001 Project Templates V1, SDK-0001.1 Python Scaffold, and SDK-0001.2 CLI

**Status:** COMPLETE / VERIFIED

The document-first standalone project template, optional generic Python scaffold, and installed
`ai-engineering project create` frontend are implemented and verified.

### AUTO-0001 Engineering Project Bootstrap

**Status:** COMPLETE / VERIFIED

AUTO-0001 adds the bounded `python-engineering` bootstrap workflow over SDK-0001, including typed
API, fail-closed post-generation verification, installed `ai-engineering project bootstrap`, and
isolated-wheel evidence.

### AUTO-0002 Project Documentation Synchronization

**Status:** COMPLETE / VERIFIED

AUTO-0002 adds deterministic local project inspection, documentation drift detection, explicit
synchronization planning, SHA-256 guarded ownership-preserving apply, post-apply verification, and
the installed commands:

```text
ai-engineering project docs check --project PATH
ai-engineering project docs plan --project PATH
ai-engineering project docs apply --project PATH
```

V1 writes only machine-owned sections of `CURRENT_STATUS.md`, `MASTER_INDEX.md`, and
`PROJECT_MAP.md`. Missing or malformed ownership markers require manual review. The workflow does not
stage or commit Git changes, execute project code, install dependencies, contact remote services, or
initialize markers automatically.

## Current Priority

Preserve the verified MCP, SDK-0001, SAFE-0001, CI-0001, release, AUTO-0001, and AUTO-0002 contracts.
Select the next engineering milestone from a fresh post-AUTO-0002 roadmap audit rather than extending
the writable documentation scope implicitly.

## Planned

### Client and IDE Interoperability

Validate interoperability with additional MCP clients and IDE integration surfaces. VS Code 1.132.1
and Antigravity are already verified for their recorded contracts; ChatGPT/OpenAI, Claude Desktop,
and other clients remain unverified.

### Future Engineering Capabilities

Potential future work includes a separately designed AUTO-0002 ownership-marker initialization flow,
additional bootstrap profiles, broader project update/migration behavior, Git/Python execution safety
boundaries, publication expansion, and additional engineering automation. None of these are implied by
AUTO-0002 V1 and each requires its own approved contract.
