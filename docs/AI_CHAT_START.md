# AI-Engineering

## Chat Bootstrap

For a new or continued session, restore context in this order:

1. `README.md`
2. `PROJECT_CONTEXT.md`
3. `PROJECT_MAP.md`
4. `CURRENT_STATUS.md`
5. `ROADMAP.md`
6. `DECISIONS.md`
7. `CODING_STANDARDS.md`
8. `MASTER_INDEX.md`
9. The design/evidence document for the active milestone listed in `MASTER_INDEX.md`, if one exists

After reading them, continue from `CURRENT_STATUS.md` and the current roadmap. `CURRENT_STATUS.md` is the authoritative current-state document.

## Current Working State

AI-Engineering has completed and verified the documentation foundation, MCP-0002, MCP-0003, SDK-0001 Project Templates V1, SDK-0001.1 Standalone Python Project Scaffold, SDK-0001.2 Project Template CLI, TOOL-0001 Core Tool Operation Verification, REL-0001 Local Distribution Verification, CI-0001 Quality Gate Automation, SAFE-0001 Workspace Path Safety Boundary, SAFE-0002 Git/Python Execution Safety, REL-0002 publication governance, REL-0003 v0.2.0 GitHub publication, AUTO-0001 Engineering Project Bootstrap, AUTO-0002 Project Documentation Synchronization, AUTO-0003 Documentation Ownership Initialization, AUTO-0004 Project Update/Migration Framework, AUTO-0005 Python Engineering Baseline V2 / first production migration, AUTO-0006 Project Health/Readiness Audit, and AUTO-0007 Engineering Project Reconciliation Plan for their approved scopes.

AUTO-0007 is COMPLETE / VERIFIED. Stages 01–06 are closed. The final verified master baseline is `53236558772b857de260817394308aec5eaa5ab2`. AUTO-0007-04 Public CLI was merged in PR #85 and verified by Quality #157 plus post-merge #160. AUTO-0007-05 Installed Distribution Verification was merged in PR #86 and verified by Quality #161 plus post-merge #162. AUTO-0007-06 Final Reconciliation / Documentation was merged in PR #87 and verified by Quality #163 plus post-merge #164.

AUTO-0007 is explicitly read-only. The planner is deterministic and fail-closed. AUTO-0007-03 verifies manual-review/unsupported behavior, ordering, determinism, project-byte preservation, and Git invariants. AUTO-0007-04 exposes the planner through `ai-engineering project reconcile plan --project PATH` without adding apply/write authority, new migration edges, or publication behavior. AUTO-0007-05 verifies the installed-wheel/public CLI path. AUTO-0007-06 reconciles documentation with the final verified repository state.

## Current State

The repository is at a clean milestone boundary. No next implementation milestone is currently approved. Future work must begin with a separate design/contract and evidence plan rather than being inferred from completion of AUTO-0007.

```text
AUTO-0007 COMPLETE / VERIFIED
        ↓
clean master baseline
        ↓
next milestone requires separate design / contract / evidence
```

## Engineering Guardrails

- Preserve originals.
- Extend, never replace.
- Documentation before implementation.
- Keep changes small, testable, deterministic, and reviewable.
- Do not redesign existing architecture without a separate approved contract.
- Keep environment-specific absolute paths out of project code and documentation contracts.
- Make compatibility and security claims only from recorded evidence.
- Treat published tags/releases as immutable historical evidence; post-release `master` work does not retroactively change them.
- Do not expand writable documents, ownership semantics, migration scope, or publication scope without a separate approved contract.
- Preserve AUTO-0007 read-only, deterministic, fail-closed boundaries unless explicitly redesigned.
- Do not expand SAFE-0002 claims to OS sandboxing, arbitrary-command containment, or future Git/Python tools without a separate contract and evidence.

## Project Context

AI-Engineering is the Engineering MCP Server and engineering-automation foundation for the AI Infrastructure ecosystem. It uses the official Python MCP SDK at the protocol/server boundary while preserving the internal Runtime and Registry architecture.

Reference project: AI-Archive-Server.
