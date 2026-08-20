# AI-Engineering Roadmap

## Completed / Verified

The documentation foundation, MCP foundation, SDK-0001, TOOL-0001, REL-0001/REL-0002/REL-0003, CI-0001, SAFE-0001/SAFE-0002, and AUTO-0001 through AUTO-0017 are COMPLETE / VERIFIED for their approved scopes.

Established automation boundaries remain layered and unchanged: AUTO-0007 is the permanent read-only reconciliation planner; AUTO-0008 is the guarded one-step apply boundary; AUTO-0009 is bounded multi-step orchestration; AUTO-0010 is the restrictive policy gate; AUTO-0011 is the optional explicit single-candidate approval gate; AUTO-0012 adds deterministic execution evidence; AUTO-0013 adds bounded read-only remote inspection/control transport; AUTO-0014 adds local worker lifecycle supervision; AUTO-0015 adds exact post-merge Quality verification; AUTO-0016 adds portable workstation bootstrap/doctor behavior plus the narrow read-only Quality relay; and AUTO-0017 reconciles canonical project state/roadmap documentation with the verified implementation state.

## AUTO-0014 — Local Control Worker Service / Lifecycle

**Status:** COMPLETE / VERIFIED

AUTO-0014 removed manual worker startup through local user-service lifecycle supervision around the existing AUTO-0013 read-only worker. Installed verification covered restart, single-instance, repository invariants, and successful read-only request behavior. AUTO-0014 final reconciliation is complete.

## AUTO-0015 — Exact Post-Merge Quality Verifier

**Status:** COMPLETE / VERIFIED

AUTO-0015 added deterministic read-only verification of the exact merged `master` Quality run. It requires workflow `.github/workflows/quality.yml`, branch `master`, event `push`, the exact target `head_sha`, terminal `completed` status, and successful conclusion. It fails closed when evidence is missing, ambiguous, incomplete, or inconsistent.

## AUTO-0016 — Workstation Bootstrap / Doctor

**Status:** COMPLETE / VERIFIED

AUTO-0016 delivered a portable workstation bootstrap contract, discovery-before-action rules, canonical worker identity `ai-engineering-worker.service`, a typed read-only workstation doctor with deterministic `READY` / `NOT_READY` semantics, a read-only doctor runtime/CLI, installed negative-path and isolated positive-path evidence, and a narrow read-only Quality relay that publishes typed exact post-merge evidence through the existing GitHub control channel.

## AUTO-0017 — Project State / Roadmap Reconciliation

**Status:** COMPLETE / VERIFIED

AUTO-0017 reconciled canonical project-state documentation with the verified implementation state through AUTO-0016 and completed a fresh post-reconciliation hardening audit. All five delivery stages are COMPLETE / VERIFIED, with exact post-merge Quality success on final merged `master` SHA `8a4375257882fd846bbb605c8791c04a6d602478`.

AUTO-0017 remained documentation-only in authority and did not expand runtime or execution behavior.

## AUTO-0018 — Read-Only Control Plane Reliability / Observability Hardening

**Status:** DESIGN ACTIVE

AUTO-0018 is the next selected milestone after AUTO-0017. Its design target is reliability and observability hardening of the existing read-only control plane while preserving all current authority boundaries.

AUTO-0018-01 is design/contract only. Proposed later stages cover typed protocol-rejection/failure taxonomy, polling/transport resilience, stale-workspace diagnostics without hidden repository mutation, installed/E2E evidence, and final reconciliation.

AUTO-0018 does not add remote write/apply authority, automatic repository repair, workflow rerun/cancel/dispatch, service-control mutation, credential mutation, deployment/publication/release scope, or expanded OpenCode authority.

## Current Priority

Complete AUTO-0018-01 design/contract through the normal exact pre-merge and post-merge Quality gates.

AUTO-0018 implementation stages that change runtime behavior require explicit approval after the design gate; design completion alone does not authorize implementation.
