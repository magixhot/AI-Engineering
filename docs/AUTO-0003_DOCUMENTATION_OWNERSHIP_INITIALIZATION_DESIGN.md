# AUTO-0003 — Documentation Ownership Initialization Design

**Status:** DESIGN / PROPOSED
**Milestone:** M3 — Engineering Automation
**Scope:** safe initialization of AUTO-0002 machine-owned sections in approved project documents

## 1. Purpose

AUTO-0003 defines the missing initialization layer between AUTO-0001 project bootstrap and AUTO-0002 project documentation synchronization.

AUTO-0002 intentionally fails closed when required ownership markers are missing or malformed. That behavior remains correct for arbitrary existing projects because AUTO-0002 must never guess where machine ownership begins. AUTO-0003 introduces a separate, explicit workflow that may initialize those ownership boundaries when a document is eligible and the insertion can be proven safe.

AUTO-0003 is not a general Markdown rewriter. It is a bounded ownership-initialization workflow whose only mutation is the insertion of approved AUTO-0002 managed sections into approved documents while preserving all pre-existing human-authored content.

The design follows the project rule: **documentation before implementation**.

## 2. Relationship to Existing Contracts

AUTO-0003 must preserve these established contracts:

- **SDK-0001 V1** remains authoritative for generated project-document structure.
- **AUTO-0001** remains authoritative for project bootstrap and its verification contract.
- **AUTO-0002** remains authoritative for project inspection, drift detection, synchronization planning, guarded apply, marker parsing, and managed-section content.
- **SAFE-0001** and **SAFE-0002** remain unrelated MCP authorization/execution boundaries and are not weakened or expanded by this local documentation workflow.
- Existing Git, Python, MCP, distribution, release, and CI behavior remains unchanged unless a later task explicitly scopes a change.

AUTO-0003 must reuse AUTO-0002 marker names and managed-section semantics rather than inventing a parallel ownership scheme.

## 3. Objective

Provide a deterministic workflow that:

1. inspects one approved project document;
2. classifies its AUTO-0002 ownership state;
3. determines whether safe marker initialization is possible;
4. produces an explicit initialization plan without mutation;
5. applies only an approved plan when explicitly requested;
6. preserves all original human content;
7. verifies the initialized document after write;
8. enables a subsequent AUTO-0002 check/plan/apply cycle without silently altering unrelated content.

The initial implementation is local-only and must not require network access.

## 4. V1 Eligible Document Set

AUTO-0003 V1 may initialize ownership only for the same three documents that AUTO-0002 V1 is allowed to synchronize:

- `CURRENT_STATUS.md`
- `PROJECT_MAP.md`
- `MASTER_INDEX.md`

AUTO-0003 must not initialize ownership markers in any other document.

In particular, V1 does not modify:

- `README.md`;
- `AI_CHAT_START.md`;
- `PROJECT_CONTEXT.md`;
- `ROADMAP.md`;
- `DECISIONS.md`;
- `CODING_STANDARDS.md`;
- arbitrary files under `docs/`.

Expanding the eligible set requires a separately approved design change.

## 5. Ownership-State Model

AUTO-0003 must classify each eligible document into a finite state before planning mutation.

Required V1 states:

- `initialized` — the exact approved AUTO-0002 start/end marker pair exists once and is structurally valid;
- `missing` — neither approved marker exists;
- `partial` — exactly one marker exists;
- `duplicate` — one or both markers occur more than once;
- `malformed` — markers exist but ordering/nesting is invalid;
- `unsupported` — document shape prevents deterministic safe initialization;
- `missing_document` — the approved target file does not exist.

Only the `missing` state may be eligible for automatic initialization in V1.

`partial`, `duplicate`, `malformed`, `unsupported`, and `missing_document` must fail closed and require manual review.

An already `initialized` document must produce a no-op result; AUTO-0003 must never add a second managed section.

## 6. Exact Marker Compatibility

AUTO-0003 must use the exact marker pairs recognized by AUTO-0002 for each document.

Implementation must source marker definitions from one shared authority so AUTO-0002 and AUTO-0003 cannot drift independently.

AUTO-0003 must not introduce version-specific aliases, fuzzy matching, case-insensitive matching, or heuristic marker repair in V1.

