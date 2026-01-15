"""The Jullix Energy Management integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import JullixApiClient, JullixApiError, JullixConnectionError
from .const import CONF_HOST, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]

type JullixConfigEntry = ConfigEntry[JullixCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: JullixConfigEntry) -> bool:
    """Set up Jullix from a config entry."""
    host = entry.data[CONF_HOST]

    session = async_get_clientsession(hass)
    client = JullixApiClient(host, session)

    # Test connection before setup
    try:
        await client.test_connection()
    except JullixConnectionError as err:
        raise ConfigEntryNotReady(f"Unable to connect to Jullix device at {host}") from err
    except JullixApiError as err:
        raise ConfigEntryNotReady(f"Error communicating with Jullix device: {err}") from err

    coordinator = JullixCoordinator(hass, client, entry)

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: JullixConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


class JullixCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Jullix data from the device."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: JullixApiClient,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
            config_entry=config_entry,
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from Jullix device."""
        try:
            return await self.client.get_all_data()
        except JullixApiError as err:
            raise UpdateFailed(f"Error communicating with Jullix device: {err}") from err
