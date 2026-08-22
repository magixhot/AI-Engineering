# Local Agent Workstation Setup

## Scope

This is the canonical workstation setup for the INFRA-0001 local-agent layer.
It covers Linux/WSL execution of OpenCode against a loopback Ollama provider.
The repository remains the authority source for provider and agent configuration.

The setup does not grant merge, protected-branch push, release, credential,
GitHub mutation, Quality bypass, or broader shell authority.

## Canonical repository inputs

The clone carries all governance-critical configuration:

- `AGENTS.md` — authority and terminal-outcome contract;
- `opencode.json` — loopback Ollama provider and `qwen3:4b` model identity;
- `.opencode/agents/repo-reader.md`;
- `.opencode/agents/implementer.md`;
- `.opencode/agents/verifier.md`;
- `scripts/local-opencode-run.sh` — governed role launcher;
- `scripts/bootstrap-local-agent.sh` — idempotent workstation preparation;
- `scripts/verify-local-agent.sh` — read-only readiness and smoke verification.

Critical provider or permission configuration must not exist only under
`~/.config/opencode/`. User-level configuration may add unrelated providers,
but the AI-Engineering local path must continue to be reproducible from the
repository configuration.

## Supported baseline

The INFRA-0001 verified baseline is:

- Linux or WSL runtime;
- OpenCode `>= 1.18.18`;
- Ollama loopback API at `127.0.0.1:11434`;
- exact local model identity `ollama/qwen3:4b`;
- Git, `flock`, Python 3, `curl`, and `uv`;
- one writer per physical Git worktree;
- repository Quality remains authoritative.

GPU acceleration is optional. CPU-only inference is acceptable for the
INFRA-0001 correctness contract; accelerator enablement is a workstation
optimization and must not weaken the verified provider or authority boundary.

## Fresh machine

Install Git, Python 3, OpenCode, and Ollama using the platform's trusted
installation path. The bootstrap intentionally does not silently install
OpenCode or Ollama because those tools may require platform-specific packages,
service authority, or administrator approval.

Then:

```bash
git clone https://github.com/magixhot/AI-Engineering.git
cd AI-Engineering
./scripts/bootstrap-local-agent.sh
./scripts/verify-local-agent.sh
```

The bootstrap:

1. requires Linux/WSL and a clean Git worktree;
2. records exact HEAD;
3. requires Git, `flock`, Python, and `curl`;
4. installs pinned user-space `uv 0.12.5` only when `uv` is absent;
5. requires OpenCode `>= 1.18.18`;
6. requires Ollama and establishes a loopback server when possible;
7. pulls exact model `qwen3:4b`;
8. syncs the locked development environment;
9. verifies repository provider and role configuration;
10. runs `verify-local-agent.sh` including a real OpenCode -> Ollama -> governed
    tool-calling smoke;
11. fails if HEAD or repository cleanliness changed.

Success ends with:

```text
LOCAL_AGENT_READY
LOCAL_AGENT_BOOTSTRAP_OK
```

## Verification matrix

Run at any time:

```bash
./scripts/verify-local-agent.sh
```

The verifier prints one `PASS` line per requirement and finishes with exactly:

```text
LOCAL_AGENT_READY
```

It validates command availability, compatible OpenCode, canonical
`opencode.json`, primary-selectable governed roles, the loopback Ollama API,
`qwen3:4b`, a clean worktree, a real `repo-reader` smoke that reports exact
HEAD, and unchanged/clean Git state after the smoke.

Any missing prerequisite or incomplete evidence is fail-closed.

## Existing workstation migration

For a workstation that already has OpenCode/Ollama:

```bash
cd /path/to/AI-Engineering
git fetch origin
git checkout master
git pull --ff-only
./scripts/bootstrap-local-agent.sh
```

Do not copy an old global OpenCode provider configuration into the repository.
The checked-in `opencode.json` is canonical. Remove or disable user-level
provider overrides if they cause the repository model identity or loopback URL
to resolve differently.

## Branch and worktree continuation

Read-only roles may share a clean worktree. The verifier must not run while a
writer owns that worktree's lock.

For implementation work, create or select the separately approved feature
branch/worktree first, record exact HEAD, confirm a clean worktree, then invoke:

```bash
bash scripts/local-opencode-run.sh implementer \
  --expected-head <EXACT_SHA> \
  --model ollama/qwen3:4b \
  -- "<approved bounded objective>"
```

The implementer may not run on `master`. Parallel writers require separate Git
worktrees and branches.

## Upgrades

Treat OpenCode, Ollama, model, provider URL, or role-permission changes as
runtime/configuration changes rather than invisible workstation drift.

After an upgrade:

```bash
./scripts/verify-local-agent.sh
```

Do not replace `qwen3:4b` with a floating `latest` model for milestone evidence.
A new required minimum OpenCode version or model identity must be committed and
pass the repository Quality gates before it becomes canonical.

## Troubleshooting

### Ollama API unavailable

Check:

```bash
curl http://127.0.0.1:11434/api/tags
ollama list
```

If a system service is installed, start it through the platform service manager.
Otherwise run Ollama bound to loopback. Do not expose the INFRA provider on a
non-loopback interface merely to make verification pass.

### Model missing

```bash
ollama pull qwen3:4b
```

### OpenCode role falls back to `build`

Verify the repository role files are present and contain `mode: primary`, then
rerun `./scripts/verify-local-agent.sh`. Do not broaden permissions or switch to
the built-in broad `build` agent as a workaround.

### Local model composes a denied shell command

Keep the deny-by-default policy. Narrow the task wording to an already allowed
command shape or return `BLOCKED`/`ESCALATE`. Do not allow generic shell
composition, semicolons, pipelines, or `&&` merely to satisfy a model attempt.

### GPU unavailable

GPU acceleration is not required. If `ollama ps` reports `100% CPU`, the local
agent remains valid if the canonical smoke and deterministic checks pass.

## Secrets and tokens

Do not store API keys, GitHub tokens, credentials, private environment files, or
machine-specific secrets in `opencode.json`, `.opencode/agents/`, bootstrap
scripts, evidence files, or Git history. Local agents are explicitly denied
secret environment files.

## Rollback / disablement

INFRA-0001 local execution is optional tooling around repository work. To
disable it on a workstation:

1. stop invoking `scripts/local-opencode-run.sh`, bootstrap, and verifier;
2. stop/disable the workstation Ollama service if it is not needed elsewhere;
3. optionally remove locally downloaded Ollama models and user-level OpenCode
   configuration outside the repository;
4. leave repository source, tests, Quality, AUTO, REL, branch protection, and
   Git history unchanged.

No history rewrite, protected-branch change, Quality relaxation, or repository
semantic migration is required for rollback.

After rollback, ordinary repository development and GitHub Quality continue to
operate independently of OpenCode/Ollama.
