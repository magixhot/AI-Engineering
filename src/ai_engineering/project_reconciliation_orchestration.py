"""Bounded reconciliation orchestration with policy and approval gates."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .project_reconciliation import (
    ProjectReconciliationPlan,
    plan_project_reconciliation,
)
from .project_reconciliation_apply import (
    ProjectReconciliationApplyResult,
    apply_project_reconciliation_step,
)
from .project_reconciliation_approval import (
    ReconciliationApproval,
    ReconciliationApprovalLoadResult,
    parse_reconciliation_approval,
)
from .project_reconciliation_approval_context import (
    ReconciliationApprovalContextError,
    approval_context_for_plan,
)
from .project_reconciliation_approval_verification import (
    verify_reconciliation_approval,
)
from .project_reconciliation_policy import (
    ReconciliationPolicyDecision,
    evaluate_reconciliation_policy,
    load_reconciliation_policy,
)

OrchestrationState = Literal[
    "complete",
    "no_change",
    "stopped",
    "failed",
    "limit_reached",
    "policy_refused",
    "policy_error",
    "approval_refused",
    "approval_error",
]

DEFAULT_MAX_STEPS = 8
MAX_MAX_STEPS = 100


@dataclass(frozen=True)
class ProjectReconciliationOrchestrationIssue:
    """Stable bounded evidence for an orchestration terminal condition."""

    code: str
    detail: str


@dataclass(frozen=True)
class ProjectReconciliationOrchestrationResult:
    """Immutable result of one bounded reconciliation orchestration run."""

    project_root: Path
    state: OrchestrationState
    successful_steps: int
    attempts: tuple[ProjectReconciliationApplyResult, ...]
    policy_decisions: tuple[ReconciliationPolicyDecision, ...]
    final_plan: ProjectReconciliationPlan
    issues: tuple[ProjectReconciliationOrchestrationIssue, ...]


def _issue(
    code: str,
    detail: str,
) -> tuple[ProjectReconciliationOrchestrationIssue, ...]:
    return (ProjectReconciliationOrchestrationIssue(code=code, detail=detail),)


def _policy_issues(
    decision: ReconciliationPolicyDecision,
) -> tuple[ProjectReconciliationOrchestrationIssue, ...]:
    return tuple(
        ProjectReconciliationOrchestrationIssue(code=item.code, detail=item.detail)
        for item in decision.issues
    )


def _approval_load_issues(
    loaded: ReconciliationApprovalLoadResult,
) -> tuple[ProjectReconciliationOrchestrationIssue, ...]:
    return tuple(
        ProjectReconciliationOrchestrationIssue(code=item.code, detail=item.detail)
        for item in loaded.issues
    )


def _result(
    project_root: Path,
    state: OrchestrationState,
    successful_steps: int,
    attempts: list[ProjectReconciliationApplyResult],
    policy_decisions: list[ReconciliationPolicyDecision],
    final_plan: ProjectReconciliationPlan,
    *,
    issues: tuple[ProjectReconciliationOrchestrationIssue, ...] = (),
) -> ProjectReconciliationOrchestrationResult:
    return ProjectReconciliationOrchestrationResult(
        project_root=project_root.resolve(),
        state=state,
        successful_steps=successful_steps,
        attempts=tuple(attempts),
        policy_decisions=tuple(policy_decisions),
        final_plan=final_plan,
        issues=issues,
    )


def _validate_max_steps(max_steps: int) -> None:
    if max_steps < 1:
        raise ValueError("max_steps must be at least 1")
    if max_steps > MAX_MAX_STEPS:
        raise ValueError(f"max_steps must not exceed {MAX_MAX_STEPS}")


def _load_approval(path: Path) -> ReconciliationApprovalLoadResult:
    try:
        raw = path.resolve().read_bytes()
    except OSError:
        return ReconciliationApprovalLoadResult(
            state="approval_error",
            approval=None,
            issues=(),
        )
    return parse_reconciliation_approval(raw)


def run_project_reconciliation(
    project_root: Path,
    *,
    max_steps: int = DEFAULT_MAX_STEPS,
    policy_path: Path | None = None,
    approval_path: Path | None = None,
) -> ProjectReconciliationOrchestrationResult:
    """Run freshly planned guarded steps with optional restrictive gates."""

    _validate_max_steps(max_steps)
    root = project_root.resolve()
    explicit_policy = policy_path.resolve() if policy_path is not None else None
    explicit_approval = approval_path.resolve() if approval_path is not None else None
    approval: ReconciliationApproval | None = None
    approval_load_error: ReconciliationApprovalLoadResult | None = None
    if explicit_approval is not None:
        loaded_approval = _load_approval(explicit_approval)
        if loaded_approval.state != "loaded" or loaded_approval.approval is None:
            approval_load_error = loaded_approval
        else:
            approval = loaded_approval.approval

    attempts: list[ProjectReconciliationApplyResult] = []
    policy_decisions: list[ReconciliationPolicyDecision] = []
    successful_steps = 0

    while True:
        plan = plan_project_reconciliation(root)

        if plan.state == "clean":
            terminal: OrchestrationState = "complete" if attempts else "no_change"
            return _result(
                root,
                terminal,
                successful_steps,
                attempts,
                policy_decisions,
                plan,
            )

        if plan.state == "unsupported":
            return _result(
                root,
                "stopped",
                successful_steps,
                attempts,
                policy_decisions,
                plan,
                issues=_issue(
                    "PLAN_UNSUPPORTED",
                    "fresh reconciliation plan is unsupported",
                ),
            )

        if plan.state == "manual_review":
            return _result(
                root,
                "stopped",
                successful_steps,
                attempts,
                policy_decisions,
                plan,
                issues=_issue(
                    "PLAN_MANUAL_REVIEW",
                    "fresh reconciliation plan requires manual review",
                ),
            )

        if not plan.steps:
            return _result(
                root,
                "stopped",
                successful_steps,
                attempts,
                policy_decisions,
                plan,
                issues=_issue(
                    "READY_PLAN_WITHOUT_STEP",
                    "ready reconciliation plan has no executable step",
                ),
            )

        step = plan.steps[0]
        effective_max_steps = max_steps
        if explicit_policy is not None:
            readiness = plan.health.git_readiness
            if readiness is None:
                return _result(
                    root,
                    "policy_error",
                    successful_steps,
                    attempts,
                    policy_decisions,
                    plan,
                    issues=_issue(
                        "POLICY_GIT_EVIDENCE_UNAVAILABLE",
                        "fresh plan did not provide policy-relevant Git evidence",
                    ),
                )

            loaded = load_reconciliation_policy(explicit_policy)
            decision = evaluate_reconciliation_policy(
                loaded,
                workflow=step.workflow,
                git_readiness=readiness,
                project_root=plan.project_root,
                expected_project_root=root,
                requested_max_steps=max_steps,
            )
            policy_decisions.append(decision)
            if decision.state == "policy_error":
                return _result(
                    root,
                    "policy_error",
                    successful_steps,
                    attempts,
                    policy_decisions,
                    plan,
                    issues=_policy_issues(decision),
                )
            if decision.state == "policy_refused":
                return _result(
                    root,
                    "policy_refused",
                    successful_steps,
                    attempts,
                    policy_decisions,
                    plan,
                    issues=_policy_issues(decision),
                )
            if decision.effective_max_steps is not None:
                effective_max_steps = decision.effective_max_steps

        if explicit_approval is not None:
            if approval_load_error is not None or approval is None:
                issues = (
                    _approval_load_issues(approval_load_error)
                    if approval_load_error is not None and approval_load_error.issues
                    else _issue(
                        "APPROVAL_READ_ERROR",
                        "approval artifact could not be loaded",
                    )
                )
                return _result(
                    root,
                    "approval_error",
                    successful_steps,
                    attempts,
                    policy_decisions,
                    plan,
                    issues=issues,
                )
            try:
                context = approval_context_for_plan(
                    plan,
                    policy_path=explicit_policy,
                )
            except ReconciliationApprovalContextError as exc:
                return _result(
                    root,
                    "approval_error",
                    successful_steps,
                    attempts,
                    policy_decisions,
                    plan,
                    issues=_issue("APPROVAL_CONTEXT_ERROR", str(exc)),
                )
            verification = verify_reconciliation_approval(approval, context)
            if verification.state != "approved":
                return _result(
                    root,
                    "approval_refused",
                    successful_steps,
                    attempts,
                    policy_decisions,
                    plan,
                    issues=tuple(
                        ProjectReconciliationOrchestrationIssue(
                            code=item.code,
                            detail=item.detail,
                        )
                        for item in verification.mismatches
                    ),
                )

        if successful_steps >= effective_max_steps:
            return _result(
                root,
                "limit_reached",
                successful_steps,
                attempts,
                policy_decisions,
                plan,
                issues=_issue(
                    "PROGRESS_LIMIT_REACHED",
                    "eligible work remains after the configured progress limit",
                ),
            )

        result = apply_project_reconciliation_step(plan, step.sequence)
        attempts.append(result)

        if result.state == "applied":
            successful_steps += 1
            continue

        if result.state == "no_change":
            fresh = plan_project_reconciliation(root)
            if fresh.state == "clean":
                return _result(
                    root,
                    "complete",
                    successful_steps,
                    attempts,
                    policy_decisions,
                    fresh,
                )
            return _result(
                root,
                "stopped",
                successful_steps,
                attempts,
                policy_decisions,
                fresh,
                issues=_issue(
                    "NO_PROGRESS",
                    "delegated step made no change while executable work remains",
                ),
            )

        fresh = plan_project_reconciliation(root)
        if result.state == "failed":
            return _result(
                root,
                "failed",
                successful_steps,
                attempts,
                policy_decisions,
                fresh,
                issues=_issue(
                    "DELEGATED_STEP_FAILED",
                    "AUTO-0008 delegated execution failed",
                ),
            )

        return _result(
            root,
            "stopped",
            successful_steps,
            attempts,
            policy_decisions,
            fresh,
            issues=_issue(
                "DELEGATED_STEP_REFUSED",
                f"AUTO-0008 stopped with state {result.state}",
            ),
        )
