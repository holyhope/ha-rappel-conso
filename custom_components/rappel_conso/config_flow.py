"""Config flow for Rappel Conso integration."""

from __future__ import annotations

import logging
from typing import Any

import httpx
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, NAME

_LOGGER = logging.getLogger(__name__)


async def validate_connection(_hass: HomeAssistant) -> dict[str, Any]:
    """Validate that we can connect to the API."""
    from .const import API_ENDPOINT

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                API_ENDPOINT,
                params={"limit": 1},
            )
            response.raise_for_status()
            data = response.json()

            if "total_count" not in data:
                msg = "Invalid API response structure"
                raise ValueError(msg)

            return {"total_recalls": data["total_count"]}

    except httpx.HTTPError:
        _LOGGER.exception("HTTP error connecting to Rappel Conso API")
        raise
    except Exception:
        _LOGGER.exception("Unexpected error connecting to Rappel Conso API")
        raise


class RappelConsoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Rappel Conso."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Check if already configured
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()

            try:
                await validate_connection(self.hass)
            except httpx.HTTPError:
                errors["base"] = "cannot_connect"
            except ValueError:
                errors["base"] = "invalid_response"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=NAME,
                    data={},
                    options={},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
            errors=errors,
            description_placeholders={
                "name": NAME,
            },
        )
