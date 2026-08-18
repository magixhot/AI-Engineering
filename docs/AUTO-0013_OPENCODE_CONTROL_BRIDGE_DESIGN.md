# AUTO-0013 — OpenCode Control Bridge Design

**Status:** DESIGN / CONTRACT ONLY

## Purpose

AUTO-0013 defines a bounded control bridge that allows an external AI operator to submit engineering inspection tasks through GitHub and have a local WSL worker execute those tasks through an already-running OpenCode server for the `AI-Engineering` workspace.

The goal is to remove manual prompt/result copying while preserving the repository's existing safety and authority boundaries.

AUTO-0013 does **not** authorize autonomous repository mutation.

## Architectural position

The control path is:

```text
External AI operator
        |
        v
GitHub control plane
        |
        v
Local WSL control worker
        |
        v
OpenCode server (localhost)
        |
        v
AI-Engineering workspace
```

GitHub is the shared transport/control plane because it is reachable by both the external operator and the local workstation. OpenCode remains bound to localhost and is not exposed directly to the public network.

## Existing authority boundaries

AUTO-0013 MUST preserve all existing AUTO-0007 through AUTO-0012 boundaries.

In particular:

- AUTO-0007 remains permanently read-only.
- AUTO-0008 remains the sole guarded one-step reconciliation mutation authority.
- AUTO-0009 remains bounded multi-step orchestration with fresh planning between writes.
- AUTO-0010 remains restriction-only policy.
- AUTO-0011 remains an optional explicit approval gate.
- AUTO-0012 remains deterministic execution evidence only.
- AUTO-0013 MUST NOT create a second project mutation path, bypass existing reconciliation authority, or treat an AI request as write authorization.

## Stage-01 scope

The first implementation stage is read-only.

Allowed task classes are limited to:

- `status` — inspect Git branch, HEAD, remote alignment, and working-tree state;
- `inspect` — read and summarize repository files and documentation;
- `plan` — produce a proposed engineering plan without modifying project state;
- `diff` — inspect existing Git differences without staging or changing them.

A future `test` task class may be designed separately after its side-effect and workspace guarantees are specified. It is intentionally excluded from the initial read-only worker contract because arbitrary test commands can have project-specific side effects.

## Explicitly forbidden operations

The Stage-01 worker MUST reject tasks that request or imply any of the following:

- file edit, write, patch, create, rename, move, or delete;
- Git add, commit, amend, merge, rebase, cherry-pick, tag, push, fetch-with-update-side-effects, reset, restore, checkout, clean, stash mutation, or remote/config mutation;
- package publication or release;
- network deployment;
- secret, credential, token, key, or `.env` disclosure;
- access outside the configured project workspace;
- arbitrary shell execution supplied by the remote requester;
- changing OpenCode configuration or permission policy;
- disabling safety checks;
- invoking existing reconciliation mutation authority indirectly.

The worker must fail closed when a request cannot be classified as one of the explicitly allowed read-only task classes.

## OpenCode permission boundary

The worker must invoke a dedicated OpenCode agent/configuration whose effective permissions deny project edits and deny shell commands by default.

The implementation may allow a minimal explicit read-only shell allowlist such as:

```text
git status
git status --short
git branch
git rev-parse HEAD
git log --oneline ...
git diff
git diff --stat
git diff --cached
git diff --cached --stat
git grep ...
```

Any shell command not matched by the approved allowlist must be denied rather than converted into an interactive approval prompt, because the local worker is intended to run unattended.

OpenCode file-edit permissions must be `deny` for the Stage-01 worker.

External-directory access must be denied.

## GitHub control-plane contract

The transport must use a narrowly-scoped GitHub conversation surface belonging to `magixhot/AI-Engineering`.

The initial design uses a dedicated control issue as an append-only request/result mailbox.

Each request must have:

- a deterministic request identifier;
- one allowed task class;
- a natural-language objective;
- the expected repository identity;
- an optional expected HEAD SHA;
- a bounded maximum result size;
- no embedded credentials or secrets.

The worker must ignore ordinary repository issues/comments that do not match the control protocol.

The worker must never execute Markdown, shell fragments, code blocks, or issue text directly as shell commands.

## Request state model

A request has one of these states:

```text
PENDING
RUNNING
SUCCEEDED
REFUSED
FAILED
```

The worker claims at most one request at a time for a configured workspace.

A result must record at minimum:

- request identifier;
- task class;
- observed repository path identity in portable form;
- observed branch;
- observed HEAD SHA;
- pre-execution Git cleanliness evidence;
- terminal state;
- bounded textual result or refusal/error summary;
- post-execution Git cleanliness evidence.

