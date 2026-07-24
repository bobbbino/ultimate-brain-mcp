import os
import sys
from typing import Literal

from .server import mcp

# Transports FastMCP.run() accepts that make sense for this server. "sse" is
# deliberately excluded: the MCP spec deprecated it in favour of
# streamable-http, so nothing should start depending on it now.
Transport = Literal["stdio", "streamable-http"]
VALID_TRANSPORTS: tuple[Transport, ...] = ("stdio", "streamable-http")


def resolve_transport(value: str | None) -> Transport:
    """Validate a UB_TRANSPORT value, defaulting to stdio when unset/empty."""
    transport = value or "stdio"
    if transport not in VALID_TRANSPORTS:
        raise ValueError(
            f"Invalid UB_TRANSPORT {transport!r}: expected one of {', '.join(VALID_TRANSPORTS)}"
        )
    return transport


def main():
    required = [
        "NOTION_INTEGRATION_SECRET",
        "UB_TASKS_DS_ID",
        "UB_PROJECTS_DS_ID",
        "UB_NOTES_DS_ID",
        "UB_TAGS_DS_ID",
        "UB_GOALS_DS_ID",
    ]
    missing = [var for var in required if not os.environ.get(var)]
    if missing:
        print(
            f"Missing required environment variables: {', '.join(missing)}",
            file=sys.stderr,
        )
        sys.exit(1)
    # Transport is env-driven (not a CLI flag) so the same invocation works
    # under MCP client configs and containers alike.
    try:
        transport = resolve_transport(os.environ.get("UB_TRANSPORT"))
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
    if transport == "streamable-http":
        # Bind address via our own env vars, not FastMCP's FASTMCP_HOST/PORT:
        # FastMCP.__init__ passes its host/port defaults to Settings as
        # explicit init args, which beat env sources in pydantic-settings, so
        # the FASTMCP_* vars are silently ignored (mcp 1.26).
        mcp.settings.host = os.environ.get("UB_HOST") or "127.0.0.1"
        mcp.settings.port = int(os.environ.get("UB_PORT") or "8000")
    mcp.run(transport=transport)
