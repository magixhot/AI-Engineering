"""Public receipt-mode execution for AUTO-0012 reconciliation runs."""

from __future__ import annotations

from pathlib import Path

from .project_reconciliation import ProjectReconciliationPlan, plan_project_reconciliation
from .project_reconciliation_approval import (
    ReconciliationApproval,
    parse_reconciliation_approval,
)
from .project_reconciliation_approval_context import (
    ReconciliationApprovalContextError,
    approval_context_for_plan,
    reconciliation_policy_fingerprint,
    reconciliation_project_id,
)
from .project_reconciliation_approval_verification import (
    verify_reconciliation_approval,
)
from .project_reconciliation_orchestration import (
    DEFAULT_MAX_STEPS,
    ProjectReconciliationOrchestrationResult,
    run_project_reconciliation,
)
from .project_reconciliation_receipt import (
    serialize_reconciliation_execution_receipt,
)
from .project_reconciliation_receipt_projection import (
    ObservedApprovalVerification,
    ReconciliationReceiptProjectionContext,
    project_reconciliation_execution_receipt,
)


def _load_valid_approval(path: Path | None) -> ReconciliationApproval | None:
    if path is None:
        return None
    try:
        raw = path.resolve().read_bytes()
    except OSError:
        return None
    loaded = parse_reconciliation_approval(raw)
    return loaded.approval if loaded.state == "loaded" else None


def _approval_observation(
    approval: ReconciliationApproval,
    plan: ProjectReconciliationPlan,
    *,
    policy_path: Path | None,
) -> ObservedApprovalVerification | None:
    if plan.state != "ready" or not plan.steps:
        return None
    try:
        context = approval_context_for_plan(plan, policy_path=policy_path)
    except ReconciliationApprovalContextError:
        return None
    return ObservedApprovalVerification(
        workflow=plan.steps[0].workflow,
        verification=verify_reconciliation_approval(approval, context),
    )


def _receipt_context(
    initial_plan: ProjectReconciliationPlan,
    result: ProjectReconciliationOrchestrationResult,
    *,
    max_steps: int,
    policy_path: Path | None,
    approval_path: Path | None,
) -> ReconciliationReceiptProjectionContext:
    readiness = initial_plan.health.git_readiness
    if readiness is None or readiness.head is None:
        raise ReconciliationApprovalContextError(
            "fresh plan did not provide receipt-relevant Git HEAD evidence"
        )

    approval = _load_valid_approval(approval_path)
    observations: list[ObservedApprovalVerification] = []
    if approval is not None:
        first = _approval_observation(
            approval,
            initial_plan,
            policy_path=policy_path,
        )
        if first is not None:
            observations.append(first)

        if result.state == "approval_refused":
            terminal = _approval_observation(
                approval,
                result.final_plan,
                policy_path=policy_path,
            )
            if terminal is not None and terminal not in observations:
                observations.append(terminal)

    return ReconciliationReceiptProjectionContext(
        project_id=reconciliation_project_id(initial_plan),
        requested_max_steps=max_steps,
        initial_state=initial_plan.state,
        git_head=readiness.head,
        git_branch=readiness.branch,
        policy_fingerprint=reconciliation_policy_fingerprint(policy_path),
        approval_digest=approval.digest if approval is not None else None,
        approval_scope=approval.scope if approval is not None else None,
        approval_verifications=tuple(observations),
    )


def run_reconciliation_orchestration_receipt(
    project_root: Path,
    *,
    max_steps: int = DEFAULT_MAX_STEPS,
    policy_path: Path | None = None,
    approval_path: Path | None = None,
) -> int:
    """Run existing orchestration and emit one canonical execution receipt JSON."""

    root = project_root.resolve()
    initial_plan = plan_project_reconciliation(root)
    result = run_project_reconciliation(
        root,
        max_steps=max_steps,
        policy_path=policy_path,
        approval_path=approval_path,
    )
    try:
        context = _receipt_context(
            initial_plan,
            result,
            max_steps=max_steps,
            policy_path=policy_path,
            approval_path=approval_path,
        )
    except ReconciliationApprovalContextError as exc:
        print(f"error: receipt evidence unavailable: {exc}")
        return 1

    receipt = project_reconciliation_execution_receipt(result, context)
    print(serialize_reconciliation_execution_receipt(receipt).decode("utf-8"), end="")
    return 0 if result.state in {"complete", "no_change"} else 1
