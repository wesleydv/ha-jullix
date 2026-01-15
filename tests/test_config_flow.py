"""Test the Jullix config flow."""

from unittest.mock import AsyncMock, patch

from custom_components.jullix.api import JullixConnectionError
from custom_components.jullix.const import CONF_HOST, DOMAIN
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType


async def test_form(hass: HomeAssistant, mock_jullix_api: AsyncMock) -> None:
    """Test we get the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {}

    with patch(
        "custom_components.jullix.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_HOST: "192.168.1.100"},
        )
        await hass.async_block_till_done()

    assert result2["type"] is FlowResultType.CREATE_ENTRY
    assert result2["title"] == "Jullix (192.168.1.100)"
    assert result2["data"] == {CONF_HOST: "192.168.1.100"}
    assert len(mock_setup_entry.mock_calls) == 1


async def test_form_cannot_connect(hass: HomeAssistant) -> None:
    """Test we handle cannot connect error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with (
        patch("homeassistant.helpers.aiohttp_client.async_get_clientsession"),
        patch("custom_components.jullix.config_flow.JullixApiClient") as mock_api,
    ):
        instance = mock_api.return_value
        instance.get_all_data = AsyncMock(side_effect=JullixConnectionError)
        instance.test_connection = AsyncMock(side_effect=JullixConnectionError)
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_HOST: "192.168.1.100"},
        )

    assert result2["type"] is FlowResultType.FORM
    assert result2["errors"] == {"base": "cannot_connect"}


async def test_form_unexpected_exception(hass: HomeAssistant) -> None:
    """Test we handle unexpected exception."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with (
        patch("homeassistant.helpers.aiohttp_client.async_get_clientsession"),
        patch("custom_components.jullix.config_flow.JullixApiClient") as mock_api,
    ):
        instance = mock_api.return_value
        instance.get_all_data = AsyncMock(side_effect=Exception)
        instance.test_connection = AsyncMock(side_effect=Exception)
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_HOST: "192.168.1.100"},
        )

    assert result2["type"] is FlowResultType.FORM
    assert result2["errors"] == {"base": "unknown"}