## 7. Preserve-Originals Contract

The central AUTO-0003 rule is:

**All original human-authored document content must survive initialization byte-for-byte except for the minimal deterministic insertion boundary itself.**

This means:

- no existing heading may be renamed;
- no paragraph may be rewritten;
- no whitespace inside existing lines may be normalized;
- no Markdown table may be reformatted;
- no content may be reordered;
- no existing line ending convention may be converted;
- no trailing content may be deleted;
- no semantic claim may be changed during initialization.

The only permitted mutation is insertion of the approved managed section at an approved deterministic insertion point.

## 8. Line-Ending Contract

AUTO-0003 must preserve the source document's newline convention.

If the document is consistently CRLF, inserted content must use CRLF. If the document is consistently LF, inserted content must use LF.

Mixed-newline documents are not safely auto-initializable in V1 and must be classified `unsupported` or `manual_review_required`.

Automated verification must exercise both LF and CRLF fixtures.

## 9. Insertion-Point Contract

AUTO-0003 may initialize only at a document-specific insertion point that is deterministic and structurally bounded.

The implementation design for each document must define exactly one accepted insertion rule before mutation code lands.

V1 rules must satisfy all of the following:

- the rule depends only on deterministic local document structure;
- the rule does not require semantic interpretation by an LLM;
- the rule does not search for approximate prose meaning;
- failure to locate the exact insertion anchor is manual review, not fallback placement;
- the inserted section may not split a fenced code block, HTML block, Markdown table row, list item, or other structured block;
- insertion at end-of-file is allowed only when that location is explicitly approved for the document type.

No generic "best place" heuristic is permitted.

## 10. Managed Section Seed Content

Initialization must insert a complete AUTO-0002 managed section, not empty markers whose meaning depends on a later write.

Seed content must be generated through the same deterministic AUTO-0002 rendering authority used for normal synchronization planning, based on the current `ProjectStateSnapshot` and approved local evidence.

AUTO-0003 must not duplicate rendering logic for `PROJECT_MAP.md`, `MASTER_INDEX.md`, or `CURRENT_STATUS.md`.

If AUTO-0002 cannot deterministically render the section for current project state, initialization fails closed.

## 11. Read-Only Planning API

AUTO-0003 must separate planning from mutation.

Proposed models:

```python
@dataclass(frozen=True)
class DocumentationOwnershipInitializationRequest:
    project_root: Path
    documents: tuple[str, ...]


@dataclass(frozen=True)
class DocumentationOwnershipInitializationUpdate:
    document: str
    original_sha256: str
    replacement_content: str


@dataclass(frozen=True)
class DocumentationOwnershipInitializationPlan:
    project_root: Path
    updates: tuple[DocumentationOwnershipInitializationUpdate, ...]
    manual_review: tuple[str, ...]
```

Recommended entry point:

```python
plan_documentation_ownership_initialization(
    request: DocumentationOwnershipInitializationRequest,
) -> DocumentationOwnershipInitializationPlan
```

Exact type names may be refined during implementation, but the public boundary must remain explicit, typed, deterministic, and read-only.

## 12. Plan Contract

For every proposed write, the plan must contain:

- approved document name;
- digest of the exact original bytes/content used for planning;
- complete replacement content;
- deterministic ownership-state classification;
- no hidden mutation intent outside the replacement content.

Planning must perform no writes, Git stage/commit operations, subprocess execution, dependency installation, network access, or project-code execution.

Identical project state and document bytes must produce an identical ordered plan.

## 13. Apply Contract

Recommended entry point:

```python
apply_documentation_ownership_initialization(
    plan: DocumentationOwnershipInitializationPlan,
) -> DocumentationOwnershipInitializationResult
```

Before any write, AUTO-0003 must verify that every target still matches the `original_sha256` captured by the plan.

V1 apply is all-or-nothing for the selected update set: if any target is stale, unsupported, or requires manual review, no target is written.

This is stricter than per-file best effort and prevents partial ownership initialization across the three-document set.

## 14. Manual-Review Boundary

AUTO-0003 must refuse automatic mutation when any of the following is true:

