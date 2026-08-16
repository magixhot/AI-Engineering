"""Read-only engineering project health/readiness aggregation for AUTO-0006."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .documentation_ownership import (
    DocumentationOwnershipError,
    plan_documentation_ownership_initialization,
)
from .documentation_sync import (
    DocumentationSyncError,
    detect_documentation_drift,
    plan_documentation_sync,
)
from .project_inspection import (
    ProjectInspectionError,
    ProjectInspectionRequest,
    ProjectStateSnapshot,
    inspect_project_state,
)
from .project_migration import (
    DEFAULT_MIGRATION_REGISTRY,
    PYTHON_ENGINEERING_V1_BASELINE,
    PYTHON_ENGINEERING_V1_TO_V2_MIGRATION,
    ProjectIdentity,
    ProjectMigrationError,
    ProjectMigrationRequest,
    detect_project_identity,
    plan_project_migration,
)

HealthState = Literal["healthy", "action_required", "manual_review", "unsupported"]
IssueState = Literal["action_required", "manual_review", "unsupported"]

NEXT_NONE = "none"
NEXT_MANUAL_REVIEW = "manual_review"
NEXT_MIGRATION_PLAN = (
    "project migrate plan --migration python-engineering-v1-to-v2"
)
NEXT_OWNERSHIP_PLAN = "project docs ownership plan"
NEXT_DOCS_PLAN = "project docs plan"


@dataclass(frozen=True)
class ProjectHealthIssue:
    """One stable machine-readable health/readiness issue."""

    code: str
    state: IssueState
    detail: str
    path: str | None = None
    workflow: str | None = None


@dataclass(frozen=True)
class ProjectHealthReport:
    """Immutable AUTO-0006 read-only project health report."""

    project_root: Path
    inspection: ProjectStateSnapshot | None
    identity: ProjectIdentity | None
    git_state: str
    documentation_ownership_state: str
    documentation_sync_state: str
    migration_state: str
    overall_state: HealthState
    next_action: str
    issues: tuple[ProjectHealthIssue, ...]


_STATE_RANK: dict[HealthState, int] = {
    "healthy": 0,
    "action_required": 1,
    "manual_review": 2,
    "unsupported": 3,
}


def _issue_sort_key(issue: ProjectHealthIssue) -> tuple[int, str, str, str]:
    return (
        -_STATE_RANK[issue.state],
        issue.code,
        issue.path or "",
        issue.workflow or "",
    )


def _sorted_issues(issues: list[ProjectHealthIssue]) -> tuple[ProjectHealthIssue, ...]:
    return tuple(sorted(issues, key=_issue_sort_key))


def _overall(issues: tuple[ProjectHealthIssue, ...]) -> HealthState:
    if not issues:
        return "healthy"
    return max((issue.state for issue in issues), key=lambda item: _STATE_RANK[item])


def _unsupported_report(project_root: Path, detail: str) -> ProjectHealthReport:
    try:
        root = project_root.resolve()
    except OSError:
        root = project_root.absolute()
    issue = ProjectHealthIssue(
        code="PROJECT_UNSUPPORTED",
        state="unsupported",
        detail=detail,
    )
    return ProjectHealthReport(
        project_root=root,
        inspection=None,
        identity=None,
        git_state="unknown",
        documentation_ownership_state="blocked",
        documentation_sync_state="blocked",
        migration_state="unavailable",
        overall_state="unsupported",
        next_action=NEXT_MANUAL_REVIEW,
        issues=(issue,),
    )


def _git_state(snapshot: ProjectStateSnapshot) -> str:
    if not snapshot.git_repository:
        return "not_repository"
    if snapshot.git_head is None:
        return "repository_without_head"
    if snapshot.git_branch is None:
        return "detached_or_unborn"
    return "ready"


def _ownership_readiness(
    snapshot: ProjectStateSnapshot,
    issues: list[ProjectHealthIssue],
) -> tuple[str, bool]:
    plan = plan_documentation_ownership_initialization(snapshot)
    if plan.manual_review:
        for classification in plan.classifications:
            if classification.document not in plan.manual_review:
                continue
            issues.append(
                ProjectHealthIssue(
                    code=f"DOC_OWNERSHIP_{classification.state.upper()}",
                    state="manual_review",
                    detail=classification.reason,
                    path=classification.document,
                    workflow=NEXT_MANUAL_REVIEW,
                )
            )
        return "manual_review", False
    if plan.updates:
        for update in plan.updates:
            issues.append(
                ProjectHealthIssue(
                    code="DOC_OWNERSHIP_INITIALIZATION_AVAILABLE",
                    state="action_required",
                    detail="approved ownership markers can be initialized safely",
                    path=update.document,
                    workflow=NEXT_OWNERSHIP_PLAN,
                )
            )
        return "initialization_available", False
    return "initialized", True


def _sync_readiness(
    snapshot: ProjectStateSnapshot,
    issues: list[ProjectHealthIssue],
) -> str:
    report = detect_documentation_drift(snapshot)
    manual_review = tuple(
        item for item in report.items if item.category == "manual_review_required"
    )
    if manual_review:
        for item in manual_review:
            issues.append(
                ProjectHealthIssue(
                    code="DOC_SYNC_MANUAL_REVIEW",
                    state="manual_review",
                    detail=item.observed,
                    path=item.document,
                    workflow=NEXT_MANUAL_REVIEW,
                )
            )
        return "manual_review"

    plan = plan_documentation_sync(report)
    if plan.updates:
        update_documents = {item.document for item in plan.updates}
        for document in sorted(update_documents):
            issues.append(
                ProjectHealthIssue(
                    code="DOC_SYNC_DRIFT",
                    state="action_required",
                    detail="managed documentation has deterministic drift",
                    path=document,
                    workflow=NEXT_DOCS_PLAN,
                )
            )
        return "drift"
    return "clean"


def _migration_readiness(
    identity: ProjectIdentity,
    issues: list[ProjectHealthIssue],
) -> str:
    if identity.baseline != PYTHON_ENGINEERING_V1_BASELINE:
        return "already_target"

    plan = plan_project_migration(
        ProjectMigrationRequest(
            identity.project_root,
            PYTHON_ENGINEERING_V1_TO_V2_MIGRATION,
        ),
        DEFAULT_MIGRATION_REGISTRY,
    )
    if plan.manual_review:
        for blocker in plan.manual_review:
            path = blocker.split(":", 1)[0]
            issues.append(
                ProjectHealthIssue(
                    code="MIGRATION_MANUAL_REVIEW",
                    state="manual_review",
                    detail=blocker,
                    path=path,
                    workflow=NEXT_MANUAL_REVIEW,
                )
            )
        return "manual_review"
    if plan.operations:
        issues.append(
            ProjectHealthIssue(
                code="MIGRATION_AVAILABLE",
                state="action_required",
                detail="registered python-engineering V1 to V2 migration is ready",
                workflow=NEXT_MIGRATION_PLAN,
            )
        )
        return "ready"
    return "already_target"


def _recommended_action(
    identity: ProjectIdentity,
    overall: HealthState,
    issues: tuple[ProjectHealthIssue, ...],
) -> str:
    if overall in {"unsupported", "manual_review"}:
        return NEXT_MANUAL_REVIEW
    if overall == "healthy":
        return NEXT_NONE
    if identity.baseline == PYTHON_ENGINEERING_V1_BASELINE and any(
        issue.code == "MIGRATION_AVAILABLE" for issue in issues
    ):
        return NEXT_MIGRATION_PLAN
    if any(
        issue.code == "DOC_OWNERSHIP_INITIALIZATION_AVAILABLE" for issue in issues
    ):
        return NEXT_OWNERSHIP_PLAN
    if any(issue.code == "DOC_SYNC_DRIFT" for issue in issues):
        return NEXT_DOCS_PLAN
    return NEXT_MANUAL_REVIEW


def audit_project_health(project_root: Path) -> ProjectHealthReport:
    """Return deterministic read-only health/readiness for one project root."""

    try:
        snapshot = inspect_project_state(ProjectInspectionRequest(project_root))
    except ProjectInspectionError as exc:
        return _unsupported_report(project_root, str(exc))

    try:
        identity = detect_project_identity(snapshot.project_root)
    except ProjectMigrationError as exc:
        issue = ProjectHealthIssue(
            code="IDENTITY_UNSUPPORTED",
            state="unsupported",
            detail=str(exc),
        )
        return ProjectHealthReport(
            project_root=snapshot.project_root,
            inspection=snapshot,
            identity=None,
            git_state=_git_state(snapshot),
            documentation_ownership_state="blocked",
            documentation_sync_state="blocked",
            migration_state="unavailable",
            overall_state="unsupported",
            next_action=NEXT_MANUAL_REVIEW,
            issues=(issue,),
        )

    issues: list[ProjectHealthIssue] = []
    migration_state = "not_required"
    docs_ownership_state = "not_evaluated"
    docs_sync_state = "not_evaluated"

    try:
        migration_state = _migration_readiness(identity, issues)
        docs_ownership_state, ownership_initialized = _ownership_readiness(
            snapshot, issues
        )
        if ownership_initialized:
            docs_sync_state = _sync_readiness(snapshot, issues)
        else:
            docs_sync_state = "blocked"
    except (DocumentationOwnershipError, DocumentationSyncError) as exc:
        issues.append(
            ProjectHealthIssue(
                code="DOCUMENTATION_MANUAL_REVIEW",
                state="manual_review",
                detail=str(exc),
                workflow=NEXT_MANUAL_REVIEW,
            )
        )
        docs_ownership_state = "manual_review"
        docs_sync_state = "manual_review"
    except ProjectMigrationError as exc:
        issues.append(
            ProjectHealthIssue(
                code="MIGRATION_MANUAL_REVIEW",
                state="manual_review",
                detail=str(exc),
                workflow=NEXT_MANUAL_REVIEW,
            )
        )
        migration_state = "manual_review"

    ordered = _sorted_issues(issues)
    overall = _overall(ordered)
    next_action = _recommended_action(identity, overall, ordered)
    return ProjectHealthReport(
        project_root=snapshot.project_root,
        inspection=snapshot,
        identity=identity,
        git_state=_git_state(snapshot),
        documentation_ownership_state=docs_ownership_state,
        documentation_sync_state=docs_sync_state,
        migration_state=migration_state,
        overall_state=overall,
        next_action=next_action,
        issues=ordered,
    )
