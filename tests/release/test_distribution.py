from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tarfile
import tomllib
import venv
import zipfile
from email import message_from_bytes
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROJECT_VERSION = tomllib.loads(
    (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
)["project"]["version"]
DIST_INFO_ROOT = f"ai_engineering-{PROJECT_VERSION}.dist-info"
SDIST_ROOT = f"ai_engineering-{PROJECT_VERSION}/"
FORBIDDEN_ARTIFACT_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    "build",
    "dist",
}


def _subprocess_environment() -> dict[str, str]:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment.pop("PYTHONHOME", None)
    environment.update(
        {
            "GIT_AUTHOR_NAME": "AI-Engineering Release Tests",
            "GIT_AUTHOR_EMAIL": "release-tests@example.invalid",
            "GIT_COMMITTER_NAME": "AI-Engineering Release Tests",
            "GIT_COMMITTER_EMAIL": "release-tests@example.invalid",
            "PIP_DISABLE_PIP_VERSION_CHECK": "1",
        }
    )
    return environment


def _run(
    command: list[str],
    *,
    cwd: Path,
    environment: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )


def _run_unchecked(
    command: list[str],
    *,
    cwd: Path,
    environment: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )


def _assert_no_forbidden_paths(names: list[str]) -> None:
    for name in names:
        path = Path(name)
        assert not FORBIDDEN_ARTIFACT_PARTS.intersection(path.parts)
        assert "uv.lock" not in path.parts
        assert not path.is_absolute()
        assert ":" not in path.drive


def _venv_executable(venv_directory: Path, name: str) -> Path:
    scripts = venv_directory / ("Scripts" if os.name == "nt" else "bin")
    suffix = ".exe" if os.name == "nt" and name == "ai-engineering" else ""
    return scripts / f"{name}{suffix}"


def _append_managed_section(path: Path, marker: str, body: str) -> None:
    original = path.read_text(encoding="utf-8")
    path.write_text(
        original
        + f"\n<!-- ai-engineering:auto0002:{marker}:start -->"
        + body
        + f"<!-- ai-engineering:auto0002:{marker}:end -->\n",
        encoding="utf-8",
    )


