"""Sensor platform for Jullix Energy Management."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import JullixConfigEntry, JullixCoordinator
from .const import (
    DEVICE_INVERTER,
    DEVICE_METER,
    DOMAIN,
    DSMR_SENSORS,
    INVERTER_SENSORS,
)


@dataclass(frozen=True, kw_only=True)
class JullixSensorEntityDescription(SensorEntityDescription):
    """Describes Jullix sensor entity."""

    value_fn: Callable[[dict[str, Any]], float | int | str | None]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: JullixConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Jullix sensor entities."""
    coordinator = entry.runtime_data

    # Create DSMR sensor descriptions with value functions
    dsmr_sensor_descriptions = [
        JullixSensorEntityDescription(
            key=desc.key,
            translation_key=desc.translation_key,
            name=desc.name,
            device_class=desc.device_class,
            state_class=desc.state_class,
            native_unit_of_measurement=desc.native_unit_of_measurement,
            suggested_display_precision=desc.suggested_display_precision,
            entity_registry_enabled_default=desc.entity_registry_enabled_default,
            value_fn=lambda data, key=desc.key: (
                data.get("dsmr", {}).get(key, {}).get("value")
            ),
        )
        for desc in DSMR_SENSORS
    ]

    # Create inverter sensor descriptions with value functions
    inverter_sensor_descriptions = [
        JullixSensorEntityDescription(
            key=desc.key,
            translation_key=desc.translation_key,
            name=desc.name,
            device_class=desc.device_class,
            state_class=desc.state_class,
            native_unit_of_measurement=desc.native_unit_of_measurement,
            suggested_display_precision=desc.suggested_display_precision,
            entity_registry_enabled_default=desc.entity_registry_enabled_default,
            value_fn=lambda data, key=desc.key: (
                data.get("inverter", {}).get("data", {}).get(key)
            ),
        )
        for desc in INVERTER_SENSORS
    ]

    # Create DSMR sensor entities
    entities: list[JullixSensor] = [
        JullixSensor(coordinator, description, DEVICE_METER)
        for description in dsmr_sensor_descriptions
    ]

    # Create inverter sensor entities
    entities.extend(
        JullixSensor(coordinator, description, DEVICE_INVERTER)
        for description in inverter_sensor_descriptions
    )

    async_add_entities(entities)


class JullixSensor(CoordinatorEntity[JullixCoordinator], SensorEntity):
    """Representation of a Jullix sensor."""

    entity_description: JullixSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: JullixCoordinator,
        description: JullixSensorEntityDescription,
        device_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._device_type = device_type

        # Set unique ID based on device type and sensor key
        if device_type == DEVICE_METER:
            meter_id = coordinator.data.get("dsmr", {}).get("id", {}).get("value", "unknown")
            self._attr_unique_id = f"{meter_id}_{description.key}"
        else:
            # Use config entry ID for inverter as it may not have a unique serial
            self._attr_unique_id = (
                f"{coordinator.config_entry.entry_id}_{description.key}"
            )

        # Set device info
        self._attr_device_info = self._get_device_info()

    def _get_device_info(self) -> DeviceInfo:
        """Return device info for this sensor."""
        if self._device_type == DEVICE_METER:
            meter_id = self.coordinator.data.get("dsmr", {}).get("id", {}).get("value", "unknown")
            return DeviceInfo(
                identifiers={(DOMAIN, f"{DEVICE_METER}_{meter_id}")},
                name="Smart Meter",
                manufacturer="Jullix",
                model="DSMR P1 Meter",
            )

        # Inverter device
        inverter_data = self.coordinator.data.get("inverter", {})
        model = inverter_data.get("model", "Unknown")
        desc = inverter_data.get("desc", "Solar Inverter")

        # Use model as-is but capitalize for manufacturer
        manufacturer = model.capitalize() if model else "Unknown"

        return DeviceInfo(
            identifiers={(DOMAIN, f"{DEVICE_INVERTER}_{self.coordinator.config_entry.entry_id}")},
            name=desc,
            manufacturer=manufacturer,
            model=model,
        )

    @property
    def native_value(self) -> float | int | str | None:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        if not super().available:
            return False

        # Check device-specific availability
        if self._device_type == DEVICE_METER:
            return self.coordinator.data.get("dsmr", {}).get("connected", False)

        # For inverter, check if it's running
        return self.coordinator.data.get("inverter", {}).get("running", False)
