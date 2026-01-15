"""Test the Jullix integration initialization."""

from unittest.mock import AsyncMock, patch

from custom_components.jullix.api import JullixConnectionError
from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.core import HomeAssistant
from tests.common import MockConfigEntry


async def test_setup_entry_success(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_jullix_api: AsyncMock,
    mock_aiohttp_session,
) -> None:
    """Test successful setup of a config entry."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.LOADED


async def test_setup_entry_connection_error(
    hass: HomeAssistant, mock_config_entry: ConfigEntry, mock_aiohttp_session
) -> None:
    """Test setup fails when connection cannot be established."""
    mock_config_entry.add_to_hass(hass)

    with patch("custom_components.jullix.JullixApiClient") as mock_api:
        mock_api.return_value.test_connection = AsyncMock(
            side_effect=JullixConnectionError
        )

        assert not await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.SETUP_RETRY


async def test_unload_entry(
    hass: HomeAssistant,
    mock_config_entry: ConfigEntry,
    mock_jullix_api: AsyncMock,
    mock_aiohttp_session,
) -> None:
    """Test successful unload of a config entry."""
    mock_config_entry.add_to_hass(hass)

    with (
        patch("homeassistant.config_entries.ConfigEntries.async_forward_entry_setups", return_value=True),
        patch("homeassistant.config_entries.ConfigEntries.async_unload_platforms", return_value=True),
    ):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        assert mock_config_entry.state is ConfigEntryState.LOADED

        assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.NOT_LOADED
