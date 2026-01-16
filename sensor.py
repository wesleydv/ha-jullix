"""Sensor platform for Jullix Energy Management."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    RestoreSensor,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from . import JullixConfigEntry, JullixCoordinator
from .const import (
    BATTERY_ENERGY_SENSORS,
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

    # Create battery energy tracking sensors
    entities.extend(
        BatteryEnergySensor(coordinator, description)
        for description in BATTERY_ENERGY_SENSORS
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


class BatteryEnergySensor(CoordinatorEntity[JullixCoordinator], RestoreSensor):
    """Battery energy tracking sensor using Riemann sum integration."""

    _attr_has_entity_name = True
    _unrecorded_attributes = frozenset({"last_period"})

    def __init__(
        self,
        coordinator: JullixCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the battery energy sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"

        # Initialize tracking variables
        self._last_update_time: datetime | None = None
        self._last_power: float | None = None
        self._total_energy: float = 0.0

        # Determine if this tracks charging or discharging
        self._track_charging = description.key == "battery_energy_charged"

        # Set device info
        inverter_data = coordinator.data.get("inverter", {})
        model = inverter_data.get("model", "Unknown")
        desc = inverter_data.get("desc", "Solar Inverter")
        manufacturer = model.capitalize() if model else "Unknown"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{DEVICE_INVERTER}_{coordinator.config_entry.entry_id}")},
            name=desc,
            manufacturer=manufacturer,
            model=model,
        )

    async def async_added_to_hass(self) -> None:
        """Handle entity added to hass."""
        await super().async_added_to_hass()

        # Restore previous state
        if (last_sensor_data := await self.async_get_last_sensor_data()) is not None:
            if last_sensor_data.native_value is not None:
                self._total_energy = float(last_sensor_data.native_value)

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        # Get current battery power (in kW)
        inverter_data = self.coordinator.data.get("inverter", {})
        if not inverter_data.get("running", False):
            return

        battery_power = inverter_data.get("data", {}).get("battery_power")
        if battery_power is None:
            return

        now = dt_util.utcnow()

        # Calculate energy increment using left Riemann sum
        if self._last_update_time is not None and self._last_power is not None:
            time_delta_hours = (now - self._last_update_time).total_seconds() / 3600

            # Use left Riemann sum: energy = power × time
            # Power is in kW, time in hours, so energy is in kWh
            energy_increment = abs(self._last_power) * time_delta_hours

            # Only accumulate if power direction matches what we're tracking
            if self._track_charging and self._last_power < 0:
                # Charging: negative power
                self._total_energy += energy_increment
            elif not self._track_charging and self._last_power > 0:
                # Discharging: positive power
                self._total_energy += energy_increment

        # Update tracking variables for next calculation
        self._last_update_time = now
        self._last_power = battery_power

        self.async_write_ha_state()

    @property
    def native_value(self) -> float:
        """Return the state of the sensor."""
        return round(self._total_energy, 2)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        if not super().available:
            return False
        return self.coordinator.data.get("inverter", {}).get("running", False)
