import os
import sys
from typing import Literal

from mcp.server.transport_security import TransportSecuritySettings

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


def parse_host_list(value: str | None) -> list[str]:
    """Split a comma-separated env value into a clean list (empty when unset)."""
    return [item.strip() for item in (value or "").split(",") if item.strip()]


def resolve_transport_security(
    hosts_value: str | None, origins_value: str | None
) -> TransportSecuritySettings | None:
    """Build DNS-rebinding-protection settings from UB_ALLOWED_HOSTS/ORIGINS.

    FastMCP auto-enables DNS rebinding protection with a localhost-only Host
    allowlist at construction time (the server object is built at import with
    the default host 127.0.0.1). Re-binding via UB_HOST later does not update
    that allowlist, so a server on 0.0.0.0 behind a proxy or MCP gateway
    answers 421 Misdirected Request to every request whose Host header is not
    localhost. When UB_ALLOWED_HOSTS is set (comma-separated Host values,
    ":*" port wildcard supported, e.g. "ultimate-brain-mcp:*"), protection
    stays ON with that allowlist instead. UB_ALLOWED_ORIGINS is the same for
    the Origin header and requires UB_ALLOWED_HOSTS — origins alone would
    build an empty Host allowlist that rejects everything. Both unset ->
    None, and the SDK's localhost default stands.
    """
    hosts = parse_host_list(hosts_value)
    origins = parse_host_list(origins_value)
    if origins and not hosts:
        raise ValueError("UB_ALLOWED_ORIGINS requires UB_ALLOWED_HOSTS to be set")
    if not hosts:
        return None
    return TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=hosts,
        allowed_origins=origins,
    )


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
        # Host-header allowlist for proxied/gatewayed serving — see
        # resolve_transport_security's docstring for why the constructor-time
        # localhost default must be replaced here.
        try:
            security = resolve_transport_security(
                os.environ.get("UB_ALLOWED_HOSTS"),
                os.environ.get("UB_ALLOWED_ORIGINS"),
            )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            sys.exit(1)
        if security is not None:
            mcp.settings.transport_security = security
    mcp.run(transport=transport)
