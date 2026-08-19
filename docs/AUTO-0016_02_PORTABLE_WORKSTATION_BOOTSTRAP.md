# AUTO-0016-02 — Portable Workstation Bootstrap

Status: IMPLEMENTATION / PENDING GATE

## Purpose

Define the portable, deterministic bootstrap path for an AI-Engineering workstation without embedding machine-specific paths, usernames, credentials, tokens, or private account state in the repository.

This stage intentionally separates portable logical identities from machine-local absolute paths. HOME, WORK, or any future workstation may use different filesystem locations while still conforming to the same workstation contract.

## Canonical logical identities

The following names are portable and must be treated as canonical unless a future design explicitly changes them:

- repository: `magixhot/AI-Engineering`;
- default branch: `master`;
- control issue: `#130`;
- user service unit: `ai-engineering-worker.service`;
- worker lifecycle entry point: `python -m ai_engineering.opencode_worker_lifecycle`;
- exact Quality workflow: `.github/workflows/quality.yml`;
- exact Quality branch/event tuple: `master` / `push`.

Absolute repository, config, runtime, Python, WSL, Windows, and home-directory paths are machine-local values and are not canonical portable identities.

## Discovery-before-action rule

A workstation must never be operated from guessed local paths or a service name copied from another machine.

Before any local update, service operation, diagnosis, or bootstrap action, discover the current workstation state read-only and establish at minimum:

1. current shell location and platform context;
2. repository checkout location, if present;
3. repository branch, exact HEAD, cleanliness, and remote identity;
4. installed matching user-service units;
5. active/running matching user-service units;
6. worker configuration location by inspecting the installed unit when present;
7. runtime-directory identity from the installed unit/configuration when present;
8. availability of required portable tools.

Discovery output is local operator evidence. Real absolute paths, usernames, credential locations, environment values, and unrelated workstation details must not be copied into public repository evidence.

## Portable prerequisite layers

### Windows and WSL2 layer

For Windows workstations, confirm that WSL2 is available and that the intended Linux distribution starts successfully. Commands intended for Linux/WSL must be run inside the Linux shell, not in PowerShell, unless a step explicitly says otherwise.

The Linux environment must support systemd user services for the installed-worker lifecycle.

### Linux tool layer

The workstation must provide:

- Git;
- Python compatible with the project requirement (`>=3.11`);
- GitHub CLI (`gh`);
- systemd user-service support;
- the project-local Python environment and locked development dependencies when repository validation is required.

Availability checks are read-only. Missing software is diagnosed, not silently installed.

### GitHub authentication layer

Use `gh auth status` or an equivalent read-only check to confirm that GitHub CLI authentication exists for the required repository operations.

Do not print tokens, authorization headers, credential-store contents, or environment secrets into shared logs or public evidence.

GitHub account state and ChatGPT/GitHub connector state are external configuration. Repository bootstrap does not provision either one.

## Repository discovery and identity verification

Do not assume a checkout path. Locate a candidate checkout first, then validate it from inside that repository.

The validated checkout must satisfy all applicable checks:

```text
branch = master
remote = magixhot/AI-Engineering
HEAD = explicitly observed SHA
working tree = observed clean or explicitly reported otherwise
```

A repository on the wrong branch, with the wrong remote identity, or with unexplained local changes is not silently repaired by the bootstrap contract.

Repository update commands such as fetch, pull, checkout, reset, clone, or ref mutation are operator-authorized actions outside the read-only doctor boundary.

## User-service discovery and reconciliation

The canonical worker unit name is:

```text
ai-engineering-worker.service
```

Before operating the worker, inspect user-service state instead of assuming installation:

```bash
systemctl --user is-system-running
systemctl --user list-unit-files --type=service | grep -i 'engineering\|opencode\|worker'
systemctl --user list-units --all --type=service | grep -i 'engineering\|opencode\|worker'
```

If `ai-engineering-worker.service` exists, inspect its effective unit definition before using machine-local config/runtime paths:

```bash
systemctl --user cat ai-engineering-worker.service
```

This inspection may reveal private local paths. Those values stay local and must be redacted from public verification evidence.

If no canonical unit exists, report `SERVICE_UNIT_MISSING`. Do not guess an alternate name and do not create/enable/start a unit automatically.

If a different historical worker unit exists, report `SERVICE_UNIT_DRIFT` and reconcile it only through an explicit operator-approved local change.

## Machine-local configuration boundary

The installed worker requires local configuration containing workstation-specific values such as repository root and local transport details. These values are intentionally not portable repository content.

Portable documentation may describe their schema and validation rules, but a workstation must discover or supply its own values locally.

The bootstrap and doctor must never publish:

- actual local usernames;
- actual home-directory paths;
- actual repository absolute paths;
- token or credential values;
- private environment values;
- unrelated workstation metadata.

## OpenCode boundary

OpenCode remains part of the existing local execution architecture for task classes that require it. It must remain loopback-only under the current design.

The `quality_verify` task is different: it is deterministic and read-only and is routed directly to the exact Quality verifier. It must not require an OpenCode request to validate a GitHub Actions Quality gate.

