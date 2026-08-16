"""Typed deterministic reconciliation policy parsing and evaluation for AUTO-0010."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .project_git_readiness import ProjectGitReadiness
from .project_health import NEXT_DOCS_PLAN, NEXT_MIGRATION_PLAN, NEXT_OWNERSHIP_PLAN

PolicyLoadState = Literal["loaded", "policy_error"]
PolicyDecisionState = Literal["allowed", "policy_refused", "policy_error"]

_POLICY_VERSION = 1
_MAX_POLICY_STEPS = 100
_KNOWN_WORKFLOWS = frozenset(
    {
        NEXT_DOCS_PLAN,
        NEXT_OWNERSHIP_PLAN,
        NEXT_MIGRATION_PLAN,
    }
)
_ALLOWED_FIELDS = frozenset(
    {
        "version",
        "max_steps",
        "allow_dirty_worktree",
        "allow_untracked_files",
        "require_attached_branch",
        "require_project_root_match",
        "allowed_workflows",
        "denied_workflows",
    }
)


@dataclass(frozen=True)
class ReconciliationPolicyIssue:
    """Stable machine-readable policy evidence."""

    code: str
    detail: str


@dataclass(frozen=True)
class ReconciliationPolicy:
    """Validated AUTO-0010 policy that can only restrict existing authority."""

    version: int
    max_steps: int | None
    allow_dirty_worktree: bool
    allow_untracked_files: bool
    require_attached_branch: bool
    require_project_root_match: bool
    allowed_workflows: tuple[str, ...]
    denied_workflows: tuple[str, ...]


@dataclass(frozen=True)
class ReconciliationPolicyLoadResult:
    """Result of bounded local TOML policy loading."""

    source: Path
    state: PolicyLoadState
    policy: ReconciliationPolicy | None
    issues: tuple[ReconciliationPolicyIssue, ...]


@dataclass(frozen=True)
class ReconciliationPolicyDecision:
    """Deterministic allow/refuse/error decision for one existing candidate step."""

    source: Path
    state: PolicyDecisionState
    workflow: str
    effective_max_steps: int | None
    issues: tuple[ReconciliationPolicyIssue, ...]
    git_branch: str | None
    staged_paths: tuple[str, ...]
    unstaged_paths: tuple[str, ...]
    untracked_paths: tuple[str, ...]


def _issue(code: str, detail: str) -> ReconciliationPolicyIssue:
    return ReconciliationPolicyIssue(code=code, detail=detail)


def _error(
    source: Path,
    *issues: ReconciliationPolicyIssue,
) -> ReconciliationPolicyLoadResult:
    return ReconciliationPolicyLoadResult(
        source=source,
        state="policy_error",
        policy=None,
        issues=tuple(sorted(issues, key=lambda item: (item.code, item.detail))),
    )


def _bool_field(data: dict[str, object], name: str, default: bool) -> bool | None:
    value = data.get(name, default)
    return value if isinstance(value, bool) else None


def _workflow_field(
    data: dict[str, object],
    name: str,
) -> tuple[tuple[str, ...] | None, tuple[ReconciliationPolicyIssue, ...]]:
    value = data.get(name, [])
    if not isinstance(value, list) or any(
        not isinstance(item, str) for item in value
    ):
        return None, (
            _issue(
                "POLICY_FIELD_TYPE",
                f"{name} must be an array of strings",
            ),
        )
    workflows = tuple(sorted(set(value)))
    unknown = tuple(item for item in workflows if item not in _KNOWN_WORKFLOWS)
    if unknown:
        return None, tuple(
            _issue("POLICY_UNKNOWN_WORKFLOW", f"unknown workflow: {item}")
            for item in unknown
        )
    return workflows, ()


def _parse_policy(source: Path, data: object) -> ReconciliationPolicyLoadResult:
    if not isinstance(data, dict):
        return _error(
            source,
            _issue(
                "POLICY_ROOT_TYPE",
                "policy root must be a TOML table",
            ),
        )

    unknown_fields = sorted(set(data) - _ALLOWED_FIELDS)
    if unknown_fields:
        return _error(
            source,
            *(
                _issue("POLICY_UNKNOWN_FIELD", f"unknown policy field: {field}")
                for field in unknown_fields
            ),
        )

    version = data.get("version")
    if type(version) is not int or version != _POLICY_VERSION:
        return _error(
            source,
            _issue("POLICY_VERSION_UNSUPPORTED", "policy version must be integer 1"),
        )

    max_steps_value = data.get("max_steps")
    max_steps: int | None
    if max_steps_value is None:
        max_steps = None
    elif (
        type(max_steps_value) is not int
        or not 1 <= max_steps_value <= _MAX_POLICY_STEPS
    ):
        return _error(
            source,
            _issue(
                "POLICY_MAX_STEPS_INVALID",
                "max_steps must be an integer from 1 to 100",
            ),
        )
    else:
        max_steps = max_steps_value

    boolean_values = {
        "allow_dirty_worktree": _bool_field(data, "allow_dirty_worktree", True),
        "allow_untracked_files": _bool_field(data, "allow_untracked_files", True),
        "require_attached_branch": _bool_field(data, "require_attached_branch", False),
        "require_project_root_match": _bool_field(
            data, "require_project_root_match", False
        ),
    }
    invalid_boolean_fields = sorted(
        name for name, value in boolean_values.items() if value is None
    )
    if invalid_boolean_fields:
        return _error(
            source,
            *(
                _issue("POLICY_FIELD_TYPE", f"{name} must be boolean")
                for name in invalid_boolean_fields
            ),
        )

    allowed, allowed_issues = _workflow_field(data, "allowed_workflows")
    denied, denied_issues = _workflow_field(data, "denied_workflows")
    if allowed_issues or denied_issues or allowed is None or denied is None:
        return _error(source, *(allowed_issues + denied_issues))

    contradictions = sorted(set(allowed) & set(denied))
    if contradictions:
        return _error(
            source,
            *(
                _issue(
                    "POLICY_CONTRADICTORY_WORKFLOW",
                    f"workflow is both allowed and denied: {workflow}",
                )
                for workflow in contradictions
            ),
        )

    return ReconciliationPolicyLoadResult(
        source=source,
        state="loaded",
        policy=ReconciliationPolicy(
            version=version,
            max_steps=max_steps,
            allow_dirty_worktree=bool(boolean_values["allow_dirty_worktree"]),
            allow_untracked_files=bool(boolean_values["allow_untracked_files"]),
            require_attached_branch=bool(boolean_values["require_attached_branch"]),
            require_project_root_match=bool(
                boolean_values["require_project_root_match"]
            ),
            allowed_workflows=allowed,
            denied_workflows=denied,
        ),
        issues=(),
    )


def load_reconciliation_policy(policy_path: Path) -> ReconciliationPolicyLoadResult:
    """Load one explicit local TOML policy without discovery or fallback."""

    try:
        source = policy_path.resolve(strict=True)
    except OSError:
        source = policy_path.absolute()
        return _error(source, _issue("POLICY_UNREADABLE", "policy file is unreadable"))
    if not source.is_file():
        return _error(source, _issue("POLICY_UNREADABLE", "policy path is not a file"))
    try:
        raw = source.read_bytes()
        data = tomllib.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError):
        return _error(
            source,
            _issue("POLICY_PARSE_ERROR", "policy TOML could not be parsed"),
        )
    return _parse_policy(source, data)


def _effective_limit(
    policy_limit: int | None,
    requested_limit: int | None,
) -> int | None:
    if policy_limit is None:
        return requested_limit
    if requested_limit is None:
        return policy_limit
    return min(policy_limit, requested_limit)


def evaluate_reconciliation_policy(
    loaded: ReconciliationPolicyLoadResult,
    *,
    workflow: str,
    git_readiness: ProjectGitReadiness,
    project_root: Path,
    expected_project_root: Path | None = None,
    requested_max_steps: int | None = None,
) -> ReconciliationPolicyDecision:
    """Evaluate one fresh candidate; allowance never grants execution authority."""

    if loaded.state != "loaded" or loaded.policy is None:
        return ReconciliationPolicyDecision(
            source=loaded.source,
            state="policy_error",
            workflow=workflow,
            effective_max_steps=requested_max_steps,
            issues=loaded.issues,
            git_branch=git_readiness.branch,
            staged_paths=git_readiness.staged_paths,
            unstaged_paths=git_readiness.unstaged_paths,
            untracked_paths=git_readiness.untracked_paths,
        )

    policy = loaded.policy
    effective_limit = _effective_limit(policy.max_steps, requested_max_steps)
    errors: list[ReconciliationPolicyIssue] = []
    refusals: list[ReconciliationPolicyIssue] = []

    if workflow not in _KNOWN_WORKFLOWS:
        errors.append(
            _issue(
                "POLICY_UNKNOWN_CANDIDATE",
                f"unknown candidate workflow: {workflow}",
            )
        )
    if policy.allowed_workflows and workflow not in policy.allowed_workflows:
        refusals.append(
            _issue(
                "POLICY_WORKFLOW_NOT_ALLOWED",
                "candidate workflow is outside the allow-list",
            )
        )
    if workflow in policy.denied_workflows:
        refusals.append(
            _issue("POLICY_WORKFLOW_DENIED", "candidate workflow is denied")
        )

    tracked_dirty = bool(git_readiness.staged_paths or git_readiness.unstaged_paths)
    if tracked_dirty and not policy.allow_dirty_worktree:
        refusals.append(
            _issue(
                "POLICY_DIRTY_WORKTREE",
                "tracked Git changes are not allowed",
            )
        )
    if git_readiness.untracked_paths and not policy.allow_untracked_files:
        refusals.append(
            _issue(
                "POLICY_UNTRACKED_FILES",
                "untracked files are not allowed",
            )
        )
    if policy.require_attached_branch and git_readiness.branch is None:
        refusals.append(
            _issue(
                "POLICY_DETACHED_BRANCH",
                "an attached Git branch is required",
            )
        )

    if policy.require_project_root_match:
        if expected_project_root is None:
            errors.append(
                _issue(
                    "POLICY_PROJECT_ROOT_UNAVAILABLE",
                    "expected project root is required for root-match policy",
                )
            )
        elif project_root.resolve() != expected_project_root.resolve():
            refusals.append(
                _issue(
                    "POLICY_PROJECT_ROOT_MISMATCH",
                    "project root does not match the explicitly supplied root",
                )
            )

    if requested_max_steps is not None and requested_max_steps < 1:
        errors.append(
            _issue(
                "POLICY_REQUEST_LIMIT_INVALID",
                "requested max steps must be positive",
            )
        )

    issues = tuple(
        sorted(errors + refusals, key=lambda item: (item.code, item.detail))
    )
    state: PolicyDecisionState
    if errors:
        state = "policy_error"
    elif refusals:
        state = "policy_refused"
    else:
        state = "allowed"

    return ReconciliationPolicyDecision(
        source=loaded.source,
        state=state,
        workflow=workflow,
        effective_max_steps=effective_limit,
        issues=issues,
        git_branch=git_readiness.branch,
        staged_paths=git_readiness.staged_paths,
        unstaged_paths=git_readiness.unstaged_paths,
        untracked_paths=git_readiness.untracked_paths,
    )
