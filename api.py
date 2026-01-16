"""API client for Jullix Energy Management System."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

from .const import API_DSMR_STATUS, API_INVERTER_STATUS, API_TIMEOUT

_LOGGER = logging.getLogger(__name__)


class JullixApiError(Exception):
    """Base exception for Jullix API errors."""


class JullixConnectionError(JullixApiError):
    """Exception raised when connection to Jullix device fails."""


class JullixTimeoutError(JullixApiError):
    """Exception raised when API request times out."""


class JullixApiClient:
    """API client for Jullix Energy Management System."""

    def __init__(self, host: str, session: aiohttp.ClientSession) -> None:
        """Initialize the Jullix API client.

        Args:
            host: IP address or hostname of the Jullix device
            session: aiohttp ClientSession for making requests

        """
        self.host = host
        self.session = session
        self._base_url = f"http://{host}"

    async def _request(self, endpoint: str) -> dict[str, Any]:
        """Make an API request to the Jullix device.

        Args:
            endpoint: API endpoint path

        Returns:
            JSON response as dictionary

        Raises:
            JullixConnectionError: If connection fails
            JullixTimeoutError: If request times out

        """
        url = f"{self._base_url}{endpoint}"
        try:
            async with asyncio.timeout(API_TIMEOUT):
                async with self.session.get(url) as response:
                    response.raise_for_status()
                    return await response.json()
        except TimeoutError as err:
            raise JullixTimeoutError(f"Timeout connecting to {url}") from err
        except aiohttp.ClientError as err:
            raise JullixConnectionError(f"Failed to connect to {url}: {err}") from err

    async def get_dsmr_data(self) -> dict[str, Any]:
        """Fetch DSMR meter data.

        Returns:
            Dictionary containing DSMR meter data

        """
        _LOGGER.debug("Fetching DSMR data from %s", self.host)
        return await self._request(API_DSMR_STATUS)

    async def get_inverter_data(self) -> dict[str, Any]:
        """Fetch inverter/battery/solar data.

        Returns:
            Dictionary containing inverter data

        """
        _LOGGER.debug("Fetching inverter data from %s", self.host)
        return await self._request(API_INVERTER_STATUS)

    async def get_all_data(self) -> dict[str, Any]:
        """Fetch all data from both endpoints.

        Returns:
            Dictionary with 'dsmr' and 'inverter' keys containing respective data

        """
        dsmr_data, inverter_data = await asyncio.gather(
            self.get_dsmr_data(),
            self.get_inverter_data(),
        )
        return {
            "dsmr": dsmr_data,
            "inverter": inverter_data,
        }

    async def test_connection(self) -> bool:
        """Test connection to the Jullix device.

        Returns:
            True if connection successful

        Raises:
            JullixApiError: If connection test fails

        """
        await self.get_all_data()
        return True
