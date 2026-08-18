# AUTO-0014 — Local Control Worker Service / Lifecycle Design

**Status:** DESIGN / CONTRACT ONLY

## Purpose

AUTO-0014 defines a safe local service lifecycle for the already-verified AUTO-0013 read-only GitHub → local worker → localhost OpenCode control path.

The immediate operational gap after AUTO-0013 is that the local control worker still has to be started manually. AUTO-0014 removes that manual startup burden without expanding the worker's authority.

AUTO-0014 does **not** authorize repository mutation, reconciliation apply/run mutation, arbitrary shell execution, public OpenCode ingress, or remote service-management authority.

## Architectural position

The verified AUTO-0013 path remains unchanged:

```text
External AI operator
  -> GitHub control issue
  -> local control worker
  -> localhost OpenCode server
  -> dedicated read-only AUTO-0013 agent
  -> AI-Engineering workspace
  -> typed GitHub result
```

AUTO-0014 adds only a local lifecycle wrapper around the existing control worker:

```text
local user service manager
  -> starts one bounded AUTO-0013 worker instance
  -> restarts only under defined failure policy
  -> records local redacted operational logs
  -> stops cleanly on shutdown/logout/service stop
```

## Authority boundary

AUTO-0014 MUST preserve every AUTO-0013 authority boundary.

The service layer may start, stop, supervise, and observe the existing read-only worker process. It may not:

- add new remote task classes;
- add file edit/write authority;
- add Git mutation authority;
- call reconciliation apply/run mutation paths;
- expose OpenCode beyond localhost;
- expose a new inbound listener on the workstation;
- create remote service-control commands;
- publish secrets, credentials, local usernames, home paths, environment values, or unrelated workstation data;
- weaken the dedicated OpenCode agent permission policy;
- convert failed requests into retries unless a later contract explicitly permits request retry semantics.

## Platform contract

The initial supported lifecycle target is a per-user service manager in WSL/Linux. The implementation should prefer a user-scoped service rather than a privileged system service.

The design must not require root privileges for normal worker execution. Installation/enabling of the service is a local operator action and must be explicit.

Machine-specific absolute paths are runtime configuration, not portable repository identity. Tracked service templates must use portable placeholders or runtime discovery rather than embedding a user's home directory or workstation-specific project path.

## Process model

Exactly one worker instance may actively service the configured repository/control issue at a time.

The lifecycle implementation must define:

- single-instance protection;
- bounded poll interval with the AUTO-0013 default remaining approximately 10 seconds unless explicitly configured;
- clean process startup and shutdown;
- deterministic repository identity binding;
- expected working-directory/project binding;
- localhost OpenCode endpoint binding;
- fail-closed behavior when repository identity, configuration, or service prerequisites are invalid;
- no shell interpretation of remote request content.

A second concurrent worker for the same repository/control issue must fail closed or remain inactive rather than race claims/results.

## OpenCode dependency model

AUTO-0014 must distinguish worker lifecycle from OpenCode server lifecycle.

The initial implementation may either:

1. require the localhost OpenCode server to already be running and surface a bounded local failure when unavailable; or
2. define a separately supervised localhost-only OpenCode dependency if and only if that behavior is explicitly covered by a later implementation stage and tests.

AUTO-0014 design does not authorize public bind addresses, tunnels, reverse proxies, firewall openings, or remote ingress.

## Restart and failure semantics

Service-manager restart policy must be process-level only.

A worker process crash may be restarted after a bounded delay. This must **not** mean that a claimed GitHub control request is automatically replayed. Existing AUTO-0013 duplicate/claim/result semantics remain authoritative.

The service must avoid tight crash loops. Repeated startup failures must remain visible in local service state/logs and must not flood the public GitHub control issue.

Known request failures continue to publish typed bounded terminal results only according to AUTO-0013 worker behavior.

## Logging and privacy

Operational logs are local-only by default.

Logs may include bounded service state such as startup, shutdown, configured repository portable identity, poll cycle failures, and known-safe error categories. Logs must not emit:

- GitHub tokens;
- OpenCode/provider credentials;
- environment dumps;
- `.env` contents;
- authorization headers;
- raw secret-bearing HTTP bodies;
- unrelated workstation information.

Public GitHub result redaction remains governed by AUTO-0013 and is not relaxed by AUTO-0014.

## Configuration

Runtime configuration must be explicit and minimal. Expected configuration includes:

- repository root/runtime project directory;
- repository portable identity `owner/name`;
- control issue identity;
- localhost OpenCode server URL;
- optional poll interval within bounded limits.

Secrets remain outside tracked repository files.

Configuration parsing must fail closed for malformed, missing, ambiguous, or non-loopback OpenCode endpoints.

## Installation boundary

AUTO-0014 may provide a generated or templated user-service definition and installation guidance.

Enabling the service is a local-machine configuration change and therefore remains an explicit operator action. The repository implementation must not silently install, enable, or start privileged services during normal package import, test execution, or CI.

Uninstall/disable behavior must be documented and reversible without mutating repository history.

## Verification requirements

Later implementation must prove at minimum:

- service starts the existing worker without changing its authority;
- one configured repository maps to one active worker instance;
- service restart after process failure does not create duplicate request execution;
- malformed service/runtime configuration fails closed;
- OpenCode remains localhost-only;
- worker still enforces AUTO-0013 task classes and repository invariants;
- public results remain bounded and safe;
- service logs do not contain secrets or machine-private data beyond the minimum local operational context;
- repository HEAD, branch, index, tracked/untracked state, Git config, and remotes remain unchanged by service startup/shutdown and read-only task execution;
- service disable/stop leaves the repository unchanged;
- existing AUTO-0007 through AUTO-0013 tests remain green.

## Non-goals

AUTO-0014 does not introduce:

- write/apply authority;
- autonomous coding or commits;
- remote start/stop commands;
- workstation webhooks or inbound listeners;
- public OpenCode exposure;
- private control-plane migration;
- GitHub Actions self-hosted runner authority;
- package/release/deployment automation;
- multi-repository execution;
- arbitrary scheduled shell commands;
- request replay/resume semantics;
- secret management infrastructure.

## Staged delivery contract

AUTO-0014 is delivered strictly in order:

1. **AUTO-0014-01 — Local Worker Service Design / Contract**: this document only; no production implementation.
2. **AUTO-0014-02 — Typed Runtime / Service Configuration**: strict local configuration model, validation, portable identity binding, and fail-closed defaults.
3. **AUTO-0014-03 — Single-Instance Worker Lifecycle**: process-level single-instance protection, bounded startup/shutdown behavior, and unchanged AUTO-0013 worker authority.
4. **AUTO-0014-04 — User Service Integration**: user-scoped service template/installer helpers with no implicit privileged mutation.
5. **AUTO-0014-05 — Installed Local-Service Verification**: real local verification proving automatic worker availability, bounded restart behavior, no duplicate execution, and unchanged repository state.
6. **AUTO-0014-06 — Final Evidence / Documentation Reconciliation**: authoritative closure evidence and documentation updates only.

Each stage requires its own pre-merge Quality SUCCESS and exact post-merge Quality SUCCESS before the next stage begins.

## Stage-01 completion rule

AUTO-0014-01 may be marked COMPLETE / VERIFIED only after this design-only change passes pre-merge Quality, is merged, and the exact resulting `master` commit passes post-merge Quality.

Production implementation must not begin before that gate is complete.
