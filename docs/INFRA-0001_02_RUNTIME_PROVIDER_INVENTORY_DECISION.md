# INFRA-0001-02 — OpenCode Runtime and Local-Model Provider Inventory / Decision

## Purpose

Record the exact repository-visible OpenCode/runtime inventory and make the
provider-level decision required by INFRA-0001 before any generalized local
coding-agent implementation.

INFRA-0001-02 is decision/evidence only. It does not install or upgrade
OpenCode, install a provider runtime, download a model, add `AGENTS.md`, add
`opencode.json`, create executable `repo-reader`/`implementer`/`verifier`
roles, broaden shell authority, change GitHub permissions, change Quality, or
authorize release/publication actions.

## Exact Baseline

This stage starts from exact `master`:

```text
0450a1180d3c7a98c8198682ffd5c64ac1167750
```

That commit is the merge of PR #209. Push-triggered Quality #432, run
`32557516312`, completed successfully for that exact `master`.

INFRA-0001-01 is therefore COMPLETE / VERIFIED before this decision begins.

## Repository-Visible OpenCode Inventory

The repository already has a bounded OpenCode integration and does not start
from a blank agent surface.

### Existing agent contract

```text
.opencode/agents/auto-0013-readonly.md
```

The existing agent is deny-by-default, read-only, workspace-bounded, blocks
sensitive `.env` paths, denies edits and external-directory access, and allows
only a narrow Git inspection command set.

INFRA-0001 must preserve this as a narrower existing authority baseline. The
future local interactive roles must not weaken or silently repurpose it.

### Existing OpenCode adapter

`src/ai_engineering/opencode_readonly_adapter.py` establishes these runtime
facts:

```text
agent:        auto-0013-readonly
default URL:  http://127.0.0.1:4096
transport:    local HTTP only
workspace:    explicit absolute repository directory
session API:  POST /session
message API:  POST /session/{id}/message
```

The adapter rejects non-loopback hosts and non-HTTP schemes. It captures Git
state before and after OpenCode execution and fails closed if repository state
changes.

The snapshot includes branch, exact HEAD, porcelain status, index state,
working-tree diff, cached diff, local Git configuration, and remotes. This is
already a stronger invariant than merely checking `git status` after a run.

### Existing service/runtime boundary

`src/ai_engineering/opencode_service_config.py` independently validates a
loopback OpenCode server URL and defaults to:

```text
http://127.0.0.1:4096
```

The service configuration does not perform environment expansion and requires
an explicit absolute repository root.

`src/ai_engineering/opencode_user_service.py` defines a user-scoped systemd
service integration for the bounded control worker. Its rendered service uses:

```text
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=read-only
Restart=on-failure
```

The existing user-service layer is therefore Linux/systemd-oriented and is
compatible with the established WSL execution boundary. INFRA-0001 does not
convert this into a Windows service or grant broader host access.

### Existing GitHub boundary

AUTO-0013 through AUTO-0019 remain a separate read-only task/control plane.
The control worker may publish bounded control evidence through its existing
contract, but INFRA-0001 does not turn that channel into a generic coding-agent
write path.

## Workstation Evidence Boundary

The repository does **not** encode enough evidence to truthfully claim any of
the following for the current workstation:

```text
exact installed OpenCode version
exact OpenCode installation method
exact provider runtime version
installed local-model inventory
GPU / VRAM / RAM suitability for a specific model
measured context-window behavior
measured tool-call reliability for a selected model
measured structured-output reliability
```

Those values are intentionally not guessed from repository state.

The previously exercised project runtime establishes a WSL/user-systemd
execution environment for the AI-Engineering worker, but this decision does not
turn historical interactive observations into a pinned OpenCode binary/model
version.

Before INFRA-0001-03 may bind an executable model profile, a fresh local probe
must record at minimum:

```text
opencode --version
OpenCode executable resolution / installation mode
provider runtime --version
provider endpoint reachability
provider model inventory
selected model identifier
reported context limit
reported tool-use capability
one bounded tool-call smoke result
one bounded malformed/failure result
```

That probe is evidence collection only. It may not install or download missing
components without separate authority.

## Current Upstream Capability Inventory

As of this decision, current OpenCode documentation explicitly supports local
models and documents multiple local-provider paths, including Ollama,
LM Studio, and OpenAI-compatible local servers such as llama.cpp.

For the provider decision, the relevant differences are:

### Ollama

- first-class documented local-model path;
- default loopback endpoint at `127.0.0.1:11434` / OpenAI-compatible `/v1`;
- automatic local model discovery in current OpenCode behavior;
- capability discovery can expose context, vision, and tool-use metadata;
- no external API credential is required for an unauthenticated local endpoint;
- provider/model selection can remain fully local.

### LM Studio

- also a documented local-model path;
- default loopback endpoint at `127.0.0.1:1234`;
- automatic local model discovery is supported;
- useful interactive desktop model management, but it introduces a separate GUI
  runtime surface that is not required by the existing WSL/systemd project
  boundary.

### llama.cpp / generic OpenAI-compatible server

- documented and fully local;
- offers a small direct serving surface;
- requires more explicit provider/model capability declaration and operational
  configuration when OpenCode cannot infer the server's actual limits or tool
  support.

## Provider Decision

**Selected provider baseline: Ollama, local loopback only.**

The decision is provider-level, not model-level.

Rationale:

1. It satisfies the local-first/token-cost objective without requiring an
   external paid-model credential for the normal local path.
2. Current OpenCode supports Ollama as a local provider and can discover local
   models and their advertised capabilities.
