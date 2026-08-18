# AUTO-0013-05 — End-to-End Verification Evidence

**Status:** VERIFICATION EVIDENCE

## Purpose

This document records the installed/local-worker verification required by AUTO-0013-05.

The verified control path is:

```text
GitHub control issue
        |
        v
local WSL control worker
        |
        v
localhost OpenCode server
        |
        v
read-only AUTO-0013 agent
        |
        v
AI-Engineering workspace
        |
        v
bounded typed result back to GitHub
```

## Verification target

The final successful verification request used:

- repository: `magixhot/AI-Engineering`
- task class: `status`
- expected HEAD: `2d03f9e37e373def6b0f705b6f2b5da751279427`
- request id: `sha256:dcdfcd976fff8c7afd16352fdc63e2781c7067c6492c4e43733abd4bd6efeb2c`
- control issue: `#130`

The request objective required a read-only inspection of branch, HEAD, cleanliness, and unchanged-workspace state.

## Successful live evidence

The local worker claimed the exact request and published a terminal typed result with:

- state: `SUCCEEDED`
- branch: `master`
- observed HEAD: `2d03f9e37e373def6b0f705b6f2b5da751279427`
- pre-execution cleanliness: `true`
- post-execution cleanliness: `true`
- repository identity: `magixhot/AI-Engineering`
- exact request identity preserved end to end

The textual result also reported that the expected HEAD matched exactly, the working tree was clean, the branch was up to date with `origin/master`, and the workspace remained unchanged.

## Failure-path evidence discovered during E2E

The live verification process also exposed two integration defects that were corrected before the final successful run:

1. A post-claim OpenCode execution failure could strand a request without a terminal typed result. The worker was hardened so execution exceptions produce bounded `FAILED` evidence while preserving observed branch/HEAD/cleanliness state and keeping detailed local diagnostics out of the public control plane.
2. Raw OpenCode HTTP sessions were initially created in the server process working directory instead of the repository workspace. The adapter was corrected to route session and message requests with the repository workspace directory, after which the final live request completed successfully.

These corrections did not add new task classes, write/apply authority, Git mutation authority, filesystem mutation authority, retry semantics, or public OpenCode ingress.

## Read-only authority evidence

Independent direct OpenCode execution with the dedicated AUTO-0013 agent confirmed that the deny-by-default shell policy is active:

- an unapproved plain `git status` tool call was denied;
- approved read-only Git commands such as `git --no-optional-locks status`, `git log`, and `git branch` were allowed;
- the repository remained clean at the expected HEAD.

## Privacy and publication boundary

The public verification evidence records only repository-safe information. It does not record credentials, tokens, environment values, local user names, home-directory paths, or unrelated workstation details.

## Acceptance conclusion

AUTO-0013-05 has demonstrated the required real control path:

`remote GitHub request -> local worker -> localhost OpenCode inspection -> typed GitHub result`

with exact repository identity, exact expected HEAD, pre/post clean state, and unchanged repository evidence.

This document itself does not mark AUTO-0013-05 COMPLETE / VERIFIED until its own pre-merge Quality gate succeeds, it is merged, and the exact resulting `master` commit passes post-merge Quality as required by the AUTO-0013 staged delivery contract.

AUTO-0013-06 remains the separate final evidence/documentation reconciliation stage and is not authorized to begin before that gate is complete.
