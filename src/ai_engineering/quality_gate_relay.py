"""Read-only exact Quality gate relay for AUTO-0016-01B."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .opencode_control_protocol import (
    ControlRequest,
    ControlResult,
    ControlResultState,
    ControlTaskClass,
)
from .opencode_readonly_adapter import SnapshotProvider, capture_repository_snapshot
from .quality_verification import build_verification_input
from .quality_verifier import verify_exact_post_merge_quality


def execute_quality_verify(
    repository_path: Path,
    request: ControlRequest,
    *,
    snapshot_provider: SnapshotProvider | None = None,
) -> ControlResult:
    """Verify one exact merged master SHA and return bounded typed evidence."""

    if request.task_class is not ControlTaskClass.QUALITY_VERIFY:
        raise ValueError("quality relay requires quality_verify task")
    if request.expected_head is None:
        raise ValueError("quality_verify requires expected_head")

    provider = snapshot_provider or (
        lambda: capture_repository_snapshot(repository_path)
    )
    before = provider()
    verification_input = build_verification_input(
        repository=request.repository,
        head_sha=request.expected_head,
    )
    verified = verify_exact_post_merge_quality(verification_input)
    after = provider()

    document: dict[str, object] = {
        "state": verified.state.value,
        "satisfies_gate": verified.satisfies_gate,
        "repository": verification_input.repository,
        "workflow_path": verification_input.workflow_path,
        "branch": verification_input.branch,
        "head_sha": verification_input.head_sha,
        "event": verification_input.event,
    }
    if verified.evidence is not None:
        document["evidence"] = asdict(verified.evidence)
    if verified.reason is not None:
        document["reason"] = verified.reason
    text = json.dumps(document, sort_keys=True, separators=(",", ":"))
    if len(text) > request.max_result_chars:
        raise ValueError("quality evidence exceeds request bound")

    state = (
        ControlResultState.SUCCEEDED
        if verified.satisfies_gate
        else ControlResultState.FAILED
    )
    return ControlResult(
        request_id=request.request_id,
        task_class=request.task_class,
        repository=request.repository,
        branch=after.branch,
        head=request.expected_head,
        pre_clean=before.is_clean,
        state=state,
        text=text,
        post_clean=after.is_clean,
        version=request.version,
    )
