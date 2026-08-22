from pathlib import Path


BOOTSTRAP = Path("scripts/bootstrap-local-agent.sh")
VERIFY = Path("scripts/verify-local-agent.sh")
SETUP_DOC = Path("docs/LOCAL_AGENT_WORKSTATION_SETUP.md")


def test_workstation_artifacts_exist() -> None:
    for path in (BOOTSTRAP, VERIFY, SETUP_DOC):
        assert path.is_file()


def test_bootstrap_preserves_governance_contract() -> None:
    content = BOOTSTRAP.read_text(encoding="utf-8")
    required = (
        "qwen3:4b",
        "127.0.0.1:11434",
        "OpenCode",
        "uv sync --locked --group dev",
        "bash scripts/verify-local-agent.sh",
        "LOCAL_AGENT_BOOTSTRAP_OK",
        "git rev-parse HEAD",
        "status --porcelain=v1",
    )
    for token in required:
        assert token in content

    forbidden = (
        "git reset --hard",
        "git push",
        "git merge",
        "git clean -f",
        "HSA_OVERRIDE_GFX_VERSION",
    )
    for token in forbidden:
        assert token not in content


def test_verifier_requires_real_governed_smoke() -> None:
    content = VERIFY.read_text(encoding="utf-8")
    required = (
        "ollama/qwen3:4b",
        "opencode --version",
        "http://127.0.0.1:11434/api/tags",
        "local-opencode-run.sh repo-reader",
        "git branch --show-current",
        "git rev-parse HEAD",
        "mode: primary",
        "LOCAL_AGENT_READY",
    )
    for token in required:
        assert token in content


def test_setup_doc_contains_fresh_machine_and_rollback_paths() -> None:
    content = SETUP_DOC.read_text(encoding="utf-8")
    required = (
        "git clone https://github.com/magixhot/AI-Engineering.git",
        "./scripts/bootstrap-local-agent.sh",
        "./scripts/verify-local-agent.sh",
        "Existing workstation migration",
        "Branch and worktree continuation",
        "Upgrades",
        "Troubleshooting",
        "Secrets and tokens",
        "Rollback / disablement",
        "GPU acceleration is not required",
    )
    for token in required:
        assert token in content
