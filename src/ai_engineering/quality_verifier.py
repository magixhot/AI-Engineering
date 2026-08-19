"""Exact post-merge Quality verification service and read-only CLI for AUTO-0015."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from typing import Sequence

from .quality_actions_transport import (
    GhActionsReadTransport,
    QualityActionsTransportError,
)
from .quality_verification import (
    QualityVerificationError,
    QualityVerificationInput,
    QualityVerificationResult,
    QualityVerificationState,
    WorkflowRunEvidence,
    build_verification_input,
    classify_exact_run,
)


def _pending(
    verification_input: QualityVerificationInput,
    reason: str,
) -> QualityVerificationResult:
    return QualityVerificationResult(
        QualityVerificationState.PENDING,
        verification_input,
        reason=reason,
    )


def _ambiguous(
    verification_input: QualityVerificationInput,
    reason: str,
) -> QualityVerificationResult:
    return QualityVerificationResult(
        QualityVerificationState.AMBIGUOUS,
        verification_input,
        reason=reason,
    )


def _unavailable(
    verification_input: QualityVerificationInput,
    reason: str,
) -> QualityVerificationResult:
    return QualityVerificationResult(
        QualityVerificationState.UNAVAILABLE,
        verification_input,
        reason=reason,
    )


def select_authoritative_run(
    verification_input: QualityVerificationInput,
    runs: Sequence[WorkflowRunEvidence],
) -> QualityVerificationResult:
    """Select one exact authoritative run, or fail closed.

    Multiple records for one GitHub workflow-run id are treated as attempts of the
    same run and the highest run_attempt is authoritative. Distinct run ids for the
    exact tuple are ambiguous and may not satisfy the gate.
    """

    if not runs:
        return _pending(verification_input, "exact Quality run is not available yet")

    grouped: dict[int, list[WorkflowRunEvidence]] = {}
    for run in runs:
        candidate = classify_exact_run(verification_input, run)
        if candidate.state is QualityVerificationState.INVALID:
            return candidate
        grouped.setdefault(run.run_id, []).append(run)

    if len(grouped) != 1:
        return _ambiguous(
            verification_input,
            "multiple distinct exact Quality workflow runs match the gate",
        )

    attempts = next(iter(grouped.values()))
    attempts_with_numbers = [run for run in attempts if run.run_attempt is not None]
    attempts_without_numbers = [run for run in attempts if run.run_attempt is None]

    if attempts_without_numbers and len(attempts) > 1:
        return _ambiguous(
            verification_input,
            "multiple attempts cannot be ordered without run_attempt evidence",
        )

    if not attempts_with_numbers:
        authoritative = attempts[0]
    else:
        by_attempt: dict[int, WorkflowRunEvidence] = {}
        for run in attempts_with_numbers:
            assert run.run_attempt is not None
            existing = by_attempt.get(run.run_attempt)
            if existing is not None and existing != run:
                return _ambiguous(
                    verification_input,
                    "conflicting evidence exists for one workflow run attempt",
                )
            by_attempt[run.run_attempt] = run
        authoritative = by_attempt[max(by_attempt)]

    return classify_exact_run(verification_input, authoritative)


def verify_exact_post_merge_quality(
    verification_input: QualityVerificationInput,
    *,
    transport: GhActionsReadTransport | None = None,
) -> QualityVerificationResult:
    """Read and classify the exact post-merge Quality gate without mutation."""

    reader = transport or GhActionsReadTransport()
    try:
        runs = reader.list_runs(verification_input)
    except QualityActionsTransportError:
        return _unavailable(
            verification_input,
            "authoritative GitHub Actions evidence is unavailable",
        )
    return select_authoritative_run(verification_input, runs)


def _result_document(result: QualityVerificationResult) -> dict[str, object]:
    document: dict[str, object] = {
        "state": result.state.value,
        "satisfies_gate": result.satisfies_gate,
        "repository": result.verification_input.repository,
        "workflow_path": result.verification_input.workflow_path,
        "branch": result.verification_input.branch,
        "head_sha": result.verification_input.head_sha,
        "event": result.verification_input.event,
    }
    if result.evidence is not None:
        document["evidence"] = asdict(result.evidence)
    if result.reason is not None:
        document["reason"] = result.reason
    return document


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify exact push-triggered Quality for a merged master SHA"
    )
    parser.add_argument("repository", help="GitHub repository in owner/name form")
    parser.add_argument("head_sha", help="exact lowercase 40-character master SHA")
    args = parser.parse_args(argv)

    try:
        verification_input = build_verification_input(
            repository=args.repository,
            head_sha=args.head_sha,
        )
    except QualityVerificationError as exc:
        print(
            json.dumps(
                {
                    "state": QualityVerificationState.INVALID.value,
                    "satisfies_gate": False,
                    "reason": str(exc),
                },
                sort_keys=True,
            )
        )
        return 2

    result = verify_exact_post_merge_quality(verification_input)
    print(json.dumps(_result_document(result), sort_keys=True))
    return 0 if result.satisfies_gate else 1


if __name__ == "__main__":
    raise SystemExit(main())
