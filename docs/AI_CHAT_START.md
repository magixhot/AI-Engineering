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
9. The design/evidence document for the active milestone listed in `MASTER_INDEX.md`

After reading them, continue from `CURRENT_STATUS.md` and the current roadmap. `CURRENT_STATUS.md` is the authoritative current-state document.

## Current Working State

AI-Engineering has completed and verified the documentation foundation, MCP-0002, MCP-0003, SDK-0001 Project Templates V1, SDK-0001.1 Standalone Python Project Scaffold, SDK-0001.2 Project Template CLI, TOOL-0001 Core Tool Operation Verification, REL-0001 Local Distribution Verification, CI-0001 Quality Gate Automation, SAFE-0001 Workspace Path Safety Boundary, SAFE-0002 Git/Python Execution Safety, REL-0002 publication governance, REL-0003 v0.2.0 GitHub publication, AUTO-0001 Engineering Project Bootstrap, AUTO-0002 Project Documentation Synchronization, AUTO-0003 Documentation Ownership Initialization, AUTO-0004 Project Update/Migration Framework, AUTO-0005 Python Engineering Baseline V2 / first production migration, and AUTO-0006 Project Health/Readiness Audit for their approved scopes.

AUTO-0007 Engineering Project Reconciliation Plan is now the active milestone. AUTO-0007-01 design, AUTO-0007-02 planner implementation, and AUTO-0007-03 reconciliation invariants are complete/verified. AUTO-0007-04 Public CLI is active in PR #85 on branch `agent/auto-0007-04-public-cli`; current head is `cbb961dd4bd76547254de027cc380a354bbb8ca1` and Quality #150 is the current gate.

AUTO-0007 is explicitly read-only. The planner is deterministic and fail-closed. AUTO-0007-03 verifies manual-review/unsupported behavior, ordering, determinism, project-byte preservation, and Git invariants. AUTO-0007-04 exposes the planner through `ai-engineering project reconcile plan --project PATH` without adding apply/write authority, new migration edges, or publication behavior.

The immediate sequence is:

```text
Quality #150 SUCCESS
    → PR #85 ready/reviewed and merged
    → post-merge quality gate
    → AUTO-0007-05 Installed Distribution Verification
    → AUTO-0007-06 Final Reconciliation / Documentation
```

No later AUTO-0007 stage starts before the current stage passes its quality and post-merge gates.

## Engineering Guardrails

- Preserve originals.
- Extend, never replace.
- Documentation before implementation.
- Keep changes small, testable, and reviewable.
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