3. Its loopback-only deployment fits the existing repository pattern of keeping
   OpenCode-facing services on localhost.
4. It does not require introducing a GUI service into the WSL-centered worker
   boundary.
5. It keeps the eventual `opencode.json` provider surface small and
   reproducible while still permitting an explicit future model profile.

The selected intended provider endpoint is:

```text
http://127.0.0.1:11434
```

When an OpenAI-compatible provider URL is required by the OpenCode
configuration surface, the corresponding intended base URL is:

```text
http://127.0.0.1:11434/v1
```

No non-loopback provider endpoint is approved by this stage.

## Model Decision

**No exact local model is selected in INFRA-0001-02.**

Selecting a model before collecting fresh workstation resource and tool-use
evidence would fabricate compatibility.

INFRA-0001-03 may bind a model only after the fresh local probe demonstrates
that the candidate satisfies all of these minimum requirements:

- code-oriented behavior appropriate for repository inspection and bounded
  implementation;
- tool calling available and operational through OpenCode;
- sufficient context for the approved task class;
- bounded textual/structured result behavior usable by the verifier contract;
- deterministic failure that can be classified as `FAIL`, `BLOCKED`, or
  `ESCALATE` rather than hidden fallback;
- acceptable local resource use on the actual workstation.

The model profile must record its exact provider/model ID. `latest`-style or
otherwise floating model identity is not acceptable for reproducible evidence.

## Context and Tool-Calling Decision

The design contract mentioned 16k–32k class context only as a practical local
starting point; INFRA-0001-02 does not turn a generic advertised context size
into a repository guarantee.

For implementation eligibility:

- advertised context must be recorded from the provider/OpenCode inventory;
- the role configuration must not claim a larger usable context than the fresh
  evidence supports;
- tool use must be tested with the actual selected model, not inferred from
  family name;
- a model that produces good prose but unreliable tool calls is not eligible
  for `implementer`;
- `repo-reader` may use a narrower profile only if all its allowed operations
  remain deterministic and bounded.

## Structured Output Decision

INFRA-0001 does not require provider-native JSON-schema generation as a source
of authority.

Where structured evidence is required, repository code or a deterministic
wrapper must validate the returned shape. Model output is untrusted until it
passes that validator.

A provider/model that cannot reliably produce the required bounded text or
validated structure must return `FAIL`/`ESCALATE`; the integration must not
silently switch to a cloud model or relax validation.

## Network and Credential Boundary

The normal local execution path selected by this stage is:

```text
OpenCode -> loopback Ollama -> local model
```

No external provider network call is part of the selected normal path.

This stage does not authorize:

- OpenCode cloud/Zen provider use;
- Ollama Cloud use;
- automatic external-model fallback;
- committing provider credentials;
- reading unrelated existing OpenCode credentials;
- uploading repository content for fallback completion.

Codex escalation remains a separate, explicit higher-reasoning path governed by
INFRA-0001, not an automatic provider fallback hidden inside OpenCode.

## OpenCode Runtime Decision

The existing repository contract keeps OpenCode itself as a localhost service
at:

```text
http://127.0.0.1:4096
```

INFRA-0001-03 must preserve this boundary unless a later design explicitly
changes it.

The preferred execution boundary for the repository-local integration is WSL,
co-located with the existing user-systemd worker/runtime and Git workspace
access already exercised by the project.

Windows-native OpenCode remains a compatibility option, not the selected
primary runtime for INFRA-0001. This avoids creating two simultaneously
authoritative filesystem/runtime views of the same working tree.

## Provider Failure and Fallback Policy

Ollama unavailability, missing model, unsupported tool use, context failure, or
malformed output must fail closed.

Allowed terminal behavior is:

```text
PASS
FAIL
BLOCKED
ESCALATE
```

Automatic fallback from Ollama to a paid/cloud provider is not approved.

`ESCALATE` means return control to the higher-level workflow for a separately
approved Codex path; it does not grant OpenCode new credentials or authority.

## INFRA-0001-03 Preconditions

INFRA-0001-03 is not automatically authorized by completion of this stage.
Before its implementation begins, the following evidence must be available:

1. exact INFRA-0001-02 PR-head Quality success;
2. expected-head-protected merge;
3. exact push-triggered post-merge Quality success;
4. fresh local OpenCode version/install-mode probe;
5. fresh local Ollama version/endpoint/model inventory;
6. one explicitly selected exact model ID with recorded advertised limits;
7. bounded tool-call smoke evidence for that exact model;
8. confirmation that the provider remains loopback-only;
9. separate human approval for INFRA-0001-03.

If the local probe shows Ollama is unavailable or materially incompatible, that
is `BLOCKED`; the provider decision must be revisited explicitly rather than
silently substituting another backend.

## Release / AUTO / REL Boundary

This decision does not change the canonical AUTO state, fabricate AUTO-0023,
or modify the existing AUTO-0013 through AUTO-0019 control authority.

REL-0004 remains a separate release-governance namespace. Landing this document
does not automatically include INFRA-0001 work in a future `0.3.0` candidate.

## INFRA-0001-02 Completion Rule

INFRA-0001-02 is COMPLETE / VERIFIED only after this exact decision passes
PR-head Quality, expected-head-protected merge, and push-triggered post-merge
Quality on the resulting exact `master`.

Completion selects only the **Ollama local loopback provider baseline** and the
**WSL-local primary execution boundary**. It does not authorize installation,
model download, model selection without fresh evidence, INFRA-0001-03 changes,
GitHub write expansion, Quality modification, or release action.
