from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tarfile
import venv
import zipfile
from email import message_from_bytes
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
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

    wheel_path = next(distribution_directory.glob("ai_engineering-0.1.0-*.whl"))
    sdist_path = distribution_directory / "ai_engineering-0.1.0.tar.gz"
    assert sdist_path.is_file()

    with zipfile.ZipFile(wheel_path) as wheel:
        wheel_names = wheel.namelist()
        _assert_no_forbidden_paths(wheel_names)
        assert "ai_engineering/__init__.py" in wheel_names
        assert "ai_engineering/cli.py" in wheel_names
        assert "ai_engineering-0.1.0.dist-info/METADATA" in wheel_names
        assert "ai_engineering-0.1.0.dist-info/entry_points.txt" in wheel_names
        assert not any(name.startswith(("tests/", "docs/")) for name in wheel_names)

        metadata = message_from_bytes(
            wheel.read("ai_engineering-0.1.0.dist-info/METADATA")
        )
        assert metadata["Name"] == "ai-engineering"
        assert metadata["Version"] == "0.1.0"
        assert metadata["Requires-Python"] == ">=3.11"
        assert any(
            requirement.startswith("mcp")
            and ">=1.27" in requirement
            and "<1.28" in requirement
            for requirement in metadata.get_all("Requires-Dist", [])
        )
        assert (
            "ai-engineering = ai_engineering.cli:main"
            in wheel.read("ai_engineering-0.1.0.dist-info/entry_points.txt").decode()
        )

    with tarfile.open(sdist_path) as sdist:
        sdist_names = sdist.getnames()
        _assert_no_forbidden_paths(sdist_names)
        root = "ai_engineering-0.1.0/"
        assert f"{root}pyproject.toml" in sdist_names
        assert f"{root}README.md" in sdist_names
        assert f"{root}LICENSE" in sdist_names
        assert any(
            name.startswith(f"{root}src/ai_engineering/") for name in sdist_names
        )
        assert any(name.startswith(f"{root}tests/") for name in sdist_names)
        assert any(name.startswith(f"{root}docs/") for name in sdist_names)

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
    assert installed_metadata["version"] == "0.1.0"
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
