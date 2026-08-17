# ADR-0001 — AI Infrastructure Layered Architecture

**Status:** ACCEPTED  
**Date:** 2026-08-17  
**Scope:** AI Infrastructure  
**Owner:** AI-Engineering  

---

## 1. Context

AI Infrastructure has evolved from the original `AI-Archive-Server` Runtime project into a broader engineering ecosystem.

Two repositories now have distinct but related responsibilities:

- `AI-Engineering` provides the engineering platform, standards, tooling, MCP capabilities, automation and quality controls.
- `AI-Archive-Server` implements `RT-0008`, the first Runtime project of AI Infrastructure and the Model Archive layer.

Historically, `AI-Archive-Server` also contained documentation describing the wider `AI Infrastructure` system. This was appropriate while it was the first and primary implementation, but it no longer provides a sufficient architectural separation as additional Runtime projects and the Engineering platform evolve independently.

The architecture therefore requires an explicit layered model that preserves the existing projects while clarifying ownership, dependencies and future extension points.

---

## 2. Decision

AI Infrastructure is defined as a **single system composed of distinct architectural layers**.

```text
AI Infrastructure
│
├── Engineering Layer
│   └── AI-Engineering
│       ├── Engineering MCP
│       ├── SDK / Project Templates
│       ├── Standards / Documentation
│       ├── CI / Quality Gates
│       ├── Safety
│       └── Automation
│
├── Runtime Layer
│   ├── RT-0008 — AI-Archive-Server
│   ├── RT-0009 — AI-Runtime
│   ├── RT-0010 — AI-Deployment
│   └── future Runtime projects
│
└── Infrastructure / Deployment Layer
    ├── Docker / Compose
    ├── Storage
    ├── Networking
    ├── Synology DS925+
    └── future execution platforms
```

### 2.1 Engineering Layer

`AI-Engineering` is the Engineering Platform for AI Infrastructure.

It defines and provides the reusable engineering mechanisms used to create, validate, maintain and automate Runtime projects.

The Engineering Layer may provide tooling and interfaces consumed by Runtime projects, but it must not absorb Runtime-specific business or implementation responsibilities.

### 2.2 Runtime Layer

Runtime projects are independent projects within AI Infrastructure, each with a defined responsibility and project identifier.

`RT-0008 — AI-Archive-Server` is the first Runtime project and owns the Model Archive layer.

Future Runtime projects such as `RT-0009` and `RT-0010` remain separate projects and must not be implemented as hidden subcomponents of `AI-Engineering`.

### 2.3 Infrastructure / Deployment Layer

Execution platforms such as Synology DS925+, Docker Compose, storage and networking are infrastructure concerns.

They host or support Engineering and Runtime components but do not define the logical architecture of AI Infrastructure.

The architecture therefore remains portable across physical hosts and deployment environments.

---

## 3. Dependency Direction

The preferred dependency direction is:

```text
Engineering Layer
        │
        ▼
Runtime Layer
        │
        ▼
Infrastructure / Deployment Layer
```

This does **not** mean that every Runtime component must depend directly on every Engineering component. Dependencies must remain explicit and minimal.

The Engineering Layer must not depend on the internal implementation details of a specific Runtime project.

Runtime projects may consume approved Engineering capabilities, standards and interfaces.

Infrastructure provides execution resources and deployment mechanisms and must not become the owner of Runtime or Engineering semantics.

---

## 4. Engineering MCP Boundary

Engineering MCP is an Engineering Layer capability.

It is not a generic uncontrolled file-system bridge and it is not part of `AI-Archive-Server`.

Where workspace access is required, the preferred model is:

```text
AI Assistant
    │
    ▼
Engineering MCP
    │
    ▼
Project Workspace
    │
    ├── local workstation
    ├── Git repository
    ├── synchronized workspace
    └── Synology / other infrastructure
```

Workspace identity must be logical and project-oriented. Engineering tooling must not encode machine-specific absolute paths such as `C:\...` or `D:\...` into portable project logic.

The exact workspace-access capability is a separate future design/contract and is **not** authorized by this ADR.

---

## 5. Project Documentation Ownership

The architectural separation is reflected in documentation ownership.

### Global AI Infrastructure documentation

Defines:

- overall architecture;
- project registry;
- cross-project relationships;
- global roadmap;
- global architectural decisions.