- one marker exists without its pair;
- duplicate markers exist;
- markers are out of order or nested unexpectedly;
- a different/legacy marker-like region could be confused with the approved section;
- the insertion anchor is missing or ambiguous;
- the document contains mixed newline conventions that cannot be preserved deterministically;
- deterministic AUTO-0002 seed rendering is unavailable;
- the document changed after planning;
- the target is outside the approved V1 set;
- the target path resolves outside the requested project root;
- the document is unreadable or unwritable;
- any other condition makes preserve-originals guarantees unprovable.

Manual review must be surfaced explicitly and must not be represented as successful initialization.

## 15. Idempotency Contract

AUTO-0003 must be idempotent.

After a successful initialization:

- a second initialization plan for the same unchanged project must contain no writes;
- the document must classify as `initialized`;
- no duplicate markers may be introduced;
- AUTO-0002 must be able to parse the managed section normally.

Idempotency is required automated evidence, not an implementation preference.

## 16. AUTO-0002 Handoff Contract

Successful AUTO-0003 initialization is complete only if the resulting document is valid input for AUTO-0002.

Verification must prove:

1. AUTO-0002 recognizes the initialized markers;
2. the managed section is rendered according to current deterministic project state;
3. an immediate AUTO-0002 `check` does not report `ownership markers missing or malformed` for initialized targets;
4. any remaining AUTO-0002 drift is ordinary supported drift, not initialization corruption;
5. human-owned prefix/suffix content remains preserved through a subsequent AUTO-0002 plan/apply cycle.

AUTO-0003 must not weaken AUTO-0002's existing fail-closed behavior for projects that have not explicitly run initialization.

## 17. CLI Direction

A later implementation task may expose an additive CLI shape such as:

```text
ai-engineering project docs init --project PATH
```

Optional future flags may include explicit document selection or a non-mutating plan mode, but exact syntax is not approved by this design task.

Any CLI must call the public AUTO-0003 API and must not duplicate marker classification, rendering, planning, or apply logic.

Mutation must require an explicit command/action; ordinary AUTO-0002 `check` and `plan` remain read-only and must never initialize ownership implicitly.

## 18. Error Model

AUTO-0003 should define a bounded domain error model, either extending the documentation synchronization domain or introducing a narrowly related initialization error type.

Required failure classes include:

- invalid project root;
- target outside project root;
- unsupported document;
- missing document;
- partial markers;
- duplicate markers;
- malformed markers;
- unsupported document structure;
- ambiguous/missing insertion anchor;
- mixed newline convention;
- deterministic seed-render failure;
- stale plan / digest mismatch;
- write failure;
- verification failure;
- manual review required;
- unknown internal failure.

Expected domain failures must be controlled and testable.

## 19. Path and Portability Rules

AUTO-0003 must use the same project-root and portability rules as AUTO-0002.

Generated managed sections must contain only approved project-relative portable paths where paths are represented.

The workflow must never embed machine-specific roots such as:

- `C:\\Users\\...`;
- `D:\\...`;
- OneDrive-specific roots;
- CI checkout roots;
- virtual-environment paths.

Windows and Linux behavior must be equivalent except for environment limitations already explicitly classified by the project.

## 20. Security Boundary

AUTO-0003 is not a sandbox.

V1 reads approved local files, derives deterministic project state through existing inspection boundaries, and writes approved Markdown documents only after explicit apply.

AUTO-0003 must not:

- execute project code;
- run tests as part of initialization;
- invoke arbitrary shell commands;
- install dependencies;
- access credentials;
- contact remote services;
- perform Git staging/commit/push;
- create branches or pull requests;
- publish releases or packages.

## 21. Git Boundary

AUTO-0003 never changes Git metadata or repository history automatically.

It must not stage, commit, reset, checkout, branch, push, or otherwise mutate Git state beyond ordinary working-tree file modifications caused by approved Markdown writes.

Automated verification must prove Git HEAD and index/staging remain unchanged after successful initialization.

## 22. Automated Verification Matrix

Implementation must provide evidence for at least:

