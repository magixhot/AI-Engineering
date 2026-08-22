#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
usage:
  bash scripts/local-opencode-run.sh repo-reader [--model PROVIDER/MODEL] -- OBJECTIVE...
  bash scripts/local-opencode-run.sh verifier [--model PROVIDER/MODEL] -- OBJECTIVE...
  bash scripts/local-opencode-run.sh implementer --expected-head SHA [--model PROVIDER/MODEL] -- OBJECTIVE...
EOF
  exit 2
}

git_fingerprint() {
  {
    printf 'branch\0%s\0' "$(git branch --show-current)"
    printf 'head\0%s\0' "$(git rev-parse HEAD)"
    printf 'status\0'
    git --no-optional-locks status --porcelain=v1 --untracked-files=all -z
    printf '\0worktree-diff\0'
    git diff --binary
    printf '\0index-diff\0'
    git diff --cached --binary
  } | sha256sum | awk '{print $1}'
}

role="${1:-}"
[[ -n "$role" ]] || usage
shift

case "$role" in
  repo-reader|verifier|implementer) ;;
  *) usage ;;
esac

model="ollama/qwen3:4b"
expected_head=""

while (($#)); do
  case "$1" in
    --model)
      (($# >= 2)) || usage
      model="$2"
      shift 2
      ;;
    --expected-head)
      (($# >= 2)) || usage
      expected_head="$2"
      shift 2
      ;;
    --)
      shift
      break
      ;;
    *) usage ;;
  esac
done

(($#)) || usage
objective="$*"

repo_root="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "BLOCKED: not inside a Git repository" >&2
  exit 3
}
cd "$repo_root"

branch="$(git branch --show-current)"
head="$(git rev-parse HEAD)"
status="$(git --no-optional-locks status --porcelain=v1 --untracked-files=all)"

if [[ -z "$branch" ]]; then
  echo "BLOCKED: detached HEAD is not allowed" >&2
  exit 3
fi

runtime_root="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
if [[ ! -d "$runtime_root" || ! -w "$runtime_root" ]]; then
  echo "BLOCKED: user runtime directory is unavailable" >&2
  exit 3
fi

worktree_key="$(printf '%s' "$repo_root" | sha256sum | awk '{print $1}')"
lock_path="$runtime_root/ai-engineering-local-agent-${worktree_key}.lock"

if [[ "$role" == "implementer" ]]; then
  [[ -n "$expected_head" ]] || {
    echo "BLOCKED: implementer requires --expected-head" >&2
    exit 3
  }
  if [[ "$branch" == "master" ]]; then
    echo "BLOCKED: implementer may not run on master" >&2
    exit 3
  fi
  if [[ "$head" != "$expected_head" ]]; then
    echo "BLOCKED: expected HEAD does not match workspace" >&2
    exit 3
  fi
  if [[ -n "$status" ]]; then
    echo "BLOCKED: implementer requires a clean worktree" >&2
    exit 3
  fi

  exec 9>"$lock_path"
  if ! flock -n 9; then
    echo "BLOCKED: another writer owns this worktree" >&2
    exit 3
  fi

  before="$head"
  opencode run --agent implementer --model "$model" "$objective"
  after="$(git rev-parse HEAD)"
  if [[ "$after" != "$before" ]]; then
    echo "FAIL: implementer changed Git HEAD" >&2
    exit 4
  fi
  exit 0
fi

before_fingerprint="$(git_fingerprint)"

if [[ "$role" == "verifier" ]]; then
  exec 9>"$lock_path"
  if ! flock -n 9; then
    echo "BLOCKED: writer is active in this worktree" >&2
    exit 3
  fi
fi

opencode run --agent "$role" --model "$model" "$objective"

after_fingerprint="$(git_fingerprint)"
if [[ "$after_fingerprint" != "$before_fingerprint" ]]; then
  echo "FAIL: read-only agent changed repository state" >&2
  exit 4
fi
