"""Unit tests for transport env resolution (see ultimate_brain_mcp.resolve_transport
and resolve_transport_security)."""

import pytest

from ultimate_brain_mcp import (
    parse_host_list,
    resolve_transport,
    resolve_transport_security,
)

pytestmark = pytest.mark.unit


def test_default_is_stdio():
    assert resolve_transport(None) == "stdio"


def test_empty_string_is_stdio():
    assert resolve_transport("") == "stdio"


def test_streamable_http():
    assert resolve_transport("streamable-http") == "streamable-http"


def test_invalid_value_raises():
    with pytest.raises(ValueError, match="Invalid UB_TRANSPORT 'sse'"):
        resolve_transport("sse")


def test_parse_host_list_unset_and_empty():
    assert parse_host_list(None) == []
    assert parse_host_list("") == []
    assert parse_host_list(" , ,") == []


def test_parse_host_list_splits_and_strips():
    assert parse_host_list(" ultimate-brain-mcp:* , localhost:8000 ") == [
        "ultimate-brain-mcp:*",
        "localhost:8000",
    ]


def test_security_unset_is_none():
    assert resolve_transport_security(None, None) is None
    assert resolve_transport_security("", "") is None


def test_security_hosts_enable_protection():
    settings = resolve_transport_security("ultimate-brain-mcp:*", None)
    assert settings is not None
    assert settings.enable_dns_rebinding_protection is True
    assert settings.allowed_hosts == ["ultimate-brain-mcp:*"]
    assert settings.allowed_origins == []


def test_security_hosts_and_origins():
    settings = resolve_transport_security(
        "ultimate-brain-mcp:*", "http://ultimate-brain-mcp:*"
    )
    assert settings is not None
    assert settings.allowed_origins == ["http://ultimate-brain-mcp:*"]


def test_security_origins_without_hosts_raise():
    with pytest.raises(ValueError, match="requires UB_ALLOWED_HOSTS"):
        resolve_transport_security(None, "http://evil.example")
