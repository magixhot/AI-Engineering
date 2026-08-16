"""AUTO-0011 approval preparation and fresh-context binding."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .project_reconciliation import ProjectReconciliationPlan, ProjectReconciliationStep
from .project_reconciliation_approval import (
    ReconciliationApproval,
    build_reconciliation_approval,
)
from .project_reconciliation_approval_verification import ReconciliationApprovalContext


class ReconciliationApprovalContextError(RuntimeError):
    """Fresh approval context could not be assembled safely."""


def reconciliation_policy_fingerprint(policy_path: Path | None) -> str | None:
    """Bind approval to exact explicit policy bytes when policy mode is used."""

    if policy_path is None:
        return None
    try:
        raw = policy_path.resolve().read_bytes()
    except OSError as exc:
        raise ReconciliationApprovalContextError(
            "explicit policy could not be read for approval binding"
        ) from exc
    return "policy-sha256:" + hashlib.sha256(raw).hexdigest()


def reconciliation_project_id(plan: ProjectReconciliationPlan) -> str:
    """Return a portable identity digest without binding to checkout path."""

    identity = plan.health.identity
    if identity is None:
        raise ReconciliationApprovalContextError(
            "fresh plan did not provide supported project identity"
        )
    payload = {
        "baseline": identity.baseline,
        "distribution_name": identity.distribution_name,
        "evidence_sha256": list(identity.evidence_sha256),
        "package_name": identity.package_name,
        "profile": identity.profile,
        "project_version": identity.project_version,
    }
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "project-v1:" + hashlib.sha256(encoded).hexdigest()


def reconciliation_candidate_inputs(
    step: ProjectReconciliationStep,
) -> tuple[tuple[str, str], ...]:
    """Canonical authority-relevant representation of one selected candidate."""

    return tuple(
        sorted(
            (
                ("affected_paths", json.dumps(list(step.affected_paths))),
                ("migration_id", step.migration_id or ""),
                ("reason", step.reason),
                ("reinspect_after_step", str(step.reinspect_after_step).lower()),
                ("sequence", str(step.sequence)),
                ("state", step.state),
            )
        )
    )


def approval_context_for_plan(
    plan: ProjectReconciliationPlan,
    *,
    policy_path: Path | None = None,
) -> ReconciliationApprovalContext:
    """Assemble fresh read-only approval context for the current first step."""

    if plan.state != "ready" or not plan.steps:
        raise ReconciliationApprovalContextError(
            "approval requires one fresh ready reconciliation candidate"
        )
    readiness = plan.health.git_readiness
    if readiness is None or readiness.head is None:
        raise ReconciliationApprovalContextError(
            "fresh plan did not provide approval-relevant Git HEAD evidence"
        )
    step = plan.steps[0]
    return ReconciliationApprovalContext(
        project_id=reconciliation_project_id(plan),
        workflow=step.workflow,
        candidate_inputs=reconciliation_candidate_inputs(step),
        git_head=readiness.head,
        git_branch=readiness.branch,
        policy_fingerprint=reconciliation_policy_fingerprint(policy_path),
    )


def build_approval_for_plan(
    plan: ProjectReconciliationPlan,
    *,
    policy_path: Path | None = None,
) -> ReconciliationApproval:
    """Create one single-candidate approval from freshly planned context."""

    context = approval_context_for_plan(plan, policy_path=policy_path)
    return build_reconciliation_approval(
        project_id=context.project_id,
        workflow=context.workflow,
        candidate_inputs=context.candidate_inputs,
        git_head=context.git_head,
        git_branch=context.git_branch,
        policy_fingerprint=context.policy_fingerprint,
    )
