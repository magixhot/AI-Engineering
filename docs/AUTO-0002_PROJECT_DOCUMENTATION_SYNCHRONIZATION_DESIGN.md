# AUTO-0002 — Project Documentation Synchronization Design

**Status:** DESIGN / PROPOSED
**Milestone:** M3 — Engineering Automation
**Scope:** bounded inspection, drift detection, deterministic planning, and controlled synchronization for approved project documentation

## 1. Purpose

AUTO-0002 defines the next engineering-automation layer after AUTO-0001.

AUTO-0001 can create and verify a new engineering project. AUTO-0002 addresses what happens after
that project evolves: project documentation can become stale relative to the actual repository
state. The goal is to make that drift visible and, for a narrowly approved document set, produce and
apply deterministic synchronization changes.

AUTO-0002 is not an AI free-form documentation writer. It is a bounded repository-state
reconciliation workflow with explicit inputs, explicit writable targets, deterministic output, and
preserve-originals safety.

The design follows the project rule: **documentation before implementation**.

## 2. Relationship to Existing Contracts

AUTO-0002 must preserve these established contracts:

- **SDK-0001 V1** remains the authoritative contract for generated project documentation structure.
- **AUTO-0001** remains the authoritative project-bootstrap API/CLI and verification contract.
- **SAFE-0001** remains limited to MCP Workspace path authorization and is not redefined by this
  local project-documentation workflow.
- Existing Git, Python, MCP, distribution, release, and CI behavior must remain unchanged unless a
  later task explicitly scopes a change.

AUTO-0002 must consume repository state through a public inspection boundary rather than by coupling
synchronization logic directly to CLI formatting or generator internals.

## 3. Objective

Provide a deterministic workflow that:

1. inspects a project root;
2. derives a bounded project-state snapshot;
3. compares that snapshot with approved project documentation;
4. reports drift without mutation by default;
5. builds an explicit synchronization plan;
6. applies only approved deterministic changes when requested;
7. verifies that applied changes match the plan.

The initial implementation is local-only and must not require network access.

## 4. V1 Writable Document Set

AUTO-0002 V1 permits synchronization of exactly three documents:

- `CURRENT_STATUS.md`
- `PROJECT_MAP.md`
- `MASTER_INDEX.md`

The workflow must not modify any other document in V1.

In particular, V1 does not automatically rewrite:

- `README.md`;
- `AI_CHAT_START.md`;
- `PROJECT_CONTEXT.md`;
- `ROADMAP.md`;
- `DECISIONS.md`;
- `CODING_STANDARDS.md`;
- arbitrary files under `docs/`.

Additional writable documents require a separately approved design extension because each document
has different authority, semantics, and risk.

## 5. Source-of-Truth Boundary

AUTO-0002 may derive facts only from approved local repository evidence.

V1 inspection sources are:

- filesystem paths beneath the project root;
- Git repository state when present;
- `pyproject.toml` metadata when present;
- existing approved project documents;
- configured project-document locations.

V1 must not infer facts from network services, GitHub, package indexes, environment-specific home
paths, IDE state, shell history, or LLM-generated guesses.

Observed facts and documentation claims must remain distinguishable in the data model.

## 6. Public Inspection API

The proposed inspection API is additive and read-only:

```python
@dataclass(frozen=True)
class ProjectInspectionRequest:
    project_root: Path


@dataclass(frozen=True)
class ProjectFileEntry:
    relative_path: str
    kind: str


@dataclass(frozen=True)
class ProjectStateSnapshot:
    project_root: Path
    files: tuple[ProjectFileEntry, ...]
    git_repository: bool
    git_branch: str | None
    git_head: str | None
    package_name: str | None
    project_name: str | None
```

Recommended entry point:

```python
inspect_project_state(request: ProjectInspectionRequest) -> ProjectStateSnapshot
```

Exact model fields may be refined during implementation, but V1 inspection must remain bounded,
portable, read-only, and deterministic for the same repository state.

## 7. Drift Model

AUTO-0002 must represent drift explicitly rather than immediately rewriting files.

Proposed model:

```python
@dataclass(frozen=True)
class DocumentationDrift:
    document: str
    category: str
    expected: str
    observed: str


@dataclass(frozen=True)
class DocumentationDriftReport:
    project: ProjectStateSnapshot
    items: tuple[DocumentationDrift, ...]
```

V1 drift categories must be finite and documented. Initial categories should include:

- missing repository path in `PROJECT_MAP.md`;
- stale repository path in `PROJECT_MAP.md`;
- missing indexed document in `MASTER_INDEX.md`;
- stale indexed document in `MASTER_INDEX.md`;
- stale bounded implementation-status facts in `CURRENT_STATUS.md`;
- unsupported or unverifiable claim requiring manual review.

The system must not classify semantic disagreement as safely auto-fixable unless the value comes from
an approved deterministic source.

## 8. Detection Contract

Recommended entry point:

```python
detect_documentation_drift(
    snapshot: ProjectStateSnapshot,
) -> DocumentationDriftReport
```

Detection is read-only and must not edit files, stage Git changes, or execute project code.

