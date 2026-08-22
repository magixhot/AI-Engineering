# AI-Engineering Local Agent Contract

This repository supports bounded local coding-agent execution through OpenCode.
OpenCode is an execution backend, not an authority source.

## Authority

Human approval and repository milestone contracts remain authoritative.
Agents may perform only the role capabilities explicitly granted here and in
`.opencode/agents/`.

No local agent may:

- merge a pull request;
- push `master` or another protected branch;
- force-push;
- change branch protection, required checks, Quality, secrets, credentials,
  releases, tags, or publication state;
- reinterpret a failing deterministic check as success;
- broaden its own permissions;
- bypass repository governance because a model is confident.

## Execution model

The primary local execution shape is CLI-first:

```text
supervisor / human
  -> precondition check
  -> opencode run --agent <role> --model <provider/model> "..."
  -> evidence / deterministic checks
  -> PASS | FAIL | BLOCKED | ESCALATE
```

A permanent `opencode serve` process is not required for this local-agent layer.
The existing AUTO-0013..AUTO-0019 localhost HTTP control plane remains a
separate, narrower contract and must not be weakened or repurposed by INFRA.

## Workspace concurrency

One physical Git worktree may have at most one write-capable agent at a time.

Read-only agents may run concurrently. A verifier must not evaluate a worktree
while an implementer still owns the writer lock.

Parallel write-capable work requires separate `git worktree` directories and
separate branches.

## Precondition boundary

Before any write-capable run, the caller must establish:

```text
repository root is the intended AI-Engineering checkout
current branch is not master/protected
exact HEAD is recorded
worktree and index are clean
single-writer lock is acquired
approved task scope is explicit
```

A failed precondition is `BLOCKED`; the agent must not repair or relax the
precondition automatically.

## Model routing

Preferred execution order:

```text
local Ollama model
  -> external OpenCode free model when explicitly allowed
  -> Codex only for escalation
```

The approved local-provider baseline is Ollama on loopback. The first verified
local tool-capable profile is `ollama/qwen3:4b` through OpenCode. Model identity
must be explicit; floating `latest` identities are not accepted as reproducible
evidence.

Automatic fallback from a local model to an external/cloud model is forbidden.
Fallback or escalation must be explicit in the higher-level workflow.

## Roles

### repo-reader

Read-only repository inspection. It may read non-sensitive repository files and
run only narrow read-only Git inspection commands. It must never edit files or
Git state.

### implementer

May edit files only within one explicitly approved task scope and only after the
caller has acquired the single-writer lock and established the preconditions
above. It may not push, merge, alter protected branches, change authority rules,
or expand its own scope.

### verifier

Read-only verification and evidence collection. It may run approved
deterministic checks but may not repair failures or edit the repository.

## Terminal outcomes

Every governed local-agent invocation must terminate as one of:

- `PASS` — bounded task completed and required evidence passed;
- `FAIL` — task or required check failed;
- `BLOCKED` — environment, lock, branch, cleanliness, permission, or evidence
  precondition prevented execution;
- `ESCALATE` — task requires stronger reasoning or authority interpretation than
  the local role/model may provide.

No hidden replay, permission expansion, cloud fallback, or automatic repair is
allowed after a terminal failure.
