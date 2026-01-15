"""Fixtures for Jullix Energy Management tests."""

import asyncio
from collections.abc import AsyncGenerator, Generator
import json
from pathlib import Path
import sys
from unittest.mock import AsyncMock, patch

import pytest

# Add the tests directory to the path so we can import from tests.common
sys.path.insert(0, str(Path(__file__).parents[3]))

from custom_components.jullix.const import CONF_HOST, DOMAIN
from homeassistant.core import HomeAssistant
from tests.common import MockConfigEntry, async_test_home_assistant


@pytest.fixture
async def hass() -> AsyncGenerator[HomeAssistant]:
    """Create a test instance of Home Assistant."""
    loop = asyncio.get_running_loop()
    async with async_test_home_assistant(loop) as hass_instance:
        # Add custom_components to the loader's path
        hass_instance.config.components.add(DOMAIN)
        yield hass_instance


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(hass: HomeAssistant):
    """Enable custom integrations in tests."""
    # This is needed to load integrations from custom_components
    from homeassistant import loader  # noqa: PLC0415

    async def mock_async_get_custom_components(hass: HomeAssistant):
        """Return custom components including our test integration."""
        # Get the path to our custom component
        custom_comp_path = Path(__file__).parent.parent
        return {
            DOMAIN: loader.Integration(
                hass,
                f"custom_components.{DOMAIN}",
                custom_comp_path,
                {
                    "domain": DOMAIN,
                    "name": "Jullix Energy Management (Local)",
                    "config_flow": True,
                    "documentation": "https://www.home-assistant.io/integrations/jullix",
                    "requirements": [],
                    "codeowners": [],
                    "integration_type": "device",
                    "iot_class": "local_polling",
                },
            )
        }

    with patch.object(loader, "async_get_custom_components", mock_async_get_custom_components):
        yield


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return the default mocked config entry."""
    return MockConfigEntry(
        version=1,
        minor_version=1,
        domain=DOMAIN,
        title="Jullix (192.168.4.167)",
        data={CONF_HOST: "192.168.4.167"},
        source="user",
        unique_id="1SAG3200415379",
    )


@pytest.fixture
def mock_dsmr_data() -> dict:
    """Return mocked DSMR data."""
    fixture_path = Path(__file__).parent / "fixtures" / "dsmr_status.json"
    return json.loads(fixture_path.read_text())


@pytest.fixture
def mock_inverter_data() -> dict:
    """Return mocked inverter data."""
    fixture_path = Path(__file__).parent / "fixtures" / "inverter_status.json"
    return json.loads(fixture_path.read_text())


@pytest.fixture
def mock_aiohttp_session():
    """Mock aiohttp client session."""
    from unittest.mock import MagicMock  # noqa: PLC0415

    session = MagicMock()
    with (
        patch("homeassistant.helpers.aiohttp_client.async_get_clientsession", return_value=session),
        patch("custom_components.jullix.async_get_clientsession", return_value=session),
        patch("custom_components.jullix.config_flow.async_get_clientsession", return_value=session),
    ):
        yield session


@pytest.fixture
def mock_jullix_api(mock_dsmr_data: dict, mock_inverter_data: dict, mock_aiohttp_session) -> Generator[AsyncMock]:
    """Return a mocked Jullix API client."""
    with (
        patch("custom_components.jullix.config_flow.JullixApiClient", autospec=True) as mock_api_config,
        patch("custom_components.jullix.JullixApiClient", autospec=True) as mock_api_init,
    ):
        # Mock for config_flow
        api_config = mock_api_config.return_value
        api_config.get_dsmr_data = AsyncMock(return_value=mock_dsmr_data)
        api_config.get_inverter_data = AsyncMock(return_value=mock_inverter_data)
        api_config.get_all_data = AsyncMock(
            return_value={
                "dsmr": mock_dsmr_data,
                "inverter": mock_inverter_data,
            }
        )
        api_config.test_connection = AsyncMock(return_value=True)

        # Mock for __init__
        api_init = mock_api_init.return_value
        api_init.get_dsmr_data = AsyncMock(return_value=mock_dsmr_data)
        api_init.get_inverter_data = AsyncMock(return_value=mock_inverter_data)
        api_init.get_all_data = AsyncMock(
            return_value={
                "dsmr": mock_dsmr_data,
                "inverter": mock_inverter_data,
            }
        )
        api_init.test_connection = AsyncMock(return_value=True)

        yield api_config


@pytest.fixture
def mock_setup_entry() -> Generator[AsyncMock]:
    """Mock setting up a config entry."""
    with patch(
        "custom_components.jullix.async_setup_entry", return_value=True
    ) as mock_setup:
        yield mock_setup