For an identical project tree, Git state, metadata, and document contents, drift detection must
produce an identical ordered report.

## 9. Synchronization Plan

Mutation requires an explicit plan object produced before writes occur.

```python
@dataclass(frozen=True)
class DocumentationUpdate:
    document: str
    original_sha256: str
    replacement_content: str


@dataclass(frozen=True)
class DocumentationSyncPlan:
    project_root: Path
    updates: tuple[DocumentationUpdate, ...]
```

Recommended entry point:

```python
plan_documentation_sync(
    report: DocumentationDriftReport,
) -> DocumentationSyncPlan
```

The plan must contain the complete replacement content for each file and the digest of the exact
original content on which that replacement was based.

This creates a compare-and-apply boundary and prevents silent mutation of documents that changed
between inspection and application.

## 10. Apply Contract

Recommended entry point:

```python
apply_documentation_sync(
    plan: DocumentationSyncPlan,
) -> DocumentationSyncResult
```

Before writing each document, AUTO-0002 must verify that the current file digest still matches the
plan's `original_sha256`. If any target changed after planning, the operation fails closed before
writing that target.

A successful apply result must report exactly which documents were changed.

The implementation must not stage, commit, push, or otherwise alter Git state beyond the approved
file-content writes.

## 11. Preserve-Originals Policy

AUTO-0002 V1 must preserve unowned content.

Two strategies are permitted during implementation design review:

1. update only explicitly machine-owned marked sections; or
2. deterministically regenerate a document only when that entire document is explicitly defined as
   AUTO-0002-owned.

Implementation must choose one ownership model per writable document before code lands.

Silent heuristic rewriting of arbitrary Markdown paragraphs is forbidden.

If a document does not contain the required ownership markers or does not match the approved format,
AUTO-0002 must report `manual_review_required` rather than normalize it destructively.

## 12. Proposed V1 Ownership Model

The recommended V1 policy is section ownership, not whole-file ownership.

AUTO-0002 should update only machine-owned sections delimited by stable markers, for example:

```text
<!-- ai-engineering:auto0002:project-map:start -->
...
<!-- ai-engineering:auto0002:project-map:end -->
```

Human-authored content outside those markers must remain byte-for-byte unchanged.

Exact marker names and section placement are implementation-time decisions that must be tested.

Existing projects without markers must not be silently rewritten. A separate initialization step may
be proposed later if needed.

## 13. Document-Specific V1 Rules

### PROJECT_MAP.md

AUTO-0002 may synchronize a machine-owned repository-structure section based on relative paths under
the project root.

Rules:

- sort paths deterministically;
- use repository-relative portable paths only;
- exclude `.git`, virtual environments, caches, bytecode, build output, and other configured local
  artifacts;
- do not embed absolute machine paths;
- do not infer architectural purpose from filenames unless purpose comes from an approved mapping.

### MASTER_INDEX.md

AUTO-0002 may synchronize a machine-owned document-index section from an approved document root and
approved filename/status metadata.

V1 must not invent semantic status values from filenames alone. A document without machine-readable
status evidence is listed with a neutral bounded state or flagged for manual review according to the
implementation contract.

### CURRENT_STATUS.md

AUTO-0002 may synchronize only explicitly machine-owned factual fields backed by deterministic local
evidence, such as:

- current Git branch;
- current Git HEAD;
- configured project/package name;
- bounded test-count evidence only when supplied by an approved local evidence source.

V1 must not infer roadmap priority, release readiness, production readiness, client compatibility, or
completion status from code presence alone.

## 14. Dry-Run Default

AUTO-0002 must be read-only by default.

The public API separates detection/planning from apply, and any future CLI must require an explicit
apply flag or apply subcommand for mutation.

A command that merely inspects synchronization state must not write files.

## 15. CLI Direction

A later AUTO-0002 CLI adapter may expose a shape such as:

```text
ai-engineering project docs check --project PATH
ai-engineering project docs plan --project PATH
ai-engineering project docs apply --project PATH
```

This is direction only; exact CLI syntax is not approved by this design task and must be finalized in
a separate bounded implementation task.

The CLI must call the public AUTO-0002 APIs rather than duplicate inspection, drift, planning, or
apply logic.

## 16. Error Model

AUTO-0002 should define a domain error boundary, provisionally `DocumentationSyncError`.

V1 failure classes include:

- invalid project root;
- project root not readable;
- required document missing;
- unsupported document format;
- ownership markers missing or malformed;
- project inspection failure;
- Git inspection failure;
- stale plan / digest mismatch;
- write failure;
- verification failure;
- manual review required;
- unknown internal failure.

Expected domain failures must be controlled and must not be represented as successful synchronization.

## 17. Verification After Apply

After applying a plan, AUTO-0002 must re-read each changed document and verify:

- resulting content equals the planned replacement;
- human-owned content outside machine-owned sections was preserved;
- a fresh drift check clears each item that the plan claimed to resolve;
- no unplanned document was modified.

A write without post-apply verification is not a successful V1 synchronization.

## 18. Portability and Path Rules

All project paths stored in reports or generated documentation must be project-relative unless the
public result explicitly identifies the local `project_root` field.

