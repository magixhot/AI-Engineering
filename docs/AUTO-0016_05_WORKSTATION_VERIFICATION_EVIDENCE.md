# AUTO-0016-05 — Workstation Verification Evidence

Status: VERIFICATION EVIDENCE / PENDING GATE

## Purpose

Record public-safe verification evidence for the AUTO-0016 workstation bootstrap and read-only doctor without publishing machine-local absolute paths, usernames, credentials, environment values, or unrelated workstation details.

This stage combines isolated deterministic coverage for the positive path with installed-workstation negative-path evidence from a real workstation.

## Verified baseline

The installed verification was performed after the workstation checkout was updated to exact `master`:

```text
a22343cc4896e55be245cccfd809602c2fd39340
```

The preceding AUTO-0016-04 exact post-merge Quality gate was independently satisfied for the same exact master state before this verification stage began.

## Installed workstation doctor evidence

The read-only doctor was executed against the real installed workstation using the current repository checkout.

Public-safe observed result:

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

Machine-local values emitted by the local doctor, including absolute repository/config paths and local usernames, are intentionally omitted from this public evidence.

## Installed drift confirmation

A separate bounded read-only diagnosis confirmed the doctor finding:

- the configured loopback OpenCode health endpoint was unreachable;
- no listener was observed on the configured loopback port;
- the canonical `ai-engineering-worker.service` remained loaded, active, and running;
- no repository mutation, package installation, credential change, service start/restart, or hidden repair was performed.

Therefore `OPENCODE_UNAVAILABLE` was a real installed prerequisite failure rather than a false-positive doctor classification.

## Fail-closed behavior demonstrated

The installed result demonstrates the intended fail-closed semantics:

- repository identity and checkout state were validated instead of guessed;
- the canonical worker unit was discovered and validated;
- the worker configuration was discovered from workstation state rather than copied from another workstation;
- GitHub authentication/control-channel readiness were independently checked;
- an unavailable required OpenCode loopback prerequisite caused `NOT_READY`;
- the doctor did not attempt automatic remediation.

This is the required safe behavior for an unknown or partially configured workstation.

## Positive-path isolated coverage

AUTO-0016-04 includes deterministic isolated tests for the corresponding positive doctor path. Those tests provide controlled evidence that, when all required observations are present and valid, the typed model returns `READY` and the CLI exits successfully.

The same test suite also covers fail-closed missing-unit behavior and typed CLI/report semantics.

The combination is deliberate:

1. isolated tests prove the deterministic `READY` path without relying on mutable workstation state;
2. installed verification proves that the real doctor correctly detects and reports a live workstation drift condition;
3. neither path requires expanding doctor authority into installation, repair, service control, or repository mutation.

## Additional bootstrap observation

The installed workstation did not provide `uv` on the interactive shell `PATH` used for verification. No package installation was performed. The doctor runtime itself was exercised through the repository source with the available Python interpreter, which preserved the read-only verification objective.

This observation remains a bootstrap/environment concern and does not weaken the installed doctor evidence above.

## Public-safety review

The public evidence intentionally excludes:

- local usernames;
- local absolute repository paths;
- local configuration paths;
- token or credential values;
- private environment variables;
- unrelated workstation metadata.

Only portable identities, typed states, exact repository SHA evidence, and public-safe classifications are retained.

## Authority boundary

AUTO-0016-05 adds no authority.

It does not authorize or perform:

- package installation;
- OpenCode installation/start/restart;
- worker service start/restart/enable/disable;
- workstation config writes;
- credential changes;
- workflow rerun/cancel/dispatch;
- merge/ref mutation beyond the normal staged repository gate;
- deployment/publication;
- repository write/apply task classes.

Observed failures remain diagnosis only.

## Verification conclusion

AUTO-0016-05 evidence supports the workstation doctor contract:

- deterministic positive behavior is covered in isolation;
- real installed negative behavior is fail-closed and correctly classified;
- discovery occurs before action;
- machine-local data remains out of public evidence;
- no hidden remediation or authority expansion occurs.

This stage is ready for the normal pre-merge Quality gate.