def test_distribution_artifacts_and_isolated_wheel_install(tmp_path: Path) -> None:
    environment = _subprocess_environment()
    source_tree = tmp_path / "clean-source"
    distribution_directory = tmp_path / "artifacts"
    isolated_working_directory = tmp_path / "isolated-working-directory"
    shutil.copytree(
        PROJECT_ROOT,
        source_tree,
        ignore=shutil.ignore_patterns(
            ".git",
            ".mypy_cache",
            ".pytest_cache",
            ".ruff_cache",
            ".venv",
            "__pycache__",
            "*.egg-info",
            "build",
            "dist",
        ),
    )
    distribution_directory.mkdir()
    isolated_working_directory.mkdir()

    _run(
        [sys.executable, "-m", "build", "--outdir", str(distribution_directory)],
        cwd=source_tree,
        environment=environment,
    )

    wheel_path = next(
        distribution_directory.glob(f"ai_engineering-{PROJECT_VERSION}-*.whl")
    )
    sdist_path = distribution_directory / f"ai_engineering-{PROJECT_VERSION}.tar.gz"
    assert sdist_path.is_file()

    with zipfile.ZipFile(wheel_path) as wheel:
        wheel_names = wheel.namelist()
        _assert_no_forbidden_paths(wheel_names)
        assert "ai_engineering/__init__.py" in wheel_names
        assert "ai_engineering/cli.py" in wheel_names
        assert f"{DIST_INFO_ROOT}/METADATA" in wheel_names
        assert f"{DIST_INFO_ROOT}/entry_points.txt" in wheel_names
        assert not any(name.startswith(("tests/", "docs/")) for name in wheel_names)

        metadata = message_from_bytes(wheel.read(f"{DIST_INFO_ROOT}/METADATA"))
        assert metadata["Name"] == "ai-engineering"
        assert metadata["Version"] == PROJECT_VERSION
        assert metadata["Requires-Python"] == ">=3.11"
        assert any(
            requirement.startswith("mcp")
            and ">=1.27" in requirement
            and "<1.28" in requirement
            for requirement in metadata.get_all("Requires-Dist", [])
        )
        assert (
            "ai-engineering = ai_engineering.cli:main"
            in wheel.read(f"{DIST_INFO_ROOT}/entry_points.txt").decode()
        )

    with tarfile.open(sdist_path) as sdist:
        sdist_names = sdist.getnames()
        _assert_no_forbidden_paths(sdist_names)
        assert f"{SDIST_ROOT}pyproject.toml" in sdist_names
        assert f"{SDIST_ROOT}README.md" in sdist_names
        assert f"{SDIST_ROOT}LICENSE" in sdist_names
        assert any(
            name.startswith(f"{SDIST_ROOT}src/ai_engineering/") for name in sdist_names
        )
        assert any(name.startswith(f"{SDIST_ROOT}tests/") for name in sdist_names)
        assert any(name.startswith(f"{SDIST_ROOT}docs/") for name in sdist_names)

    venv_directory = tmp_path / "isolated-venv"
    venv.create(venv_directory, with_pip=True)
    venv_python = _venv_executable(venv_directory, "python")
    _run(
        [str(venv_python), "-m", "pip", "install", str(wheel_path)],
        cwd=isolated_working_directory,
        environment=environment,
    )

    metadata_check = (
        "import importlib.metadata as metadata; import json; import ai_engineering; "
        "entry = next(item for item in metadata.entry_points(group='console_scripts') "
        "if item.name == 'ai-engineering'); "
        "distribution = metadata.metadata('ai-engineering'); "
        "print(json.dumps({"
        "'module_path': ai_engineering.__file__, "
        "'name': distribution['Name'], "
        "'version': distribution['Version'], "
        "'requires_python': distribution['Requires-Python'], "
        "'requires_dist': distribution.get_all('Requires-Dist'), "
        "'entry_point': entry.value}))"
    )
    installed = _run(
        [str(venv_python), "-c", metadata_check],
        cwd=isolated_working_directory,
        environment=environment,
    )
    installed_metadata = json.loads(installed.stdout)
    installed_path = Path(installed_metadata["module_path"]).resolve()
    assert installed_path.is_relative_to(venv_directory.resolve())
    assert installed_metadata["name"] == "ai-engineering"
    assert installed_metadata["version"] == PROJECT_VERSION
    assert installed_metadata["requires_python"] == ">=3.11"
    assert any(
        requirement.startswith("mcp")
        and ">=1.27" in requirement
        and "<1.28" in requirement
        for requirement in installed_metadata["requires_dist"]
    )
    assert installed_metadata["entry_point"] == "ai_engineering.cli:main"

    installed_cli = _venv_executable(venv_directory, "ai-engineering")
    help_result = _run(
        [str(installed_cli), "--help"],
        cwd=isolated_working_directory,
        environment=environment,
    )
    assert "project" in help_result.stdout
    project_help = _run(
        [str(installed_cli), "project", "--help"],
        cwd=isolated_working_directory,
        environment=environment,
    )
    assert "create" in project_help.stdout
    assert "bootstrap" in project_help.stdout
    assert "docs" in project_help.stdout
    docs_help = _run(
        [str(installed_cli), "project", "docs", "--help"],
        cwd=isolated_working_directory,
        environment=environment,
    )
    assert "check" in docs_help.stdout
    assert "plan" in docs_help.stdout
    assert "apply" in docs_help.stdout

    generated_project = tmp_path / "installed-artifact-project"
    _run(
        [
            str(installed_cli),
            "project",
            "create",
            "--name",
            "Installed Artifact Project",
            "--destination",
            str(generated_project),
            "--description",
            "A project generated by the installed distribution artifact.",
        ],
        cwd=isolated_working_directory,
        environment=environment,
    )
    assert generated_project.is_dir()
    assert (generated_project / ".git").is_dir()
    assert _run(
        ["git", "branch", "--show-current"],
        cwd=generated_project,
        environment=environment,
    ).stdout.strip() == "main"
    assert _run(
        ["git", "log", "-1", "--format=%s"],
        cwd=generated_project,
        environment=environment,
    ).stdout.strip()

    bootstrapped_project = tmp_path / "installed-bootstrap-project"
    bootstrap_result = _run(
        [
            str(installed_cli),
            "project",
            "bootstrap",
            "--name",
            "Installed Bootstrap Project",
            "--destination",
            str(bootstrapped_project),
            "--description",
            "An engineering project bootstrapped by the installed wheel.",
        ],
        cwd=isolated_working_directory,
        environment=environment,
    )
    bootstrap_output = bootstrap_result.stdout.splitlines()
    assert f"bootstrapped_project={bootstrapped_project.resolve()}" in bootstrap_output
    assert "project_name=Installed Bootstrap Project" in bootstrap_output
    assert "profile=python-engineering" in bootstrap_output
    assert "package_name=installed_bootstrap_project" in bootstrap_output
    assert "git_branch=main" in bootstrap_output
    assert "initial_commit=created" in bootstrap_output
    assert "verification=passed" in bootstrap_output
    assert (bootstrapped_project / ".git").is_dir()
    assert (bootstrapped_project / "pyproject.toml").is_file()
    assert (
        bootstrapped_project
        / "src"
        / "installed_bootstrap_project"
        / "__init__.py"
    ).is_file()
    assert (bootstrapped_project / "tests" / "test_smoke.py").is_file()
    assert _run(
        ["git", "branch", "--show-current"],
        cwd=bootstrapped_project,
        environment=environment,
    ).stdout.strip() == "main"
    assert _run(
        ["git", "log", "-1", "--format=%s"],
        cwd=bootstrapped_project,
        environment=environment,
    ).stdout.strip()

    unmarked_check = _run_unchecked(
        [
            str(installed_cli),
            "project",
            "docs",
            "check",
            "--project",
            str(bootstrapped_project),
        ],
        cwd=isolated_working_directory,
        environment=environment,
    )
    assert unmarked_check.returncode == 1
    assert "manual_review_count=3" in unmarked_check.stdout
    assert "status=drift" in unmarked_check.stdout
    assert unmarked_check.stderr == ""

    _append_managed_section(
        bootstrapped_project / "CURRENT_STATUS.md",
        "current-status",
        "\n- stale: value\n",
    )
    _append_managed_section(
        bootstrapped_project / "PROJECT_MAP.md",
        "project-map",
        "\n- `gone.txt` (file)\n",
    )
    _append_managed_section(
        bootstrapped_project / "MASTER_INDEX.md",
        "master-index",
        "\n- `OLD.md` — observed\n",
    )
    _run(
        ["git", "add", "CURRENT_STATUS.md", "PROJECT_MAP.md", "MASTER_INDEX.md"],
        cwd=bootstrapped_project,
        environment=environment,
    )
    _run(
        ["git", "commit", "-m", "add AUTO-0002 ownership markers"],
        cwd=bootstrapped_project,
        environment=environment,
    )
    sync_head = _run(
        ["git", "rev-parse", "HEAD"],
        cwd=bootstrapped_project,
        environment=environment,
    ).stdout.strip()

    plan_result = _run(
        [
            str(installed_cli),
            "project",
            "docs",
            "plan",
            "--project",
            str(bootstrapped_project),
        ],
        cwd=isolated_working_directory,
        environment=environment,
    )
    assert "update_count=3" in plan_result.stdout
    assert "manual_review_count=0" in plan_result.stdout
    assert plan_result.stdout.count("update=") == 3
    assert "status=ready" in plan_result.stdout

    apply_result = _run(
        [
            str(installed_cli),
            "project",
            "docs",
            "apply",
            "--project",
            str(bootstrapped_project),
        ],
        cwd=isolated_working_directory,
        environment=environment,
    )
    assert "changed_count=3" in apply_result.stdout
    assert "verification=passed" in apply_result.stdout
    assert apply_result.stdout.count("changed_document=") == 3
    assert _run(
        ["git", "rev-parse", "HEAD"],
        cwd=bootstrapped_project,
        environment=environment,
    ).stdout.strip() == sync_head
    assert _run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=bootstrapped_project,
        environment=environment,
    ).stdout == ""

    clean_check = _run(
        [
            str(installed_cli),
            "project",
            "docs",
            "check",
            "--project",
            str(bootstrapped_project),
        ],
        cwd=isolated_working_directory,
        environment=environment,
    )
    assert "drift_count=0" in clean_check.stdout
    assert "manual_review_count=0" in clean_check.stdout
    assert "status=clean" in clean_check.stdout
