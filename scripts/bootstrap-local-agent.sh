#!/usr/bin/env bash
set -euo pipefail

MODEL="qwen3:4b"
MIN_OPENCODE_VERSION="1.18.18"
UV_VERSION="0.12.5"

info() {
  printf 'INFO  %s\n' "$1"
}

fail() {
  printf 'BLOCKED  %s\n' "$1" >&2
  exit 1
}

repo_root="$(git rev-parse --show-toplevel 2>/dev/null)" || fail "run inside AI-Engineering clone"
cd "$repo_root"

[[ "$(uname -s)" == "Linux" ]] || fail "bootstrap supports Linux/WSL only"

for command in git flock python3 curl; do
  command -v "$command" >/dev/null 2>&1 || fail "missing required command: $command"
done

status_before="$(git --no-optional-locks status --porcelain=v1 --untracked-files=all)"
[[ -z "$status_before" ]] || fail "bootstrap requires a clean worktree"
head_before="$(git rev-parse HEAD)"
info "exact HEAD $head_before"

if ! command -v uv >/dev/null 2>&1; then
  info "installing uv $UV_VERSION in user space"
  curl -LsSf "https://astral.sh/uv/$UV_VERSION/install.sh" | sh
  export PATH="$HOME/.local/bin:$PATH"
fi
command -v uv >/dev/null 2>&1 || fail "uv unavailable after bootstrap"

if ! command -v opencode >/dev/null 2>&1; then
  fail "OpenCode is not installed; install a compatible OpenCode >= $MIN_OPENCODE_VERSION, then rerun"
fi

opencode_version="$(opencode --version 2>/dev/null | grep -Eo '[0-9]+\.[0-9]+\.[0-9]+' | head -n1)"
[[ -n "$opencode_version" ]] || fail "cannot read OpenCode version"
if [[ "$(printf '%s\n%s\n' "$MIN_OPENCODE_VERSION" "$opencode_version" | sort -V | head -n1)" != "$MIN_OPENCODE_VERSION" ]]; then
  fail "OpenCode $opencode_version is older than required $MIN_OPENCODE_VERSION"
fi
info "OpenCode $opencode_version"

if ! command -v ollama >/dev/null 2>&1; then
  fail "Ollama is not installed; install Ollama for Linux/WSL, then rerun"
fi

if ! curl --fail --silent --max-time 3 http://127.0.0.1:11434/api/tags >/dev/null; then
  if command -v systemctl >/dev/null 2>&1 && systemctl is-enabled ollama >/dev/null 2>&1; then
    info "starting Ollama system service"
    sudo systemctl start ollama
  else
    info "starting user Ollama server on loopback"
    nohup env OLLAMA_HOST=127.0.0.1:11434 ollama serve \
      >"${TMPDIR:-/tmp}/ai-engineering-ollama.log" 2>&1 &
  fi
  for _ in $(seq 1 20); do
    curl --fail --silent --max-time 1 http://127.0.0.1:11434/api/tags >/dev/null && break
    sleep 1
  done
fi
curl --fail --silent --max-time 3 http://127.0.0.1:11434/api/tags >/dev/null || \
  fail "Ollama loopback API is unavailable at 127.0.0.1:11434"

info "ensuring local model $MODEL"
ollama pull "$MODEL"

info "syncing locked development environment"
uv sync --locked --group dev

python3 - <<'PY' || exit 1
import json
from pathlib import Path

config = json.loads(Path("opencode.json").read_text(encoding="utf-8"))
provider = config["provider"]["ollama"]
assert provider["options"]["baseURL"] == "http://127.0.0.1:11434/v1"
assert "qwen3:4b" in provider["models"]
PY

for role in repo-reader verifier implementer; do
  path=".opencode/agents/$role.md"
  [[ -f "$path" ]] || fail "missing governed agent: $role"
  grep -q '^mode: primary$' "$path" || fail "agent is not primary-selectable: $role"
done

bash scripts/verify-local-agent.sh

head_after="$(git rev-parse HEAD)"
status_after="$(git --no-optional-locks status --porcelain=v1 --untracked-files=all)"
[[ "$head_after" == "$head_before" ]] || fail "bootstrap changed Git HEAD"
[[ -z "$status_after" ]] || fail "bootstrap changed repository state"

printf 'LOCAL_AGENT_BOOTSTRAP_OK\n'
