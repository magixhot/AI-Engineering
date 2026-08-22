from pathlib import Path


AGENT_FILES = (
    Path(".opencode/agents/repo-reader.md"),
    Path(".opencode/agents/verifier.md"),
    Path(".opencode/agents/implementer.md"),
)


def test_cli_roles_are_primary_agents() -> None:
    for path in AGENT_FILES:
        content = path.read_text(encoding="utf-8")
        frontmatter = content.split("---", 2)[1]
        assert "mode: primary" in frontmatter
        assert "mode: subagent" not in frontmatter
