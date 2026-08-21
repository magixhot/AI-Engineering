# REL-0004-02 — Compatibility Inventory and Version Decision

**Status:** VERSION DECIDED / CANDIDATE NOT PREPARED

## Purpose

Classify the exact post-v0.2.0 compatibility delta and select the next intended
release version without changing package metadata, fixing runtime behavior,
freezing a candidate, or performing publication.

## Exact Baselines

The immutable published baseline remains:

```text
release:  AI-Engineering 0.2.0
tag:      v0.2.0
tag_sha:  1faf14c121b7b5da7c8781e3de4e836f85838a76
PyPI:     NOT APPROVED / NOT PUBLISHED
```

The REL-0004-02 audit starts from exact `master`
`113e848d950629d501b5fef6e0ccdf1279d9e7f8`, after REL-0004-01 merged
through PR #207. Push-triggered Quality #428 (run id `32522858824`) completed
successfully for that exact SHA.

The exact `v0.2.0..master` delta at this decision point is:

```text
commits:           405
files_changed:     174
insertions:        29770
deletions:         462
source_added:      35
source_modified:   2
tests_added:       56
tests_modified:    2
docs_added:        68
docs_modified:     7
```

These counts identify the audited decision baseline. They are not a future
candidate freeze; later approved preparation commits will change them.

## Compatibility Inventory

### Installed CLI

The v0.2.0 commands remain callable:

- `project create`;
- `project bootstrap`;
- `project docs check/plan/apply`.

The installed console-script target changed from `ai_engineering.cli:main` to
`ai_engineering.public_cli:main`. The wrapper delegates all commands outside
its exact added routes to the prior `ai_engineering.cli:main`, which remains
importable. Existing executable spelling and prior command/argument routes are
preserved.

The post-v0.2.0 line adds:

- `project docs ownership check/plan/apply`;
- `project migrate check/plan/apply`;
- `project health`;
- `project reconcile plan/apply/approve/run` with bounded policy, approval,
  orchestration, and optional receipt behavior;
- `workstation doctor`.

One release-readiness gap is explicit: direct invocation of `reconcile
run/approve` and `workstation doctor` works, but the current parent help tree
does not list all three routes. The exact public help hierarchy must be made
coherent before candidate selection.

### Bootstrap and Generated Projects

`project create` and the compatibility-level standalone template API are
byte-unchanged from v0.2.0.

`project bootstrap` intentionally changes its default generated baseline from
python-engineering V1 to V2. V2 adds the explicit identity marker and the V2
`.gitignore` contract. The command does not mutate existing projects; the
registered `python-engineering-v1-to-v2` migration provides explicit,
inspectable check/plan/apply behavior for existing V1 projects.

This deliberate default-output change is not a patch-level change even though
the migration path is bounded and verified.

### Importable Python Surfaces

The established package root and core MCP/discovery/registry/runtime,
Workspace, Git, Python, STDIO, standalone-template, documentation-sync, and
project-inspection source files are unchanged from v0.2.0.

Thirty-five source modules are additive. They introduce typed ownership,
migration, health, reconciliation, control-plane, exact-Quality, workstation,
and canonical-state surfaces. `EngineeringBootstrapVerification` gains a
defaulted `baseline` field, preserving prior positional construction while
adding V2 evidence. The material behavioral change is the bootstrap output
described above.

No promise of a permanently stable Python API is inferred for modules that
were introduced after v0.2.0. Candidate release notes must distinguish public
CLI/contracts from internal operational modules.

### MCP Server and Tool Schemas

The v0.2.0 MCP server, adapter, tool registry, and all 15 built-in
Workspace/Git/Python tool implementations are byte-unchanged. Their existing
names, schemas, and SAFE-0001/SAFE-0002 authority boundaries are preserved.

The post-v0.2.0 GitHub/OpenCode control protocol is a separate additive,
bounded operational surface. Its task classes remain `status`, `inspect`,
`plan`, `diff`, and `quality_verify`; recovery never replays a claimed
request or invokes executor/OpenCode/`quality_verify`.

One version-consistency blocker is explicit. `MCPConfig.server_version`
declares `0.2.0`, while the active SDK `Server` is still constructed with
literal `0.1.0`; an initialize response therefore reports `0.1.0`. Candidate
preparation must establish one authoritative version value and test the exact
installed MCP initialize result for the selected version.

### Reconciliation and Control Envelopes

The plan, apply, policy, approval, orchestration, and receipt formats are new
after v0.2.0 rather than modifications of a published v0.2.0 envelope. Their
deterministic serialization, refusal states, reinspection boundaries, bounded
step limits, and zero-write failure behavior are covered by unit and installed
distribution tests.

