# AI-Engineering Roadmap

## Completed / Verified

The documentation foundation, MCP foundation, SDK-0001, TOOL-0001, REL-0001/REL-0002/REL-0003, CI-0001, SAFE-0001/SAFE-0002, and AUTO-0001 through AUTO-0013 are COMPLETE / VERIFIED for their approved scopes.

AUTO-0007 remains the permanent read-only reconciliation planner. AUTO-0008 remains the guarded one-step apply boundary. AUTO-0009 is bounded multi-step orchestration. AUTO-0010 adds only a restrictive policy gate. AUTO-0011 adds only an optional explicit single-candidate approval gate. AUTO-0012 adds deterministic execution receipts/evidence only. AUTO-0013 adds bounded read-only remote inspection/control transport and evidence only.

## AUTO-0014 — Local Control Worker Service / Lifecycle

**Status:** AUTO-0014-06 FINAL RECONCILIATION ACTIVE

AUTO-0014 adds only local lifecycle supervision around the existing AUTO-0013 read-only worker. It removes manual worker startup without expanding remote task classes or repository mutation authority.

Verified installed path:

```text
External AI operator
  -> GitHub control issue
  -> installed user-scoped worker service
  -> localhost OpenCode server
  -> dedicated read-only AUTO-0013 agent
  -> AI-Engineering workspace
  -> typed GitHub result
```

### Delivery Evidence

- AUTO-0014-01 — PR #137; pre-merge and exact post-merge Quality SUCCESS.
- AUTO-0014-02 — PR #138; pre-merge and exact post-merge Quality SUCCESS.
- AUTO-0014-03 — PR #139; pre-merge and exact post-merge Quality SUCCESS.
- AUTO-0014-04 — PR #140; pre-merge and exact post-merge Quality SUCCESS.
- AUTO-0014-05 runtime-directory correction — PR #141; hardened user runtime integration.
- AUTO-0014-05 safe stage diagnostics — PR #142; merged exact master `5b5b3b0ec1922685a594679ddebc199f28b6b8d5`; exact post-merge Quality SUCCESS.
- AUTO-0014-05 installed-service evidence — PR #143; Quality #302 SUCCESS; merged exact master `58e0b3c6cd5393386ad97871aa34f6fd9e4fef47`; exact post-merge Quality SUCCESS.
- AUTO-0014-06 final evidence/documentation reconciliation — active; must pass pre-merge and exact post-merge Quality before AUTO-0014 closes.

Installed lifecycle checks recorded `restart=PASS`, `single-instance=PASS`, and `repository-invariants=PASS`.

Verified successful installed-service request:

```text
sha256:593eff3b7e76a65ec2399ea3988ae0895ea01c2bc608bb690bc62be46fe9baf7
```

Its terminal result recorded `SUCCEEDED`, `master`, exact HEAD `5b5b3b0ec1922685a594679ddebc199f28b6b8d5`, `pre_clean=true`, and `post_clean=true`.

## Next Approved Milestone

After AUTO-0014 closes, begin a design-first read-only exact post-merge Quality verifier. It will deterministically verify the `Quality` workflow for the exact merged `master` SHA, including push event, completed status, and successful conclusion, and fail closed otherwise.

This verifier is intended to remove the remaining manual GitHub Actions confirmation step. It must not gain workflow rerun/cancel authority, merge authority, repository mutation authority, or any new AUTO task class.

## Current Priority

Complete AUTO-0014-06 without weakening AUTO-0007 through AUTO-0014 authority boundaries. No implementation of the exact post-merge verifier begins until AUTO-0014-06 itself passes its full gate.
