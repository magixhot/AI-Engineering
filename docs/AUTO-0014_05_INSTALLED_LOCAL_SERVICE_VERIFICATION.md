# AUTO-0014-05 — Installed Local-Service Verification

**Status:** COMPLETE / VERIFIED

This document records the installed local-service verification evidence for AUTO-0014-05. It does not add service authority, repository mutation authority, remote service-control authority, request replay, or any new AUTO-0013 task class.

## Verified lifecycle behavior

The user-scoped service was installed explicitly on a WSL/Linux verification host and observed running under the per-user service manager.

The installed service uses the AUTO-0014 lifecycle entrypoint and preserves the existing AUTO-0013 read-only control path:

```text
External AI operator
  -> GitHub control issue
  -> installed user-scoped worker service
  -> localhost OpenCode server
  -> dedicated read-only AUTO-0013 agent
  -> AI-Engineering workspace
  -> typed GitHub result
```

Local lifecycle checks recorded:

```text
restart=PASS
single-instance=PASS
repository-invariants=PASS
```

These checks established that a service restart produces a fresh worker process, a second lifecycle instance for the same repository/control issue fails closed rather than racing the installed worker, and the repository remains unchanged by lifecycle verification.

## Runtime-directory correction

Initial installed-service verification exposed a fail-closed interaction between `ProtectSystem=strict` and creation of the worker runtime directory under the per-user runtime root.

PR #141 corrected the user-service integration by validating the runtime directory as a direct child of the current user runtime root and rendering `RuntimeDirectory=` plus `RuntimeDirectoryMode=0700`, while preserving `ProtectSystem=strict` and `ProtectHome=read-only`.

The corrective pre-merge Quality gate succeeded. The correction merged before the final installed-service E2E verification.

## Safe execution-stage diagnostics

A subsequent installed E2E request proved GitHub request discovery, autonomous claim publication, terminal result publication, exact repository binding, and before/after cleanliness, but the localhost OpenCode message call returned HTTP 500.

PR #142 added bounded public stage qualification so a safe failure can distinguish session creation from message execution without publishing response bodies, credentials, paths, environment values, provider configuration, or other machine-private data.

The corrected PR #142 head `6ada946ae28c40b15c0848911c5ba60b6e07a5e9` passed pre-merge Quality. PR #142 merged as exact master:

```text
5b5b3b0ec1922685a594679ddebc199f28b6b8d5
```

The exact post-merge Quality gate for that master commit was confirmed SUCCESS before final AUTO-0014-05 verification continued.

## Final installed-service end-to-end evidence

The final verification request used issue #130 and the exact expected repository head:

```text
request_id=sha256:593eff3b7e76a65ec2399ea3988ae0895ea01c2bc608bb690bc62be46fe9baf7
expected_head=5b5b3b0ec1922685a594679ddebc199f28b6b8d5
task_class=status
```

The already-running installed worker discovered and claimed the request autonomously. No manual worker process was started for the request.

The terminal typed result recorded:

```text
state=SUCCEEDED
task_class=status
repository=magixhot/AI-Engineering
branch=master
head=5b5b3b0ec1922685a594679ddebc199f28b6b8d5
pre_clean=true
post_clean=true
```

The successful result therefore proves the complete installed path from GitHub through the user-scoped worker service and localhost OpenCode to the read-only agent and back to typed GitHub evidence, while preserving the repository state.

## Authority and privacy boundary

AUTO-0014-05 does not authorize:

- write/apply execution;
- Git mutation;
- arbitrary shell execution;
- public OpenCode ingress;
- inbound workstation webhooks;
- remote service start/stop commands;
- claimed-request replay/resume;
- publication of credentials, environment values, local usernames, home directories, or machine-specific absolute paths.

The worker remains restricted to the existing AUTO-0013 task classes `status`, `inspect`, `plan`, and `diff`.

## Stage completion evidence

The evidence-only PR #143 passed pre-merge Quality #302, merged as exact master:

```text
58e0b3c6cd5393386ad97871aa34f6fd9e4fef47
```

The exact post-merge Quality gate for that master commit was confirmed SUCCESS. AUTO-0014-05 is therefore COMPLETE / VERIFIED for its approved installed read-only service scope.
