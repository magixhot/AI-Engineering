"""Deterministic local-first routing for INFRA-0001.

This module makes routing decisions only. It never invokes OpenCode, an
external model, Codex, GitHub, or a repository mutation by itself.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Sequence


class Route(StrEnum):
    """Bounded execution route selected by the policy."""

    LOCAL = "LOCAL"
    EXTERNAL_EXPLICIT = "EXTERNAL_EXPLICIT"
    CODEX_ESCALATE = "CODEX_ESCALATE"
    BLOCKED = "BLOCKED"


class TaskClass(StrEnum):
    """Task classes relevant to the local-first policy."""

    INSPECTION = "inspection"
    MECHANICAL_EDIT = "mechanical_edit"
    BOUNDED_IMPLEMENTATION = "bounded_implementation"
    VERIFICATION = "verification"
    ARCHITECTURE = "architecture"
    AUTHORITY = "authority"
    SECURITY = "security"
    NONDETERMINISTIC_FAILURE = "nondeterministic_failure"


class LocalState(StrEnum):
    """Evidence from the local execution attempt, when one exists."""

    NOT_ATTEMPTED = "not_attempted"
    PASS = "pass"
    FAIL = "fail"
    BLOCKED = "blocked"
    ESCALATE = "escalate"


DIRECT_CODEX_CLASSES = frozenset(
    {
        TaskClass.ARCHITECTURE,
        TaskClass.AUTHORITY,
        TaskClass.SECURITY,
        TaskClass.NONDETERMINISTIC_FAILURE,
    }
)

WRITE_CLASSES = frozenset(
    {
        TaskClass.MECHANICAL_EDIT,
        TaskClass.BOUNDED_IMPLEMENTATION,
    }
)


@dataclass(frozen=True, slots=True)
class RoutingRequest:
    """Explicit evidence supplied to one routing decision."""

    task_class: TaskClass
    deterministic_verification: bool
    local_available: bool = True
    local_state: LocalState = LocalState.NOT_ATTEMPTED
    external_fallback_approved: bool = False
    external_model: str | None = None


@dataclass(frozen=True, slots=True)
class RoutingDecision:
    """Serializable policy result with bounded evidence."""

    route: Route
    reason: str
    local_first: bool
    external_execution_authorized: bool
    codex_execution_authorized: bool


def decide_route(request: RoutingRequest) -> RoutingDecision:
    """Return a deterministic route without executing any model.

    External execution is possible only when both an exact model identity and
    explicit approval are present. ``CODEX_ESCALATE`` is a handoff signal, not
    authority to invoke Codex automatically.
    """

    if request.task_class in DIRECT_CODEX_CLASSES:
        return RoutingDecision(
            route=Route.CODEX_ESCALATE,
            reason=(
                f"task class {request.task_class.value} requires stronger reasoning"
            ),
            local_first=False,
            external_execution_authorized=False,
            codex_execution_authorized=False,
        )

    if request.task_class in WRITE_CLASSES and not request.deterministic_verification:
        return RoutingDecision(
            route=Route.CODEX_ESCALATE,
            reason="write-capable task has no deterministic verification path",
            local_first=False,
            external_execution_authorized=False,
            codex_execution_authorized=False,
        )

    if request.local_state is LocalState.PASS:
        return RoutingDecision(
            route=Route.LOCAL,
            reason="local execution already produced PASS evidence",
            local_first=True,
            external_execution_authorized=False,
            codex_execution_authorized=False,
        )

    if request.local_state is LocalState.ESCALATE:
        return RoutingDecision(
            route=Route.CODEX_ESCALATE,
            reason="local agent explicitly returned ESCALATE",
            local_first=True,
            external_execution_authorized=False,
            codex_execution_authorized=False,
        )

    external_ready = (
        request.external_fallback_approved
        and request.external_model is not None
        and bool(request.external_model.strip())
    )

    if request.local_state in {LocalState.FAIL, LocalState.BLOCKED}:
        if external_ready:
            return RoutingDecision(
                route=Route.EXTERNAL_EXPLICIT,
                reason=(
                    "local attempt did not pass; explicit external fallback "
                    "is approved"
                ),
                local_first=True,
                external_execution_authorized=True,
                codex_execution_authorized=False,
            )
        return RoutingDecision(
            route=Route.BLOCKED,
            reason="local attempt did not pass and no explicit fallback is approved",
            local_first=True,
            external_execution_authorized=False,
            codex_execution_authorized=False,
        )

    if request.local_available:
        return RoutingDecision(
            route=Route.LOCAL,
            reason="bounded task is eligible for the available local runtime",
            local_first=True,
            external_execution_authorized=False,
            codex_execution_authorized=False,
        )

    if external_ready:
        return RoutingDecision(
            route=Route.EXTERNAL_EXPLICIT,
            reason="local runtime unavailable; explicit external fallback is approved",
            local_first=True,
            external_execution_authorized=True,
            codex_execution_authorized=False,
        )

    return RoutingDecision(
        route=Route.BLOCKED,
        reason="local runtime unavailable and no explicit fallback is approved",
        local_first=True,
        external_execution_authorized=False,
        codex_execution_authorized=False,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--task-class",
        choices=[member.value for member in TaskClass],
        required=True,
    )
    parser.add_argument(
        "--local-state",
        choices=[member.value for member in LocalState],
        default=LocalState.NOT_ATTEMPTED.value,
    )
    parser.add_argument("--deterministic-verification", action="store_true")
    parser.add_argument("--local-unavailable", action="store_true")
    parser.add_argument("--external-fallback-approved", action="store_true")
    parser.add_argument("--external-model")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Emit one stable JSON routing decision."""

    args = _parser().parse_args(argv)
    request = RoutingRequest(
        task_class=TaskClass(args.task_class),
        deterministic_verification=args.deterministic_verification,
        local_available=not args.local_unavailable,
        local_state=LocalState(args.local_state),
        external_fallback_approved=args.external_fallback_approved,
        external_model=args.external_model,
    )
    decision = decide_route(request)
    payload = {
        "request": {
            **asdict(request),
            "task_class": request.task_class.value,
            "local_state": request.local_state.value,
        },
        "decision": {
            **asdict(decision),
            "route": decision.route.value,
        },
    }
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
