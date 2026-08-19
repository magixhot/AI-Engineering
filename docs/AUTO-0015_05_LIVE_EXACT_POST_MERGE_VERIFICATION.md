# AUTO-0015-05 — Live Exact Post-Merge Verification

Status: IN PROGRESS / PENDING LIVE GATE

## Purpose

Prove that the AUTO-0015 verifier can read authoritative GitHub Actions metadata and classify the exact push-triggered `Quality` run for the current `master` base SHA without manual inspection of the Actions UI.

## Live verification path

For pull-request-triggered `Quality` runs, the workflow now grants only read-only `actions: read` in addition to the existing `contents: read` permission. After lint, type-check, and test gates pass, a PR-only step invokes:

`python -m ai_engineering.quality_verifier <repository> <pull-request-base-sha>`

The target SHA is `github.event.pull_request.base.sha`, so each PR verifies the exact post-merge Quality evidence for the `master` commit it is based on.

For this stage, the first live target is:

`6413a7e596fe901dce34d72814b94cf1b63e25cd`

That commit is the merge commit for AUTO-0015-04 / PR #148.

## Authority boundary

This stage adds no workflow rerun, cancel, dispatch, merge, ref write, repository write, service control, deployment, publication, or reconciliation mutation authority.

The added GitHub Actions permission is read-only. The verifier continues to fail closed unless it observes exactly one authoritative exact tuple with workflow `Quality`, branch `master`, event `push`, exact SHA, status `completed`, and conclusion `success`.

## Completion rule

AUTO-0015-05 may be marked COMPLETE / VERIFIED only after:

1. the stage PR's pre-merge `Quality` run completes successfully with the live verifier step enabled;
2. that live step verifies the exact base `master` SHA rather than the PR merge SHA;
3. the stage PR merges through the normal expected-head gate;
4. the exact resulting `master` SHA passes post-merge `Quality`.

The final reconciliation stage must record the concrete run and commit evidence.
