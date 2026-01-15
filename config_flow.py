"""Config flow for Jullix Energy Management integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

from .api import JullixApiClient, JullixApiError, JullixConnectionError, JullixTimeoutError
from .const import CONF_HOST, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): cv.string,
    }
)


class JullixConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Jullix Energy Management."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]

            # Test connection to the device
            session = async_get_clientsession(self.hass)
            client = JullixApiClient(host, session)

            try:
                data = await client.get_all_data()

                # Extract meter ID for unique ID
                meter_id = data.get("dsmr", {}).get("id", {}).get("value")
                if meter_id:
                    await self.async_set_unique_id(meter_id)
                    self._abort_if_unique_id_configured()

                # Create the config entry
                return self.async_create_entry(
                    title=f"Jullix ({host})",
                    data=user_input,
                )

            except JullixTimeoutError:
                errors["base"] = "timeout"
            except JullixConnectionError:
                errors["base"] = "cannot_connect"
            except JullixApiError:
                errors["base"] = "unknown"
            except Exception:
                _LOGGER.exception("Unexpected exception during connection test")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
