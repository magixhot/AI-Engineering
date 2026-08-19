"""Read-only GitHub Actions transport for AUTO-0015 exact Quality evidence."""

from __future__ import annotations

import json
import subprocess
from collections.abc import Callable, Mapping
from typing import Any
from urllib.parse import urlencode

from .quality_verification import (
    EXPECTED_WORKFLOW_PATH,
    QualityVerificationError,
    QualityVerificationInput,
    WorkflowRunEvidence,
    parse_workflow_run_evidence,
    validate_verification_input,
)

_GH_TIMEOUT_SECONDS = 30
_PAGE_SIZE = 100
_WORKFLOW_FILE = "quality.yml"


class QualityActionsTransportError(RuntimeError):
    """Raised when authoritative GitHub Actions evidence cannot be read safely."""


CommandRunner = Callable[[tuple[str, ...]], str]


def _run_gh(command: tuple[str, ...]) -> str:
    try:
        completed = subprocess.run(
            command,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            check=True,
            timeout=_GH_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise QualityActionsTransportError("GitHub Actions read timed out") from exc
    except subprocess.CalledProcessError as exc:
        raise QualityActionsTransportError("GitHub Actions read failed") from exc
    except FileNotFoundError as exc:
        raise QualityActionsTransportError("gh executable not found") from exc
    return completed.stdout


def _workflow_endpoint(value: QualityVerificationInput) -> str:
    validate_verification_input(value)
    if value.workflow_path != EXPECTED_WORKFLOW_PATH:
        raise QualityActionsTransportError("unsupported workflow path")
    query = urlencode(
        {
            "branch": value.branch,
            "event": value.event,
            "head_sha": value.head_sha,
            "per_page": _PAGE_SIZE,
        }
    )
    return (
        f"repos/{value.repository}/actions/workflows/{_WORKFLOW_FILE}/runs?{query}"
    )


class GhActionsReadTransport:
    """Enumerate exact workflow-run evidence through authenticated `gh api`."""

    def __init__(self, *, runner: CommandRunner = _run_gh) -> None:
        self._runner = runner

    def list_runs(
        self, verification_input: QualityVerificationInput
    ) -> list[WorkflowRunEvidence]:
        """Return all paginated workflow runs for the exact supported query."""

        try:
            endpoint = _workflow_endpoint(verification_input)
        except QualityVerificationError as exc:
            raise QualityActionsTransportError("invalid verification input") from exc

        raw = self._runner(("gh", "api", "--paginate", "--slurp", endpoint))
        try:
            pages = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise QualityActionsTransportError(
                "GitHub Actions returned malformed JSON"
            ) from exc
        if not isinstance(pages, list):
            raise QualityActionsTransportError(
                "GitHub Actions paginated response is not a list"
            )

        evidence: list[WorkflowRunEvidence] = []
        for page in pages:
            evidence.extend(self._parse_page(page))
        return evidence

    @staticmethod
    def _parse_page(page: Any) -> list[WorkflowRunEvidence]:
        if not isinstance(page, Mapping):
            raise QualityActionsTransportError(
                "GitHub Actions page is not an object"
            )
        runs = page.get("workflow_runs")
        if not isinstance(runs, list):
            raise QualityActionsTransportError(
                "GitHub Actions page has no workflow_runs list"
            )

        parsed: list[WorkflowRunEvidence] = []
        for run in runs:
            if not isinstance(run, Mapping):
                raise QualityActionsTransportError(
                    "GitHub Actions workflow run is not an object"
                )
            try:
                parsed.append(parse_workflow_run_evidence(run))
            except QualityVerificationError as exc:
                raise QualityActionsTransportError(
                    "GitHub Actions workflow run violates evidence schema"
                ) from exc
        return parsed
