"""
MCP STDIO JSON codec.
"""

from __future__ import annotations

import json
from typing import Any

from ..transport.messages import (
    MCPRequest,
    MCPResponse,
)


def encode_response(
    response: MCPResponse,
) -> str:
    """
    Encode MCP response to JSON.
    """

    return json.dumps(
        {
            "id": response.id,
            "result": response.result,
            "error": response.error,
        }
    )


def decode_request(
    data: str,
) -> MCPRequest:
    """
    Decode JSON request.
    """

    payload: dict[str, Any] = json.loads(
        data
    )

    return MCPRequest(
        id=str(payload["id"]),
        method=payload["method"],
        params=payload.get(
            "params",
            {},
        ),
    )