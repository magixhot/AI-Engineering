# AUTO-0016 — Workstation Bootstrap and Doctor Design

Status: DESIGN / PENDING GATE

## Purpose

Define a reproducible, explicit workstation bootstrap and read-only workstation prerequisite doctor for the AI-Engineering control-plane environment without expanding repository or execution authority.

AUTO-0016 exists to make a fresh workstation setup deterministic and auditable while keeping public repository content portable and free of machine-specific secrets or private paths.

## Scope

AUTO-0016 covers three deliberately separate layers.

### 1. Portable repository prerequisites

Document the portable prerequisites needed to run the project on a supported workstation, including Windows with WSL2, a Linux distribution with systemd user services, Git, Python, GitHub CLI, repository checkout expectations, and the project-local Python environment.

Portable documentation may name required tools, supported version constraints, commands, expected states, and validation criteria. It must not embed credentials, tokens, local usernames, absolute workstation paths, private account identifiers, or machine-specific environment values.

### 2. Local workstation configuration

Document the machine-local setup needed for the existing local control path: OpenCode installed and available on loopback, the project-local agent/configuration, localhost health verification, worker configuration, user systemd service installation, runtime directories, wrappers, and service-state verification.

Machine-local values must remain local. Public docs may describe placeholders and discovery procedures but must not publish real local usernames, home directories, repository absolute paths, token values, or unrelated workstation details.

### 3. External account and connector configuration

Document the boundary between local workstation setup and external account/connector configuration. GitHub authentication and any external ChatGPT/GitHub connector setup are external account state, not repository-owned local configuration.

The bootstrap may explain how to verify that required external authentication exists, but must not store credentials or imply that repository code can provision external accounts or connectors.

## Required bootstrap path

The final bootstrap documentation must provide a deterministic path for a fresh workstation covering:

1. Windows prerequisites and WSL2 readiness.
2. Linux distribution and systemd readiness.
3. Git, Python, and GitHub CLI availability.
4. GitHub authentication verification without exposing credentials.
5. Repository clone and exact-state verification.
6. Project dependency/environment setup.
7. OpenCode installation/configuration and project agent availability.
8. OpenCode loopback health verification.
9. Worker configuration using machine-local values.
10. systemd user-service installation and daemon reload.
11. Runtime directory and wrapper expectations.
12. Worker service active/running verification.
13. Read-only end-to-end control-channel verification.
14. Clear separation of external ChatGPT/GitHub connector state from local machine state.
15. A final `NEW WORKSTATION READY` checklist.

## Read-only workstation doctor

AUTO-0016 will add a read-only `workstation doctor` capability after the documentation contract is accepted.

The doctor must inspect and report prerequisite state only. Its intended checks include:

- WSL/Linux environment suitability;
- systemd user-service availability;
- Git availability;
- supported Python availability;
- GitHub CLI availability;
- GitHub authentication presence;
- repository identity and expected checkout state;
- OpenCode loopback health;
- worker configuration presence/shape without printing secret or private values;
- installed user-service unit presence;
- worker active/running state;
- read-only control-channel readiness where safely observable.

The doctor must fail closed when a prerequisite cannot be determined safely. It must not silently install packages, change configuration, start/enable services, write credentials, repair repository state, mutate refs, trigger workflows, or invoke any write/apply authority.

## Troubleshooting coverage

The bootstrap must include bounded troubleshooting for known workstation setup failure classes, including:

- PowerShell command versus WSL/Linux command context mistakes;
- Python `ModuleNotFoundError` caused by running outside the project environment;
- missing user-service unit or missing daemon reload;
- runtime-directory or `ProtectSystem` incompatibilities;
- OpenCode localhost health failures and HTTP 5xx responses;
- GitHub authentication unavailable or insufficient for the required read-only checks.

Troubleshooting must prefer diagnosis and explicit operator actions. No hidden repair path is authorized.

## Authority boundary

AUTO-0016 does not add local write/apply authority, remote mutation task classes, workflow rerun/cancel/dispatch authority, merge authority, repository/ref mutation authority, service-control authority, deployment/publication authority, credential provisioning, or hidden installation.

Any future command that installs software, writes workstation configuration, enables/starts services, changes authentication, or mutates repository state requires a separate explicit authority contract.

## Proposed delivery stages

1. AUTO-0016-01 — Design / Contract.
2. AUTO-0016-02 — Portable Workstation Bootstrap Documentation.
3. AUTO-0016-03 — Typed Read-Only Workstation Doctor Model.
4. AUTO-0016-04 — Read-Only Doctor Runtime / CLI.
5. AUTO-0016-05 — Fresh-Workstation or Isolated Verification Evidence.
6. AUTO-0016-06 — Final Evidence / Documentation Reconciliation.

Each stage follows the project gate: pre-merge Quality success, merge through expected-head protection, and exact post-merge Quality verification before advancing.

## Completion rule

AUTO-0016 is complete only when the bootstrap path is documented, the read-only doctor is implemented and tested, verification evidence demonstrates the intended checks without secret/private-data leakage or mutation authority, and final documentation reconciles the exact verified state.