| Row | Required evidence |
|---|---|
| Missing markers | eligible approved document produces deterministic initialization plan |
| Already initialized | no-op / no duplicate markers |
| Partial markers | fail closed / manual review |
| Duplicate markers | fail closed / manual review |
| Malformed ordering | fail closed / manual review |
| Unsupported document | rejected |
| Approved targets only | only the three AUTO-0002 documents are eligible |
| Deterministic insertion | identical input produces identical replacement |
| Human-content preservation | original content outside insertion is byte-preserved |
| LF portability | LF source remains LF |
| CRLF portability | CRLF source remains CRLF |
| Mixed newline input | fail closed |
| Digest guard | changed target invalidates plan before writes |
| Multi-document atomicity | one stale/manual-review target prevents all writes |
| Idempotency | second run plans no changes |
| AUTO-0002 compatibility | initialized document is parsed and synchronized normally |
| Seed rendering reuse | AUTO-0003 does not diverge from AUTO-0002 managed-section content |
| Project-root containment | outside-root targets are rejected |
| Git invariants | HEAD/staging unchanged |
| No execution/network | no subprocess/project-code/network behavior introduced |
| Existing AUTO-0002 tests | remain green unchanged unless explicitly extended |
| Existing AUTO-0001/SDK behavior | remains green |

Repository-wide pytest, Ruff, mypy, and `git diff --check` must remain green.

## 23. Implementation Boundaries

The smallest implementation should separate:

- ownership-state classification;
- document-specific insertion-anchor resolution;
- deterministic initialization planning;
- digest-guarded atomic apply;
- post-write verification and AUTO-0002 compatibility checks;
- CLI adaptation, if later approved.

Shared marker definitions and managed-section rendering should be factored from AUTO-0002 only as much as required to establish one authority. Unrelated synchronization, MCP, Git, Python, release, CI, or bootstrap refactoring is out of scope.

## 24. Non-Goals

AUTO-0003 V1 explicitly excludes:

- automatically repairing malformed or partial markers;
- migrating unknown legacy ownership schemes;
- free-form LLM document rewriting;
- semantic interpretation of arbitrary Markdown;
- changing human-authored status or roadmap claims;
- whole-document normalization;
- initializing ownership in documents outside the approved three-file set;
- changing AUTO-0002 writable scope;
- making AUTO-0002 `check` or `plan` mutate files;
- Git staging, commit, branch, push, or PR automation;
- project bootstrap or project creation;
- dependency installation;
- project-code or test execution;
- network access;
- GitHub release/publishing behavior;
- PyPI publication;
- secrets or credentials;
- general production-readiness claims.

## 25. Proposed Atomic Implementation Sequence

After design approval:

### AUTO-0003-02 — Ownership Classification and Planning

Implement shared marker authority, ownership-state classification, document-specific safe insertion anchors, deterministic replacement planning, LF/CRLF handling, and tests. No writes and no CLI changes.

### AUTO-0003-03 — Guarded Atomic Apply and AUTO-0002 Handoff

Implement all-or-nothing digest-guarded writes, post-write verification, idempotency evidence, Git invariants, and AUTO-0002 compatibility checks. No CLI yet.

### AUTO-0003-04 — CLI and Installed-Distribution Verification

Expose the approved initialization workflow through the installed console script and extend isolated-wheel verification. Exact CLI contract must be frozen before implementation.

Each task must remain atomic and may stop if a preserve-originals or compatibility gap is discovered.

## 26. Completion Criteria

AUTO-0003 is complete only when:

- this design is approved;
- the eligible set remains exactly the three AUTO-0002 V1 writable documents;
- only completely missing marker pairs are auto-initializable;
- partial/duplicate/malformed/unsupported states fail closed;
- insertion points are deterministic and document-specific;
- all original human content is preserved outside the insertion boundary;
- LF and CRLF are preserved and mixed-newline input fails closed;
- seed content reuses AUTO-0002 deterministic rendering authority;
- planning precedes mutation;
- stale plans fail closed;
- multi-document apply is atomic in V1;
- repeated initialization is idempotent;
- resulting documents are valid AUTO-0002 inputs;
- no Git metadata/history mutation occurs;
- no project code, subprocess, dependency install, remote service, publication, or credential behavior is introduced;
- repository quality gates remain green;
- documentation records verified behavior and remaining boundaries.