The result is evidence only. It is not authority for a later write.

## Workspace and Git invariants

For every Stage-01 request, the worker must verify before and after OpenCode execution that:

- branch/HEAD did not change;
- index did not change;
- tracked working-tree content did not change;
- no new untracked project files were created by the worker or OpenCode;
- repository configuration and remotes were not changed.

If any invariant changes unexpectedly, the worker must mark the request `FAILED`, stop processing further tasks, and require operator inspection. AUTO-0013 Stage-01 does not authorize automatic rollback.

## Authentication and secrets

GitHub authentication is local runtime configuration, not repository content.

The worker must not store GitHub tokens, OpenCode provider credentials, API keys, or other secrets in tracked files, task payloads, issue comments, logs committed to Git, or result bodies.

The implementation should support credentials from the local environment or an already-authenticated GitHub CLI/session.

## Public-repository disclosure boundary

`AI-Engineering` is a public repository. Therefore the control plane must assume that request and result text posted to the repository can be public.

Stage-01 results must be limited to information that is already safe to expose for this public repository. The worker must redact local user names, home-directory paths, environment values, credentials, tokens, and unrelated workstation information.

A later private control-plane design may be introduced if richer private workstation evidence is required.

## OpenCode server boundary

OpenCode should remain bound to localhost, for example:

```text
127.0.0.1:4096
```

AUTO-0013 does not require public exposure, port forwarding, reverse proxies, tunnels, or firewall openings for the OpenCode HTTP server.

The local worker communicates with OpenCode over localhost only.

## Failure model

The implementation must fail closed for at least:

- malformed control request;
- unknown task class;
- repository identity mismatch;
- expected HEAD mismatch;
- dirty workspace when the request requires a clean baseline;
- OpenCode server unavailable;
- OpenCode permission refusal;
- OpenCode execution failure;
- Git invariant change;
- result publication failure;
- duplicate/replayed request identifier;
- control-plane authentication failure.

A failed or refused request must not be retried automatically unless a later contract explicitly defines safe retry semantics.

## Non-goals

AUTO-0013 Stage-01 does not introduce:

- autonomous code editing;
- AI-authorized commits or pushes;
- pull-request creation by the local worker;
- reconciliation apply/run authority;
- arbitrary command execution;
- public exposure of the OpenCode server;
- webhook listeners on the workstation;
- background deployment control;
- cross-repository execution;
- secret retrieval;
- automatic rollback;
- unattended production mutation.

## Staged delivery contract

AUTO-0013 is delivered strictly in order:

1. **AUTO-0013-01 — Control Bridge Design / Contract**: this document only; no production implementation.
2. **AUTO-0013-02 — Typed Request / Result Protocol**: typed parser/serializer, strict validation, deterministic request identity, and fail-closed task classification.
3. **AUTO-0013-03 — Read-Only OpenCode Adapter**: localhost OpenCode integration with dedicated deny-by-default permissions and invariant checks.
4. **AUTO-0013-04 — GitHub Control Worker**: bounded polling/claim/result transport for the dedicated control issue.
5. **AUTO-0013-05 — End-to-End Verification**: installed/local-worker verification proving remote request → local OpenCode inspection → GitHub result with unchanged repository state.
6. **AUTO-0013-06 — Final Evidence / Documentation Reconciliation**: authoritative closure evidence and documentation updates.

Each stage requires its own pre-merge Quality success and exact post-merge Quality success before the next stage begins.

## Acceptance invariants

AUTO-0013 Stage-01 is acceptable only if later implementation tests prove that:

- only explicitly allowed read-only task classes are executable;
- arbitrary request text cannot become a shell command;
- OpenCode edit/write tools are denied;
- shell access is deny-by-default and restricted to the approved read-only allowlist;
- external-directory access is denied;
- a request cannot change HEAD, branch, index, tracked files, untracked project state, remotes, or repository configuration;
- malformed, duplicate, unknown, dirty-baseline, or identity-mismatched requests fail closed;
- credentials and local private environment details are not emitted into the public control plane;
- OpenCode remains localhost-only;
- result publication is evidence only and cannot grant later write authority;
- existing AUTO-0007 through AUTO-0012 tests remain green.

## Stage-01 completion rule

AUTO-0013-01 may be marked COMPLETE / VERIFIED only after this design-only change passes pre-merge Quality, is merged, and the exact resulting `master` commit passes post-merge Quality.

Production implementation must not begin before that gate is complete.
