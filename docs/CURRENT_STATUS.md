# AI-Engineering — Current Status

<!-- canonical-project-state
{"schema_version":1,"completed_through":"AUTO-0019","active_milestone":"AUTO-0020","active_stage":"AUTO-0020-04","active_state":"IMPLEMENTATION_ACTIVE","release_line":"v0.2.0"}
-->

**Snapshot date:** 2026-08-19  
**Status:** ACTIVE  
**Release line:** 0.2.0  
**Current milestone:** AUTO-0014 — Local Control Worker Service / Lifecycle  
**Active stage:** AUTO-0014-06 — Final Evidence / Documentation Reconciliation

## Authoritative State

AUTO-0001 through AUTO-0013 are COMPLETE / VERIFIED for their approved scopes. AUTO-0014 stages 01 through 05 are COMPLETE / VERIFIED; AUTO-0014-06 is the only active stage.

| Stage | State | Evidence |
|---|---|---|
| AUTO-0014-01 Local Worker Service Design / Contract | COMPLETE / VERIFIED | PR #137; pre-merge and exact post-merge Quality SUCCESS. |
| AUTO-0014-02 Typed Runtime / Service Configuration | COMPLETE / VERIFIED | PR #138; pre-merge and exact post-merge Quality SUCCESS. |
| AUTO-0014-03 Single-Instance Worker Lifecycle | COMPLETE / VERIFIED | PR #139; pre-merge and exact post-merge Quality SUCCESS. |
| AUTO-0014-04 User Service Integration | COMPLETE / VERIFIED | PR #140; pre-merge and exact post-merge Quality SUCCESS. |
| AUTO-0014-05 Installed Local-Service Verification | COMPLETE / VERIFIED | PR #143; Quality #302 SUCCESS; merged master `58e0b3c6cd5393386ad97871aa34f6fd9e4fef47`; exact post-merge Quality SUCCESS. |
| AUTO-0014-06 Final Evidence / Documentation Reconciliation | ACTIVE | Final documentation gate in progress. |

Corrective prerequisites within AUTO-0014-05 included PR #141 for hardened per-user runtime-directory integration and PR #142 for safe OpenCode execution-stage diagnostics. PR #142 merged as exact master `5b5b3b0ec1922685a594679ddebc199f28b6b8d5` and passed exact post-merge Quality before final installed-service verification continued.

## Verified AUTO-0014 Installed-Service Evidence

The installed user-scoped worker service was verified for restart, single-instance behavior, and repository invariants:

```text
restart=PASS
single-instance=PASS
repository-invariants=PASS
```

Successful live request:

```text
sha256:593eff3b7e76a65ec2399ea3988ae0895ea01c2bc608bb690bc62be46fe9baf7
```

Verified path:

```text
GitHub control issue
  -> installed user-scoped worker service
  -> localhost OpenCode server
  -> dedicated read-only AUTO-0013 agent
  -> AI-Engineering workspace
  -> typed GitHub result
```

The terminal result recorded `state=SUCCEEDED`, `branch=master`, exact HEAD `5b5b3b0ec1922685a594679ddebc199f28b6b8d5`, `pre_clean=true`, and `post_clean=true`.

## Authority Boundaries

AUTO-0007 remains permanently read-only. AUTO-0008 remains the sole guarded one-step apply authority. AUTO-0009 remains bounded replan-between-writes orchestration. AUTO-0010 remains restriction-only policy. AUTO-0011 approval cannot grant mutation authority. AUTO-0012 remains deterministic execution evidence only. AUTO-0013 remains bounded read-only remote inspection/control transport and evidence. AUTO-0014 adds only local service lifecycle supervision for that existing worker.

AUTO-0014 does not authorize file mutation, Git mutation, reconciliation apply/run mutation, arbitrary remote shell execution, publication, deployment, public OpenCode ingress, remote service control, request replay, or a second write path.

## Current Priority

Finish the AUTO-0014-06 pre-merge/merge/exact-post-merge Quality gate. After AUTO-0014 closure, begin the already-approved design-first milestone for a read-only exact post-merge Quality verifier so future merge gates no longer require manual GitHub Actions confirmation. The verifier must fail closed and must not gain workflow mutation or repository mutation authority.