Generated documentation must never embed machine-specific roots such as:

- `C:\\Users\\...`;
- `D:\\...`;
- OneDrive-specific roots;
- CI runner checkout roots;
- virtual-environment locations.

Path ordering and separators in generated Markdown must be deterministic and platform-independent.

## 19. Security Boundary

AUTO-0002 is not a sandbox.

V1 performs local filesystem inspection, optional bounded Git inspection, and approved Markdown
writes. It does not execute project Python code, run tests, install dependencies, invoke arbitrary
shell commands, contact remote services, or access credentials.

SAFE-0001 remains the MCP Workspace authorization contract and must not be implicitly extended or
weakened by AUTO-0002.

## 20. No-Commit Policy

AUTO-0002 V1 never commits documentation changes automatically.

After apply, changes remain ordinary working-tree modifications for the caller to inspect. Automatic
Git staging, commit creation, branch creation, push, PR creation, or release behavior are explicit
non-goals.

## 21. Automated Verification Matrix

Implementation must provide automated evidence for at least:

| Row | Required evidence |
|---|---|
| Project inspection | deterministic snapshot from isolated fixture repository |
| Relative-path portability | no machine-specific paths in snapshot/generated content |
| PROJECT_MAP drift | missing/stale path detection |
| MASTER_INDEX drift | missing/stale approved document detection |
| CURRENT_STATUS drift | deterministic factual-field drift only |
| Unsupported semantic claim | manual-review classification rather than rewrite |
| Dry-run behavior | detection/planning performs no writes |
| Stable plan | identical input produces identical plan |
| Original digest guard | changed target causes stale-plan failure |
| Marker preservation | human-owned content outside markers is byte-preserved |
| Approved targets only | no file outside the V1 writable set is changed |
| Apply verification | planned updates re-read and verified |
| Re-check after apply | resolved drift disappears |
| Missing/malformed markers | controlled failure/manual-review behavior |
| Git cleanliness semantics | AUTO-0002 creates no commit/stage/push |
| Existing AUTO-0001 behavior | unchanged |
| Existing SDK-0001 behavior | unchanged |

Repository-wide pytest, Ruff, mypy, and `git diff --check` must remain green.

## 22. Implementation Boundaries

The smallest implementation should separate:

- project-state inspection;
- document parsing/ownership handling;
- drift detection;
- deterministic plan generation;
- guarded apply and post-apply verification;
- CLI adaptation, if later approved.

No implementation task should mix all layers in one module solely for convenience.

AUTO-0002 must not refactor unrelated MCP, Runtime, Registry, Workspace, Git, Python, bootstrap,
distribution, CI, or release code merely to introduce synchronization.

## 23. Non-Goals

AUTO-0002 V1 explicitly excludes:

- free-form LLM rewriting;
- rewriting all project documentation;
- project bootstrap or project creation;
- project upgrade/migration;
- source-code generation;
- application/business-logic generation;
- dependency installation;
- executing tests or project code;
- Git staging or commits;
- branch creation;
- GitHub issues, PRs, releases, or repository creation;
- remote Git operations;
- CI workflow generation;
- release/version/tag decisions;
- PyPI publication;
- secrets or credentials;
- arbitrary user-configurable shell hooks;
- network access;
- automatic changes to `README.md`, `AI_CHAT_START.md`, `PROJECT_CONTEXT.md`, `ROADMAP.md`,
  `DECISIONS.md`, or `CODING_STANDARDS.md`.

## 24. Proposed Atomic Implementation Sequence

After design approval:

### AUTO-0002-01 — Project State Inspection API

Implement read-only typed project inspection and deterministic local snapshot tests. No document
writes and no CLI changes.

### AUTO-0002-02 — Drift Detection and Sync Planning

Implement V1 ownership parsing, the three-document drift model, deterministic plan generation, and
stale/manual-review classifications. Still no document writes.

### AUTO-0002-03 — Guarded Apply and Verification

Implement digest-guarded writes to approved machine-owned sections and post-apply verification. No
Git commit/staging behavior.

### AUTO-0002-04 — CLI and Installed-Distribution Verification

Expose the approved check/plan/apply workflow through the installed console script and extend
isolated-wheel verification. Exact CLI contract must be frozen before implementation.

Each task must preserve an atomic review/test boundary and may stop if a real defect or policy gap is
discovered.

## 25. Completion Criteria

AUTO-0002 is complete only when:

- this design is approved;
- project inspection is deterministic and read-only;
- V1 writable scope remains exactly `CURRENT_STATUS.md`, `PROJECT_MAP.md`, and `MASTER_INDEX.md`;
- document ownership is explicit and human content is preserved;
- drift detection is deterministic and bounded to approved evidence;
- synchronization planning precedes mutation;
- stale plans fail closed through digest checks;
- apply writes only approved machine-owned sections;
- post-apply verification proves planned results;
- no Git commit/staging/push is performed;
- installed CLI behavior is verified if included in approved implementation scope;
- repository quality gates remain green;
- documentation records the verified behavior;
- no network, LLM free-form rewriting, publication, or general project-update behavior is implied.
