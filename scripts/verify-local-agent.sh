#!/usr/bin/env bash
set -euo pipefail

MODEL="ollama/qwen3:4b"
MIN_OPENCODE_VERSION="1.18.18"

pass() {
  printf 'PASS  %s\n' "$1"
}

fail() {
  printf 'FAIL  %s\n' "$1" >&2
  exit 1
}

version_at_least() {
  local actual="$1"
  local minimum="$2"
  [[ "$(printf '%s\n%s\n' "$minimum" "$actual" | sort -V | head -n1)" == "$minimum" ]]
}

repo_root="$(git rev-parse --show-toplevel 2>/dev/null)" || fail "repository root"
cd "$repo_root"

[[ "$(uname -s)" == "Linux" ]] || fail "Linux/WSL runtime"
pass "Linux/WSL runtime"

for command in git flock python3 uv curl opencode ollama; do
  command -v "$command" >/dev/null 2>&1 || fail "command available: $command"
  pass "command available: $command"
done

opencode_version="$(opencode --version 2>/dev/null | grep -Eo '[0-9]+\.[0-9]+\.[0-9]+' | head -n1)"
[[ -n "$opencode_version" ]] || fail "OpenCode version readable"
version_at_least "$opencode_version" "$MIN_OPENCODE_VERSION" || \
  fail "OpenCode >= $MIN_OPENCODE_VERSION"
pass "OpenCode >= $MIN_OPENCODE_VERSION ($opencode_version)"

python3 - <<'PY' || fail "canonical opencode.json"
import json
from pathlib import Path

config = json.loads(Path("opencode.json").read_text(encoding="utf-8"))
provider = config["provider"]["ollama"]
assert provider["options"]["baseURL"] == "http://127.0.0.1:11434/v1"
assert "qwen3:4b" in provider["models"]
PY
pass "canonical opencode.json"

for role in repo-reader verifier implementer; do
  path=".opencode/agents/$role.md"
  [[ -f "$path" ]] || fail "agent present: $role"
  grep -q '^mode: primary$' "$path" || fail "agent primary-selectable: $role"
  pass "agent primary-selectable: $role"
done

[[ -x scripts/local-opencode-run.sh || -f scripts/local-opencode-run.sh ]] || \
  fail "governed launcher present"
pass "governed launcher present"

curl --fail --silent --max-time 3 http://127.0.0.1:11434/api/tags >/dev/null || \
  fail "Ollama loopback API"
pass "Ollama loopback API"

ollama list | awk 'NR > 1 {print $1}' | grep -Fxq 'qwen3:4b' || \
  fail "local model qwen3:4b"
pass "local model qwen3:4b"

head_before="$(git rev-parse HEAD)"
status_before="$(git --no-optional-locks status --porcelain=v1 --untracked-files=all)"
[[ -z "$status_before" ]] || fail "clean worktree before smoke"
pass "clean worktree before smoke ($head_before)"

smoke_output="$(
  bash scripts/local-opencode-run.sh repo-reader \
    --model "$MODEL" \
    -- \
    "Report current branch and exact HEAD only. Use exactly two separate allowed commands: 'git branch --show-current' and 'git rev-parse HEAD'. Do not combine commands, do not use semicolons, pipes, &&, or other shell composition."
)" || fail "OpenCode -> Ollama governed smoke"

printf '%s\n' "$smoke_output" | grep -Fq "$head_before" || \
  fail "smoke reports exact HEAD"
pass "OpenCode -> Ollama governed smoke"
pass "smoke reports exact HEAD"

head_after="$(git rev-parse HEAD)"
status_after="$(git --no-optional-locks status --porcelain=v1 --untracked-files=all)"
[[ "$head_after" == "$head_before" ]] || fail "HEAD unchanged after smoke"
[[ -z "$status_after" ]] || fail "clean worktree after smoke"
pass "HEAD unchanged after smoke"
pass "clean worktree after smoke"

printf 'LOCAL_AGENT_READY\n'
