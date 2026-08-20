# AI-Engineering Roadmap

## Completed / Verified

The documentation foundation, MCP foundation, SDK-0001, TOOL-0001, REL-0001/REL-0002/REL-0003, CI-0001, SAFE-0001/SAFE-0002, and AUTO-0001 through AUTO-0016 are COMPLETE / VERIFIED for their approved scopes.

Established automation boundaries remain layered and unchanged: AUTO-0007 is the permanent read-only reconciliation planner; AUTO-0008 is the guarded one-step apply boundary; AUTO-0009 is bounded multi-step orchestration; AUTO-0010 is the restrictive policy gate; AUTO-0011 is the optional explicit single-candidate approval gate; AUTO-0012 adds deterministic execution evidence; AUTO-0013 adds bounded read-only remote inspection/control transport; AUTO-0014 adds local worker lifecycle supervision; AUTO-0015 adds exact post-merge Quality verification; and AUTO-0016 adds portable workstation bootstrap/doctor behavior plus the narrow read-only Quality relay.

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

**Status:** ACTIVE — FINAL EVIDENCE

AUTO-0017 reconciles canonical project-state documentation with the verified implementation state before any new execution authority is considered.

### Delivery status

- AUTO-0017-01 — Design / Contract: COMPLETE / VERIFIED.
- AUTO-0017-02 — Canonical Roadmap Reconciliation: COMPLETE / VERIFIED.
- AUTO-0017-03 — Project Context / Start-State Reconciliation: COMPLETE / VERIFIED.
- AUTO-0017-04 — Cross-Document Consistency Audit: COMPLETE / VERIFIED.
- AUTO-0017-05 — Final Evidence / Next-Milestone Selection: ACTIVE.

AUTO-0017 is documentation-only in authority and does not expand runtime or execution behavior.

## Fresh post-reconciliation selection

The corrected project state shows that the safest next design target is reliability and observability hardening of the existing read-only control plane, not new execution authority.

Selected next milestone candidate:

**AUTO-0018 — Read-Only Control Plane Reliability / Observability Hardening**

The candidate is selected for design only. AUTO-0017 does not preapprove AUTO-0018 implementation, automatic repository repair, new remote write/apply authority, workflow mutation, service-control mutation, credentials, publication, deployment, or release changes.

## Current Priority

Complete AUTO-0017-05 by merging final reconciliation evidence and verifying exact post-merge Quality on the resulting `master` SHA.

After AUTO-0017 completes, AUTO-0018 may begin with a separate design/approval gate focused on read-only control-plane reliability and operator-visible diagnostics while preserving all existing authority boundaries.