The control request/result/recovery formats are likewise additive relative to
v0.2.0. A future release must retain their current versioned envelope and
no-replay boundaries; release preparation must not broaden task classes or
mutation authority.

### Packaging and Runtime Requirements

The following remain unchanged from v0.2.0:

- distribution name `ai-engineering`;
- Python requirement `>=3.11`;
- runtime dependency `mcp>=1.27,<1.28`;
- setuptools build backend and `src` package discovery;
- wheel/sdist content policy.

`pyproject.toml` and `uv.lock` deliberately remain `0.2.0` in this decision
stage. Existing release tests verify wheel/sdist construction, metadata,
source-tree isolation, isolated installation, the current console entry point,
and installed CLI behavior through the reconciliation surface.

Fresh candidate evidence must additionally cover the corrected complete help
tree, exact MCP initialize version, workstation doctor from an installed
wheel, and any operational imports claimed in release notes.

### Prior Compatibility and Safety Claims

The next line preserves the bounded VS Code and Antigravity interoperability
evidence. It does not claim general ChatGPT/OpenAI, Claude Desktop, or other
MCP-client compatibility. SAFE-0001 and SAFE-0002 remain authority and
execution boundaries, not an operating-system sandbox.

GitHub worker/service behavior remains workstation-local and operational; it
does not expand the public MCP tool set or make the release a hosted service.

## Version Decision

The approved intended next package version is **`0.3.0`**, with intended tag
**`v0.3.0`**.

The decision is based on compatibility scope:

- the delta adds multiple public CLI and typed workflow families;
- the default bootstrap output intentionally advances from V1 to V2;
- the installed entry-point implementation changes while preserving prior
  executable routes;
- the release must surface a materially larger operational and safety contract.

`0.2.1` is rejected because a patch line would understate new public
capabilities and the intentional bootstrap contract evolution. `1.0.0` is
rejected because the repository still carries bounded client-compatibility
claims, has not declared its new post-v0.2.0 Python/operational surfaces
permanently stable, and has not completed fresh cross-platform candidate
evidence.

This is a pre-1.0 minor-line decision. It does not assert a formal universal
compatibility guarantee beyond the explicit inventory above.

## Approved Candidate Scope

The intended 0.3.0 candidate scope is the verified v0.2.0 foundation plus the
completed work through AUTO-0022:

1. AUTO-0003 documentation ownership initialization;
2. AUTO-0004/AUTO-0005 migration and python-engineering V2 baseline;
3. AUTO-0006 project health/readiness;
4. AUTO-0007 through AUTO-0012 bounded reconciliation planning, guarded
   execution, policy, approval, orchestration, and receipts;
5. AUTO-0013 through AUTO-0019 bounded read-only control, worker lifecycle,
   exact-Quality verification, workstation readiness, reliability, and
   no-replay recovery;
6. AUTO-0020 through AUTO-0022 canonical repository/control-surface coherence;
7. release-governance documentation required to prepare and verify 0.3.0.

No unverified feature may be added opportunistically during candidate
preparation.

## Required Pre-Candidate Corrections

REL-0004-03 must complete, test, and document exactly these release blockers
before an exact candidate can be selected:

1. align package, lockfile, MCP configuration, active SDK initialize metadata,
   documentation, and expected tag to `0.3.0` from one explicit version
   contract;
2. make the public CLI parent help tree accurately expose `reconcile
   approve/run` and `workstation doctor` while preserving existing command
   behavior and exit codes;
3. draft exact v0.3.0 release notes for the approved scope;
4. keep publication, credentials, workflow permissions, and PyPI unchanged.

REL-0004-04 must then obtain fresh exact Linux/full-suite, distribution,
isolated-wheel, installed MCP/CLI, and Windows-local evidence. Any failure or
unexplained skip blocks publication.

## Authority and State Boundary

This decision does not:

- edit `pyproject.toml`, `uv.lock`, or runtime version metadata;
- freeze a candidate SHA;
- create or move `v0.3.0`;
- create a GitHub Release or upload assets;
- publish to TestPyPI or PyPI;
- change secrets, credentials, workflows, task classes, or runtime authority;
- change the canonical AUTO state.

The published and canonical release line remains `v0.2.0` until a separately
approved and successfully completed publication stage. The AUTO manifest
remains `AUTO-0022` / `QUIESCENT`.

## Result

**REL-0004-02 result: `0.3.0` SELECTED / CANDIDATE NOT PREPARED / NOT
PUBLISHED.**

REL-0004-03 requires separate approval for the bounded corrections, version
metadata, lockfile, release notes, and candidate-preparation work listed above.
