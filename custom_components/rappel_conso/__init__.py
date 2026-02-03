"""The Rappel Conso integration."""

from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.const import Platform
from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
)
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import (
    ATTR_BRANDS,
    ATTR_CATEGORIES,
    ATTR_KEYWORDS,
    ATTR_LIMIT,
    ATTR_PRODUCT_NAMES,
    DOMAIN,
    SERVICE_SEARCH_RECALLS,
)
from .coordinator import RappelConsoCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup(  # pylint: disable=unused-argument
    hass: HomeAssistant,
    config: ConfigType,  # noqa: ARG001
) -> bool:
    """Set up the Rappel Conso integration."""

    async def handle_search_recalls(call: ServiceCall) -> ServiceResponse:
        """Handle the search_recalls service call."""
        # Get all loaded config entries
        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="no_config_entry",
            )

        # Get the first loaded entry's coordinator
        entry = next((e for e in entries if e.state == ConfigEntryState.LOADED), None)
        if not entry:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="config_entry_not_loaded",
            )

        coordinator: RappelConsoCoordinator = hass.data[DOMAIN][entry.entry_id]

        # Extract service parameters
        product_names = call.data.get(ATTR_PRODUCT_NAMES)
        brands = call.data.get(ATTR_BRANDS)
        categories = call.data.get(ATTR_CATEGORIES)
        keywords = call.data.get(ATTR_KEYWORDS)
        limit = call.data.get(ATTR_LIMIT, 100)

        # Validate at least one search criterion is provided
        if not any([product_names, brands, categories, keywords]):
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="no_search_criteria",
            )

        # Perform search
        try:
            results = await coordinator.async_search_recalls(
                product_names=product_names,
                brands=brands,
                categories=categories,
                keywords=keywords,
                limit=limit,
            )

            return {
                "recalls": results,
                "count": len(results),
            }

        except Exception as err:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="search_failed",
                translation_placeholders={"error": str(err)},
            ) from err

    # Define service schema
    service_schema = vol.Schema(
        {
            vol.Optional(ATTR_PRODUCT_NAMES): vol.All(cv.ensure_list, [cv.string]),
            vol.Optional(ATTR_BRANDS): vol.All(cv.ensure_list, [cv.string]),
            vol.Optional(ATTR_CATEGORIES): vol.All(cv.ensure_list, [cv.string]),
            vol.Optional(ATTR_KEYWORDS): vol.All(cv.ensure_list, [cv.string]),
            vol.Optional(ATTR_LIMIT, default=100): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=1000)
            ),
        }
    )

    # Register the service
    hass.services.async_register(
        DOMAIN,
        SERVICE_SEARCH_RECALLS,
        handle_search_recalls,
        schema=service_schema,
        supports_response=SupportsResponse.ONLY,
    )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Rappel Conso from a config entry."""
    coordinator = RappelConsoCoordinator(hass)

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        coordinator: RappelConsoCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_shutdown()

    return unload_ok
