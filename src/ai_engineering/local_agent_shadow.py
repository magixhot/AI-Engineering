"""Representative shadow validation evidence for INFRA-0001.

The module validates workstation observations. It does not invoke OpenCode,
Ollama, Codex, GitHub, or repository mutation by itself.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence

from .local_agent_routing import Route, RoutingRequest, TaskClass, decide_route

LOCAL_MODEL = "ollama/qwen3:4b"


@dataclass(frozen=True, slots=True)
class ShadowCase:
    """One representative task and its expected governed route."""

    case_id: str
    task_class: TaskClass
    role: str
    objective: str
    deterministic_verification: bool
    expected_route: Route


@dataclass(frozen=True, slots=True)
class ShadowObservation:
    """Evidence collected from one workstation shadow run."""

    case_id: str
    model: str
    role: str
    terminal_state: str
    repository_clean_before: bool
    repository_clean_after: bool
    head_unchanged: bool
    deterministic_check_passed: bool


CASES = (
    ShadowCase(
        case_id="inspect-head",
        task_class=TaskClass.INSPECTION,
        role="repo-reader",
        objective="Report current branch and exact HEAD only.",
        deterministic_verification=True,
        expected_route=Route.LOCAL,
    ),
    ShadowCase(
        case_id="inspect-agent-contract",
        task_class=TaskClass.INSPECTION,
        role="repo-reader",
        objective="Read AGENTS.md and report the four terminal outcomes.",
        deterministic_verification=True,
        expected_route=Route.LOCAL,
    ),
    ShadowCase(
        case_id="verify-routing-tests",
        task_class=TaskClass.VERIFICATION,
        role="verifier",
        objective="Run the bounded local-agent routing test file and report evidence.",
        deterministic_verification=True,
        expected_route=Route.LOCAL,
    ),
)


def case_map() -> dict[str, ShadowCase]:
    return {case.case_id: case for case in CASES}


def expected_routes() -> dict[str, Route]:
    """Derive representative routes through the production routing policy."""

    routes: dict[str, Route] = {}
    for case in CASES:
        decision = decide_route(
            RoutingRequest(
                task_class=case.task_class,
                deterministic_verification=case.deterministic_verification,
            )
        )
        routes[case.case_id] = decision.route
    return routes


def validate_observations(
    observations: Sequence[ShadowObservation],
) -> tuple[bool, tuple[str, ...]]:
    """Validate exact, complete workstation evidence fail-closed."""

    cases = case_map()
    observed: dict[str, ShadowObservation] = {}
    issues: list[str] = []

    for observation in observations:
        if observation.case_id not in cases:
            issues.append(f"unknown case: {observation.case_id}")
            continue
        if observation.case_id in observed:
            issues.append(f"duplicate case: {observation.case_id}")
            continue
        observed[observation.case_id] = observation

    missing = sorted(set(cases) - set(observed))
    issues.extend(f"missing case: {case_id}" for case_id in missing)

    routes = expected_routes()
    for case_id, observation in observed.items():
        case = cases[case_id]
        if routes[case_id] is not case.expected_route:
            issues.append(f"routing drift: {case_id}")
        if observation.model != LOCAL_MODEL:
            issues.append(f"unexpected model: {case_id}")
        if observation.role != case.role:
            issues.append(f"unexpected role: {case_id}")
        if observation.terminal_state != "PASS":
            issues.append(f"non-PASS terminal state: {case_id}")
        if not observation.repository_clean_before:
            issues.append(f"dirty before: {case_id}")
        if not observation.repository_clean_after:
            issues.append(f"dirty after: {case_id}")
        if not observation.head_unchanged:
            issues.append(f"HEAD changed: {case_id}")
        if not observation.deterministic_check_passed:
            issues.append(f"deterministic check failed: {case_id}")

    return not issues, tuple(sorted(issues))


def _load(path: Path) -> list[ShadowObservation]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, list):
        raise ValueError("shadow evidence must be a JSON list")
    observations: list[ShadowObservation] = []
    for item in value:
        if not isinstance(item, dict):
            raise ValueError("shadow evidence entries must be objects")
        observations.append(ShadowObservation(**item))
    return observations


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list-cases", action="store_true")
    parser.add_argument("--evidence")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.list_cases:
        payload = [
            {
                **asdict(case),
                "task_class": case.task_class.value,
                "expected_route": case.expected_route.value,
            }
            for case in CASES
        ]
        print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
        return 0
    if not args.evidence:
        raise SystemExit("--evidence is required unless --list-cases is used")
    try:
        observations = _load(Path(args.evidence))
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"issues": [str(exc)], "valid": False}, sort_keys=True))
        return 2
    valid, issues = validate_observations(observations)
    print(json.dumps({"issues": list(issues), "valid": valid}, sort_keys=True))
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
