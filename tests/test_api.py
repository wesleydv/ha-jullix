"""Tests for the Jullix API client."""

from unittest.mock import AsyncMock, MagicMock, Mock, patch

import aiohttp
import pytest

from custom_components.jullix.api import (
    JullixApiClient,
    JullixConnectionError,
    JullixTimeoutError,
)


def test_api_client_initialization():
    """Test API client can be initialized."""
    session = Mock()
    client = JullixApiClient("192.168.4.167", session)
    assert client.host == "192.168.4.167"
    assert client._base_url == "http://192.168.4.167"  # noqa: SLF001


async def test_api_get_all_data():
    """Test getting all data returns correct structure."""
    session = Mock()
    client = JullixApiClient("192.168.4.167", session)

    # Mock the individual data methods
    client.get_dsmr_data = AsyncMock(return_value={"power": {"value": 1.0}})
    client.get_inverter_data = AsyncMock(return_value={"model": "TEST"})

    result = await client.get_all_data()

    assert "dsmr" in result
    assert "inverter" in result
    assert result["dsmr"]["power"]["value"] == 1.0
    assert result["inverter"]["model"] == "TEST"


async def test_api_get_dsmr_data_success():
    """Test successfully getting DSMR data."""
    mock_response = MagicMock()
    mock_response.json = AsyncMock(return_value={"power": {"value": 1.0}})
    mock_response.raise_for_status = MagicMock()
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)

    session = MagicMock()
    session.get = MagicMock(return_value=mock_response)

    client = JullixApiClient("192.168.4.167", session)
    result = await client.get_dsmr_data()

    assert result == {"power": {"value": 1.0}}
    session.get.assert_called_once_with("http://192.168.4.167/api/dsmr/status")


async def test_api_get_inverter_data_success():
    """Test successfully getting inverter data."""
    mock_response = MagicMock()
    mock_response.json = AsyncMock(return_value={"model": "TEST"})
    mock_response.raise_for_status = MagicMock()
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)

    session = MagicMock()
    session.get = MagicMock(return_value=mock_response)

    client = JullixApiClient("192.168.4.167", session)
    result = await client.get_inverter_data()

    assert result == {"model": "TEST"}
    session.get.assert_called_once_with("http://192.168.4.167/api/inverter/status/A")


async def test_api_connection_error():
    """Test connection error is raised properly."""
    mock_response = MagicMock()
    mock_response.__aenter__ = AsyncMock(side_effect=aiohttp.ClientError("Connection failed"))

    session = MagicMock()
    session.get = MagicMock(return_value=mock_response)

    client = JullixApiClient("192.168.4.167", session)

    with pytest.raises(JullixConnectionError, match="Failed to connect"):
        await client.get_dsmr_data()


async def test_api_timeout_error():
    """Test timeout error is raised properly."""
    with patch("asyncio.timeout") as mock_timeout:
        # Make asyncio.timeout raise TimeoutError when entering the context
        mock_timeout.return_value.__aenter__ = AsyncMock(side_effect=TimeoutError())

        session = MagicMock()
        client = JullixApiClient("192.168.4.167", session)

        with pytest.raises(JullixTimeoutError, match="Timeout connecting to"):
            await client.get_dsmr_data()


async def test_api_test_connection_success():
    """Test connection test succeeds."""
    session = Mock()
    client = JullixApiClient("192.168.4.167", session)

    client.get_all_data = AsyncMock(return_value={"dsmr": {}, "inverter": {}})

    result = await client.test_connection()

    assert result is True


async def test_api_test_connection_failure():
    """Test connection test fails and raises error."""
    session = Mock()
    client = JullixApiClient("192.168.4.167", session)

    client.get_all_data = AsyncMock(side_effect=JullixConnectionError("Connection failed"))

    with pytest.raises(JullixConnectionError):
        await client.test_connection()
