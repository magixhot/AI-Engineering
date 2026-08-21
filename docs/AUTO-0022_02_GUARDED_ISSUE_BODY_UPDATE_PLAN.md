# AUTO-0022-02 — Guarded Issue Body Update Plan

## Scope

This stage freezes the exact future body of public GitHub issue #130 and the
fail-closed procedure for a later body-only update. It does not mutate GitHub
issue state. The external write remains separately authorized stage
`AUTO-0022-03`.

Exact target:

```text
repository: magixhot/AI-Engineering
issue:      130
field:      body
```

No title, state, label, milestone, assignee, comment, reaction, or other issue
is in scope.

## Verified Repository Baseline

AUTO-0022-01 merged through PR #203 as exact `master`
`3efd7714b1302f13c371f81e6b8894f08b517c6f`. Pre-merge Quality #419 and
push-triggered Quality #420 (run id `32513910434`) completed successfully.

## Fresh External Pre-State

The fresh AUTO-0022-02 read-only inspection observed:

```text
state:      open
title:      AUTO-0013 OpenCode control channel
updated_at: 2026-08-21T12:31:00Z
body_sha256: ee0db3171f5d0c39976102c14b4780ca0ea3677fe3ec82f7df9becdc66edf4ff
```

The hash is over the exact UTF-8 body bytes returned by GitHub, with no byte
added or removed by the verifier.

## Approved Desired Body

`docs/AUTO-0022_ISSUE_130_DESIRED_BODY.md` is the complete future issue body,
not a template or prose description. Its exact tracked UTF-8 bytes, including
the final LF, are the only approved mutation payload. The desired-body SHA-256
is recorded below after repository generation and must match before any write:

```text
c99ffa0b885926a64db30c451eeb910ad5dc9b6449f1c4833908d94c43dc859e
```

Stage -03 must read the file as bytes and derive the API body string without
normalizing whitespace, wrapping lines, or adding/removing a trailing LF.

## Fail-Closed Preconditions

Immediately before any update, stage -03 must perform a fresh read and require
all of the following:

1. repository is exactly `magixhot/AI-Engineering`;
2. issue number is exactly `130`;
3. issue state is exactly `open`;
4. title is exactly `AUTO-0013 OpenCode control channel`;
5. current body SHA-256 is exactly
   `ee0db3171f5d0c39976102c14b4780ca0ea3677fe3ec82f7df9becdc66edf4ff`;
6. desired artifact SHA-256 equals the recorded approved desired hash;
7. the repository stage -02 commit and its exact gates are verified.

Any mismatch or unavailable evidence stops without a write. The operator must
not silently rebase the precondition to newly observed issue content.

## Single Update Attempt

After all preconditions match, stage -03 may make exactly one API update whose
only supplied mutable field is `body`, populated from the exact approved
artifact. It must not supply title, state, labels, milestone, assignees, or
other mutable fields.

There is no automatic write retry. A timeout, disconnect, malformed response,
or other ambiguous result triggers read-only reinspection, not another update.

## Ambiguous-Response Resolution

After an ambiguous response, re-fetch issue #130 once and compare its exact
body hash:

- desired hash observed: classify the write as applied and continue with
  post-write verification;
- original expected hash observed: classify the attempt as not observed and
  stop for controlled review;
- any other hash or unavailable read: fail closed and stop for manual audit.

No branch may issue a second automatic write.

## Post-Write Verification

Stage -03 must re-read the issue and record public-safe evidence that:

- repository and issue identity are exact;
- state remains `open` and title remains unchanged;
- returned body bytes equal the approved artifact exactly;
- post-write body SHA-256 equals the approved desired hash;
- the mutation request supplied only `body`;
- no retry occurred;
- task-class, authority, privacy, and no-replay statements match the approved
  contract.

`updated_at` may change as the expected consequence of the body update. The
plan does not claim that GitHub-internal metadata is otherwise byte-stable.

## Preserved Boundaries

This plan adds no task class, protocol/runtime behavior, worker/OpenCode
authority, request replay, generic GitHub synchronizer, automatic repair,
workflow control, service or credential mutation, deployment, release,
publication, or PyPI authority. Evidence must omit tokens, credentials,
environment values, local paths, hostnames, usernames, and unrelated issue or
comment content.
