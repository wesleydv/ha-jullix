"""Simple tests for Jullix integration."""

from custom_components.jullix.const import CONF_HOST, DOMAIN


def test_constants():
    """Test that constants are defined."""
    assert DOMAIN == "jullix"
    assert CONF_HOST == "host"
