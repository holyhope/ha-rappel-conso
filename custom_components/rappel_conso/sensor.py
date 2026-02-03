"""Sensor platform for Rappel Conso."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN, SENSOR_ICON, SENSOR_NAME
from .coordinator import RappelConsoCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Rappel Conso sensor."""
    coordinator: RappelConsoCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([RappelConsoSensor(coordinator)], True)


class RappelConsoSensor(CoordinatorEntity[RappelConsoCoordinator], SensorEntity):
    """Representation of a Rappel Conso sensor."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_icon = SENSOR_ICON
    _attr_native_unit_of_measurement = "recalls"

    def __init__(self, coordinator: RappelConsoCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = DOMAIN
        self._attr_device_info = {
            "identifiers": {(DOMAIN, DOMAIN)},
            "name": SENSOR_NAME,
            "manufacturer": "data.gouv.fr",
            "model": "RappelConso V2",
            "entry_type": "service",
        }

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("total_count")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if not self.coordinator.data:
            return {
                "attribution": ATTRIBUTION,
            }

        return {
            "last_update": self.coordinator.data.get("last_update"),
            "new_recalls_count": self.coordinator.data.get("new_recalls_count", 0),
            "recent_recalls": self.coordinator.data.get("recent_recalls", []),
            "attribution": ATTRIBUTION,
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success and self.coordinator.data is not None
        )
