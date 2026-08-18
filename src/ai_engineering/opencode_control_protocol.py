"""Typed, deterministic protocol for AUTO-0013 OpenCode control requests/results."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

PROTOCOL_VERSION = 1
MAX_OBJECTIVE_CHARS = 4_000
MAX_RESULT_CHARS = 20_000
MIN_RESULT_CHARS = 256
_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_REQUEST_ID_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
_REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


class ControlProtocolError(ValueError):
    """Raised when a control-plane value fails closed validation."""


class ControlTaskClass(str, Enum):
    STATUS = "status"
    INSPECT = "inspect"
    PLAN = "plan"
    DIFF = "diff"


class ControlResultState(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    REFUSED = "REFUSED"
    FAILED = "FAILED"


@dataclass(frozen=True, slots=True)
class ControlRequest:
    request_id: str
    task_class: ControlTaskClass
    objective: str
    repository: str
    expected_head: str | None = None
    max_result_chars: int = 8_000
    version: int = PROTOCOL_VERSION


@dataclass(frozen=True, slots=True)
class ControlResult:
    request_id: str
    task_class: ControlTaskClass
    repository: str
    branch: str
    head: str
    pre_clean: bool
    state: ControlResultState
    text: str
    post_clean: bool
    version: int = PROTOCOL_VERSION


def _canonical_json(value: Mapping[str, Any]) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _request_payload(
    *,
    task_class: ControlTaskClass,
    objective: str,
    repository: str,
    expected_head: str | None,
    max_result_chars: int,
    version: int,
) -> dict[str, Any]:
    return {
        "expected_head": expected_head,
        "max_result_chars": max_result_chars,
        "objective": objective,
        "repository": repository,
        "task_class": task_class.value,
        "version": version,
    }


def _validate_request_fields(
    *,
    task_class: ControlTaskClass,
    objective: str,
    repository: str,
    expected_head: str | None,
    max_result_chars: int,
    version: int,
) -> None:
    if version != PROTOCOL_VERSION:
        raise ControlProtocolError(f"unsupported protocol version: {version}")
    if not isinstance(objective, str):
        raise ControlProtocolError("objective must be a string")
    if not objective.strip():
        raise ControlProtocolError("objective must not be empty")
    if len(objective) > MAX_OBJECTIVE_CHARS:
        raise ControlProtocolError("objective exceeds maximum length")
    if "\x00" in objective:
        raise ControlProtocolError("objective contains NUL")
    if not isinstance(repository, str) or not _REPOSITORY_RE.fullmatch(repository):
        raise ControlProtocolError("repository must be owner/name")
    if expected_head is not None and (
        not isinstance(expected_head, str) or not _SHA_RE.fullmatch(expected_head)
    ):
        raise ControlProtocolError("expected_head must be a lowercase 40-character SHA")
    if isinstance(max_result_chars, bool) or not isinstance(max_result_chars, int):
        raise ControlProtocolError("max_result_chars must be an integer")
    if not MIN_RESULT_CHARS <= max_result_chars <= MAX_RESULT_CHARS:
        message = (
            "max_result_chars must be between "
            f"{MIN_RESULT_CHARS} and {MAX_RESULT_CHARS}"
        )
        raise ControlProtocolError(message)
    if not isinstance(task_class, ControlTaskClass):
        raise ControlProtocolError("invalid task class")


def derive_request_id(
    *,
    task_class: ControlTaskClass,
    objective: str,
    repository: str,
    expected_head: str | None = None,
    max_result_chars: int = 8_000,
    version: int = PROTOCOL_VERSION,
) -> str:
    """Derive the deterministic request identifier from canonical request fields."""

    _validate_request_fields(
        task_class=task_class,
        objective=objective,
        repository=repository,
        expected_head=expected_head,
        max_result_chars=max_result_chars,
        version=version,
    )
    payload = _request_payload(
        task_class=task_class,
        objective=objective,
        repository=repository,
        expected_head=expected_head,
        max_result_chars=max_result_chars,
        version=version,
    )
    return "sha256:" + hashlib.sha256(_canonical_json(payload)).hexdigest()


def build_request(
    *,
    task_class: ControlTaskClass,
    objective: str,
    repository: str,
    expected_head: str | None = None,
    max_result_chars: int = 8_000,
) -> ControlRequest:
    request_id = derive_request_id(
        task_class=task_class,
        objective=objective,
        repository=repository,
        expected_head=expected_head,
        max_result_chars=max_result_chars,
    )
    return ControlRequest(
        request_id=request_id,
        task_class=task_class,
        objective=objective,
        repository=repository,
        expected_head=expected_head,
        max_result_chars=max_result_chars,
    )


def serialize_request(request: ControlRequest) -> bytes:
    expected = derive_request_id(
        task_class=request.task_class,
        objective=request.objective,
        repository=request.repository,
        expected_head=request.expected_head,
        max_result_chars=request.max_result_chars,
        version=request.version,
    )
    if request.request_id != expected:
        raise ControlProtocolError(
            "request_id does not match canonical request payload"
        )
    return _canonical_json(
        {
            "expected_head": request.expected_head,
            "max_result_chars": request.max_result_chars,
            "objective": request.objective,
            "repository": request.repository,
            "request_id": request.request_id,
            "task_class": request.task_class.value,
            "version": request.version,
        }
    )


def _load_object(data: bytes | str) -> dict[str, Any]:
    try:
        value = json.loads(data)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ControlProtocolError("malformed JSON") from exc
    if not isinstance(value, dict):
        raise ControlProtocolError("protocol document must be a JSON object")
    return value


def parse_request(data: bytes | str) -> ControlRequest:
    value = _load_object(data)
    expected_keys = {
        "expected_head",
        "max_result_chars",
        "objective",
        "repository",
        "request_id",
        "task_class",
        "version",
    }
    if set(value) != expected_keys:
        raise ControlProtocolError("request fields do not match protocol schema")
    try:
        task_class = ControlTaskClass(value["task_class"])
    except (TypeError, ValueError) as exc:
        raise ControlProtocolError("unknown task class") from exc
    if not isinstance(value["version"], int) or isinstance(value["version"], bool):
        raise ControlProtocolError("version must be an integer")
    request = ControlRequest(
        request_id=value["request_id"],
        task_class=task_class,
        objective=value["objective"],
        repository=value["repository"],
        expected_head=value["expected_head"],
        max_result_chars=value["max_result_chars"],
        version=value["version"],
    )
    if not isinstance(request.request_id, str) or not _REQUEST_ID_RE.fullmatch(
        request.request_id
    ):
        raise ControlProtocolError("invalid request_id format")
    expected_id = derive_request_id(
        task_class=request.task_class,
        objective=request.objective,
        repository=request.repository,
        expected_head=request.expected_head,
        max_result_chars=request.max_result_chars,
        version=request.version,
    )
    if request.request_id != expected_id:
        raise ControlProtocolError(
            "request_id does not match canonical request payload"
        )
    return request


def serialize_result(result: ControlResult) -> bytes:
    _validate_result(result)
    return _canonical_json(
        {
            "branch": result.branch,
            "head": result.head,
            "post_clean": result.post_clean,
            "pre_clean": result.pre_clean,
            "repository": result.repository,
            "request_id": result.request_id,
            "state": result.state.value,
            "task_class": result.task_class.value,
            "text": result.text,
            "version": result.version,
        }
    )


def _validate_result(result: ControlResult) -> None:
    if result.version != PROTOCOL_VERSION:
        raise ControlProtocolError(f"unsupported protocol version: {result.version}")
    if not _REQUEST_ID_RE.fullmatch(result.request_id):
        raise ControlProtocolError("invalid request_id format")
    if not _REPOSITORY_RE.fullmatch(result.repository):
        raise ControlProtocolError("repository must be owner/name")
    if not isinstance(result.branch, str) or not result.branch.strip():
        raise ControlProtocolError("branch must not be empty")
    if not _SHA_RE.fullmatch(result.head):
        raise ControlProtocolError("head must be a lowercase 40-character SHA")
    if not isinstance(result.pre_clean, bool) or not isinstance(
        result.post_clean, bool
    ):
        raise ControlProtocolError("cleanliness evidence must be boolean")
    if not isinstance(result.text, str):
        raise ControlProtocolError("result text must be a string")
    if len(result.text) > MAX_RESULT_CHARS:
        raise ControlProtocolError("result text exceeds protocol maximum")
    if "\x00" in result.text:
        raise ControlProtocolError("result text contains NUL")


def parse_result(data: bytes | str) -> ControlResult:
    value = _load_object(data)
    expected_keys = {
        "branch",
        "head",
        "post_clean",
        "pre_clean",
        "repository",
        "request_id",
        "state",
        "task_class",
        "text",
        "version",
    }
    if set(value) != expected_keys:
        raise ControlProtocolError("result fields do not match protocol schema")
    try:
        task_class = ControlTaskClass(value["task_class"])
    except (TypeError, ValueError) as exc:
        raise ControlProtocolError("unknown task class") from exc
    try:
        state = ControlResultState(value["state"])
    except (TypeError, ValueError) as exc:
        raise ControlProtocolError("unknown result state") from exc
    if not isinstance(value["version"], int) or isinstance(value["version"], bool):
        raise ControlProtocolError("version must be an integer")
    result = ControlResult(
        request_id=value["request_id"],
        task_class=task_class,
        repository=value["repository"],
        branch=value["branch"],
        head=value["head"],
        pre_clean=value["pre_clean"],
        state=state,
        text=value["text"],
        post_clean=value["post_clean"],
        version=value["version"],
    )
    _validate_result(result)
    return result


def validate_result_for_request(result: ControlResult, request: ControlRequest) -> None:
    """Fail closed unless result identity/scope matches the originating request."""

    _validate_result(result)
    if result.request_id != request.request_id:
        raise ControlProtocolError("result request_id does not match request")
    if result.task_class is not request.task_class:
        raise ControlProtocolError("result task class does not match request")
    if result.repository != request.repository:
        raise ControlProtocolError("result repository does not match request")
    if request.expected_head is not None and result.head != request.expected_head:
        raise ControlProtocolError("result HEAD does not match expected_head")
    if len(result.text) > request.max_result_chars:
        raise ControlProtocolError("result text exceeds request bound")