OpenCode availability or HTTP failures must therefore not block the `quality_verify` path when the installed worker and GitHub CLI read transport are otherwise healthy.

## Exact Quality relay readiness

An installed workstation is Quality-relay ready when all of the following are true:

- canonical worker service is installed and active;
- worker checkout contains the current relay implementation;
- GitHub CLI can read Actions evidence;
- control issue transport is readable/writable only to the already-authorized typed evidence channel;
- a `quality_verify` request for an exact master SHA can observe queued/in-progress evidence without premature terminal failure;
- the same request eventually publishes one typed terminal result after the exact run becomes terminal;
- successful evidence requires `.github/workflows/quality.yml`, branch `master`, event `push`, exact head SHA, `status=completed`, and `conclusion=success`.

No rerun, cancel, dispatch, merge, ref mutation, deployment, service-control, repository write/apply, or OpenCode authority is added by this readiness check.

## Deterministic bootstrap sequence

A fresh or unknown workstation should be handled in this order:

1. Establish PowerShell versus WSL/Linux command context.
2. Confirm WSL/Linux and systemd readiness.
3. Confirm Git, Python, and GitHub CLI availability.
4. Confirm GitHub CLI authentication without exposing credentials.
5. Discover an existing repository checkout; if absent, report it rather than inventing a path.
6. Validate repository identity, branch, HEAD, and cleanliness.
7. Confirm the project environment can be created/used according to repository dependency metadata.
8. Discover installed worker service units.
9. Require `ai-engineering-worker.service` as the canonical logical service identity.
10. Inspect the canonical unit to resolve local config/runtime paths instead of guessing them.
11. Validate worker configuration shape without printing machine-private values.
12. Validate loopback OpenCode health only for paths that depend on OpenCode.
13. Validate worker active/running state.
14. Validate the read-only GitHub control channel.
15. Validate exact Quality relay behavior where installed.
16. Report drift explicitly; do not silently repair it.
17. Mark the workstation `NEW WORKSTATION READY` only when all required checks are satisfied.

## Drift classifications

The workstation doctor introduced in later AUTO-0016 stages should use explicit drift concepts rather than implicit assumptions. At minimum:

- `REPOSITORY_MISSING`;
- `REPOSITORY_IDENTITY_DRIFT`;
- `BRANCH_DRIFT`;
- `WORKTREE_DIRTY`;
- `SERVICE_UNIT_MISSING`;
- `SERVICE_UNIT_DRIFT`;
- `SERVICE_INACTIVE`;
- `CONFIG_MISSING`;
- `CONFIG_INVALID`;
- `GITHUB_AUTH_UNAVAILABLE`;
- `OPENCODE_UNAVAILABLE` where OpenCode is required;
- `QUALITY_RELAY_UNAVAILABLE`;
- `READY`.

These names describe diagnosis only. They do not authorize remediation.

## Troubleshooting rules

### Commands run in the wrong shell

If a Linux command fails because it was run from PowerShell or a Windows shell, first establish the command context. Do not reinterpret the error as a missing Linux package or missing repository.

### Repository not found from the current directory

A `not a git repository` error means the current shell location is not a validated checkout. Search for the checkout read-only before issuing repository mutation commands.

### Unit not found

A `Unit ... not found` error means the assumed unit name is not verified on that workstation. Enumerate matching user units first. Do not copy a unit name from another workstation.

### Python module missing

If `python -m ai_engineering...` raises `ModuleNotFoundError`, verify that the command is using the intended project environment and checkout before installing anything globally.

### Runtime-directory or protection failure

If the worker cannot create its runtime directory under systemd hardening, inspect the generated/effective unit and current runtime-directory contract. Do not weaken service hardening silently.

### OpenCode HTTP failure

Local OpenCode HTTP 5xx evidence is diagnosed separately from deterministic `quality_verify`. Do not route exact Quality verification through OpenCode as a workaround.

## NEW WORKSTATION READY checklist

A workstation can be declared ready only when the operator or doctor has positive evidence for all required applicable items:

```text
[ ] correct shell/platform context established
[ ] WSL/Linux ready
[ ] systemd user manager ready
[ ] Git available
[ ] supported Python available
[ ] GitHub CLI available
[ ] GitHub authentication present
[ ] repository checkout discovered, not guessed
[ ] repository identity correct
[ ] branch and exact HEAD observed
[ ] worktree state observed
[ ] project environment usable
[ ] canonical ai-engineering-worker.service discovered or explicitly installed
[ ] effective unit inspected for local config/runtime identities
[ ] worker configuration valid without secret disclosure
[ ] worker active/running
[ ] OpenCode loopback healthy when required
[ ] control channel reachable
[ ] exact Quality relay verified when required
[ ] no unexplained drift remains
```

## Authority boundary

This document does not authorize installation, clone, checkout, pull, reset, config writes, credential changes, service installation, daemon reload, enable/start/restart, workflow mutation, merge/ref mutation, deployment, or any repository write/apply path.

It defines discovery, validation, diagnosis, and the explicit operator steps that may be performed only under the relevant existing or separately granted authority.