### AI-Engineering documentation

Defines the Engineering Platform itself, including its MCP, SDK, standards, automation, safety and quality mechanisms.

### Runtime project documentation

Each Runtime repository defines its own implementation, runtime milestones, APIs, components and project-specific decisions.

Existing historical documentation is preserved. Migration or relocation of documents is performed incrementally and must not destroy project history.

---

## 6. Capability and Milestone Separation

Engineering capabilities and Runtime milestones use separate identifiers and lifecycles.

```text
AUTO-*  → AI-Engineering capabilities
HF-*    → AI-Archive-Server Runtime milestones
RT-*    → Runtime project identity
```

These identifiers must not be merged or renumbered merely to make the projects appear synchronized.

Cross-project dependencies are expressed explicitly in documentation when required.

---

## 7. AI-Archive-Server Position

`AI-Archive-Server` remains the first Runtime project of AI Infrastructure.

Its responsibility is the Model Archive layer, including the model acquisition, storage, registry and related archive services defined by its own project documentation.

AI-Archive-Server remains independent from AI-Engineering at the implementation level while consuming applicable Engineering standards and capabilities.

The Archive Server remains the authoritative model source for Runtime components according to its existing architecture decisions.

---

## 8. Synology Position

Synology DS925+ is an execution and infrastructure platform, not a separate logical project layer.

It may host Runtime services, Engineering services, storage and related infrastructure through approved deployment mechanisms such as Docker Compose and SSH.

No AI Infrastructure architectural dependency may be introduced solely because a component is currently hosted on Synology.

---

## 9. Consequences

### Positive consequences

- Clear separation between engineering tooling and Runtime products.
- `AI-Archive-Server` can evolve without becoming the architectural root of all future systems.
- `AI-Engineering` can serve multiple Runtime projects.
- Synology remains replaceable as a physical execution platform.
- Logical project paths remain portable across workstations.
- AUTO, HF and RT identifiers retain clear meanings.
- Future AI Infrastructure projects can be added without restructuring the existing repositories.

### Negative consequences

- Some historical documentation will temporarily exist at multiple levels.
- A future reconciliation of the global Master Index is required.
- Cross-project changes require explicit documentation of ownership and dependencies.

---

## 10. Non-Goals

This ADR does not:

- implement a new MCP capability;
- grant file-system mutation authority to AI;
- define a Synology deployment architecture;
- change the current AUTO-0012 authority boundaries;
- change the HF milestone sequence of AI-Archive-Server;
- move or delete existing documentation;
- replace existing project standards.

Any such capability requires its own design, contract or architectural decision as appropriate.

---

## 11. Migration Strategy

The architecture is adopted incrementally.

1. Preserve existing repositories and project history.
2. Treat `AI-Engineering` as the Engineering Platform.
3. Treat `AI-Archive-Server` as `RT-0008` Runtime project.
4. Establish or reconcile the global AI Infrastructure Master Index.
5. Reconcile documentation ownership without destructive moves.
6. Define future cross-project capabilities through explicit design/contract documents.

No repository-wide restructuring is required as a prerequisite for adopting this ADR.

---

## 12. Relationship to Current Project State

At the time of this decision:

- `AI-Engineering` is at release line `0.2.0`.
- AUTO-0001 through AUTO-0012 are complete/verified for their approved scopes.
- No AUTO capability milestone is active.
- `AI-Archive-Server` is `RT-0008` and continues its own HF milestone lifecycle.

This ADR reconciles architectural ownership; it does not alter those implementation states.

---

## 13. Future Work

The following are intentionally deferred until their own design/contract work is completed:

- Engineering MCP project-workspace access;
- global AI Infrastructure Master Index reconciliation;
- formal cross-project dependency representation;
- deployment architecture for Synology and other execution platforms.

---

## 14. Decision Summary

> **AI Infrastructure is one system with separate Engineering, Runtime and Infrastructure/Deployment concerns. `AI-Engineering` is the Engineering Platform. `AI-Archive-Server` is `RT-0008`, the first Runtime project. Runtime projects may consume Engineering capabilities, while Engineering remains independent of Runtime implementation details. Physical platforms such as Synology host the system but do not define its logical architecture.**

---

**End of ADR-0001**
