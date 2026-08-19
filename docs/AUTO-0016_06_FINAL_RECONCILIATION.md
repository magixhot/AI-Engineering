# AUTO-0016-06 — Final Evidence / Documentation Reconciliation

Status: FINAL RECONCILIATION / PENDING GATE

## Purpose

Reconcile the delivered AUTO-0016 workstation-bootstrap and read-only doctor work against the accepted design, verified implementation stages, installed evidence, and authority boundary.

This document is the final stage record for AUTO-0016. It does not add runtime behavior or authority.

## Reconciled scope

AUTO-0016 now provides:

- a portable workstation bootstrap contract that separates repository prerequisites, workstation-local configuration, and external account/connector state;
- discovery-before-action rules that prohibit copying workstation-specific paths or service names from another machine;
- the canonical worker unit identity `ai-engineering-worker.service`;
- a typed read-only workstation doctor model with deterministic `READY` / `NOT_READY` semantics;
- a read-only doctor runtime and public CLI path;
- explicit fail-closed classifications for missing, invalid, unavailable, or drifting prerequisites;
- installed-workstation negative-path evidence and isolated positive-path coverage;
- a read-only exact post-merge Quality relay used to obtain deterministic terminal gate evidence without workflow mutation authority.

## Stage reconciliation

### AUTO-0016-01 — Design / Contract

The design established the three-layer workstation model, public/private data boundary, doctor authority boundary, deterministic bootstrap requirements, and staged completion rule.

During implementation, the Quality relay was introduced and hardened as a narrow read-only control-plane prerequisite before later AUTO-0016 stages proceeded. Its final installed pending-to-terminal behavior was verified before AUTO-0016-02 began.

Verified implementation baseline entering AUTO-0016-02:

```text
5683ea917e7c0ed960fb72aeb2643adc3e4bf009
```

### AUTO-0016-02 — Portable Workstation Bootstrap Documentation

The portable bootstrap documents logical identities instead of machine-specific absolute paths. It requires current-workstation discovery before action, separates Windows/WSL command contexts, documents repository and service readiness, preserves local-only values, and defines the `NEW WORKSTATION READY` path without hidden repair.

Exact verified post-merge master:

```text
6eda7f4e5c1465ae01bb86a0eaaa8f4fbde33818
```

### AUTO-0016-03 — Typed Read-Only Workstation Doctor Model

The typed model defines the canonical checks, `PASS` / `FAIL` / `UNKNOWN` states, strict summaries, deterministic ordering, and fail-closed overall readiness.

Exact verified post-merge master:

```text
5756dc801ddcaf47965b8e4d68006eb81db5f544
```

### AUTO-0016-04 — Read-Only Doctor Runtime / CLI

The runtime implements discovery-before-action for Linux/WSL suitability, systemd user availability, Git, Python, GitHub CLI/authentication, repository identity/state, worker unit/config discovery, worker activity, loopback OpenCode health, and the existing control issue.

The public CLI exposes:

```text
ai-engineering workstation doctor
```

The runtime does not install, repair, start, stop, restart, enable, disable, authenticate, mutate repository state, or trigger workflow changes.

Exact verified post-merge master:

```text
a22343cc4896e55be245cccfd809602c2fd39340
```

The exact post-merge Quality relay evidence for this state used push run `32264710791` with `completed/success` and `satisfies_gate=true`.

### AUTO-0016-05 — Fresh-Workstation or Isolated Verification Evidence

Verification combines deterministic isolated positive-path coverage with a real installed-workstation negative-path observation.

Public-safe installed result:

```text
workstation_readiness=NOT_READY
wsl_linux=PASS
systemd_user=PASS
git=PASS
python=PASS
github_cli=PASS
github_auth=PASS
repository=PASS
worker_unit=PASS
worker_config=PASS
opencode_loopback=FAIL OPENCODE_UNAVAILABLE
worker_active=PASS
control_channel=PASS
```

A separate bounded read-only diagnosis confirmed that the configured loopback endpoint was unavailable while the canonical worker remained active. No package installation or service-control repair was performed.

Machine-local usernames, absolute repository/configuration paths, environment values, and credentials were excluded from public evidence.

Exact verified post-merge master:

```text
39e9de4d3b44c868b4a0703c31d2f100c86dcc65
```

The exact post-merge Quality relay evidence for this state used push run `32267549326` with `completed/success` and `satisfies_gate=true`.

## Quality relay reconciliation

The Quality relay remains a narrow read-only verification path.

It validates the exact tuple:

- repository `magixhot/AI-Engineering`;
- workflow `.github/workflows/quality.yml`;
- branch `master`;
- event `push`;
- exact target `head_sha`;
- terminal `completed/success` evidence.

Pending and temporary unavailable states are retried boundedly instead of being terminalized immediately. The relay does not gain rerun, cancel, dispatch, merge, ref mutation, repository write/apply, service-control, deployment, or credential authority.

## Workstation portability reconciliation

AUTO-0016 intentionally does not define one physical filesystem layout for every workstation.

The portable contract is based on logical roles and discovered current-machine state. In particular:

- repository absolute paths are workstation-local;
- worker configuration absolute paths are workstation-local;
- the canonical worker service identity is `ai-engineering-worker.service`;
- the doctor discovers and validates current state instead of importing assumptions from another workstation;
- public evidence retains typed classifications and exact repository identities while excluding private machine-local values.

## Installed observation retained as a diagnostic finding

The installed verification workstation exposed two environment observations:

1. interactive-shell `uv` availability was absent;
2. the required OpenCode loopback endpoint was unavailable at verification time.

Neither observation was silently repaired. `OPENCODE_UNAVAILABLE` correctly caused fail-closed `NOT_READY`.

These findings do not expand AUTO-0016 authority. Any future package installation, OpenCode lifecycle control, worker lifecycle mutation, or workstation configuration write requires explicit separate authority.

## Public-safety reconciliation

The delivered public documentation and evidence must not contain real workstation:

- usernames;
- home-directory paths;
- repository absolute paths;
- worker configuration absolute paths;
- credential or token values;
- private environment values;
- unrelated machine metadata.

AUTO-0016-05 evidence follows this rule by publishing only public-safe typed states and portable identities.

## Authority boundary — final state

AUTO-0016 does **not** authorize:

- local write/apply operations;
- package installation or hidden bootstrap repair;
- OpenCode install/start/restart authority;
- worker start/restart/enable/disable authority;
- workstation configuration writes;
- credential provisioning or authentication changes;
- workflow rerun/cancel/dispatch;
- new merge/ref mutation authority;
- deployment/publication authority;
- new remote repository write/apply task classes.

The workstation doctor remains inspection/reporting only.

## Completion rule for this stage

AUTO-0016-06 follows the normal repository gate:

1. pre-merge Quality must complete successfully for the exact PR head;
2. merge must use expected-head protection;
3. exact post-merge push Quality for the resulting `master` SHA must be verified through the read-only relay.

When all three conditions are satisfied, AUTO-0016 is `COMPLETE / VERIFIED` and no additional AUTO-0016 implementation stage remains.
