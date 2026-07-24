"""Unit tests for UB_TRANSPORT resolution (see ultimate_brain_mcp.resolve_transport)."""

import pytest

from ultimate_brain_mcp import resolve_transport

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
