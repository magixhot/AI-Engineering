# AUTO-0003-04 Verification Matrix

Status: IN REVIEW

| Boundary | Verification |
|---|---|
| CLI discovery | `project docs ownership --help` lists check, plan, apply |
| Read-only check | reports missing/initialized ownership without writes |
| Read-only plan | deterministic update digests and manual-review boundaries |
| Guarded apply | delegates to AUTO-0003 atomic apply and verification |
| Manual review | apply fails closed with no document mutation |
| Idempotency | second apply changes zero documents |
| AUTO-0002 handoff | `project docs check` reports clean after ownership apply |
| Git invariants | HEAD and staged index remain unchanged |
| Distribution | wheel is built, installed into isolated venv, and console script executes ownership workflow |
