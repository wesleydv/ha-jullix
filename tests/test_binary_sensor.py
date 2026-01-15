"""Test the Jullix binary sensor platform."""

from unittest.mock import AsyncMock

from custom_components.jullix.binary_sensor import (
    JullixBinarySensor,
    JullixBinarySensorEntityDescription,
)
from custom_components.jullix.const import DOMAIN
from homeassistant.components.binary_sensor import BinarySensorDeviceClass


async def test_binary_sensor_on():
    """Test binary sensor in ON state."""
    coordinator = AsyncMock()
    coordinator.data = {
        "dsmr": {
            "id": {"value": "ABC123"},
            "connected": True,
            "tariff1": {"value": True},
        }
    }
    coordinator.config_entry = AsyncMock()
    coordinator.config_entry.entry_id = "test_entry"

    description = JullixBinarySensorEntityDescription(
        key="tariff1",
        translation_key="tariff1",
        name="Tariff 1",
        value_fn=lambda data: data.get("dsmr", {}).get("tariff1", {}).get("value"),
    )

    binary_sensor = JullixBinarySensor(coordinator, description, "meter")

    assert binary_sensor.unique_id == "ABC123_tariff1"
    assert binary_sensor.is_on is True
    assert binary_sensor.available is True


async def test_binary_sensor_off():
    """Test binary sensor in OFF state."""
    coordinator = AsyncMock()
    coordinator.data = {
        "dsmr": {
            "id": {"value": "ABC123"},
            "connected": True,
            "tariff1": {"value": False},
        }
    }
    coordinator.config_entry = AsyncMock()
    coordinator.config_entry.entry_id = "test_entry"

    description = JullixBinarySensorEntityDescription(
        key="tariff1",
        translation_key="tariff1",
        name="Tariff 1",
        value_fn=lambda data: data.get("dsmr", {}).get("tariff1", {}).get("value"),
    )

    binary_sensor = JullixBinarySensor(coordinator, description, "meter")

    assert binary_sensor.is_on is False


async def test_binary_sensor_no_data():
    """Test binary sensor when data is missing."""
    coordinator = AsyncMock()
    coordinator.data = {}
    coordinator.config_entry = AsyncMock()
    coordinator.config_entry.entry_id = "test_entry"

    description = JullixBinarySensorEntityDescription(
        key="tariff1",
        translation_key="tariff1",
        name="Tariff 1",
        value_fn=lambda data: data.get("dsmr", {}).get("tariff1", {}).get("value"),
    )

    binary_sensor = JullixBinarySensor(coordinator, description, "meter")

    # Should return None (unknown state) when data is missing
    assert binary_sensor.is_on is None


async def test_binary_sensor_device_info():
    """Test binary sensor device info."""
    coordinator = AsyncMock()
    coordinator.data = {"dsmr": {"id": {"value": "123456"}, "connected": True}}
    coordinator.config_entry = AsyncMock()
    coordinator.config_entry.entry_id = "test_entry"

    description = JullixBinarySensorEntityDescription(
        key="tariff1",
        translation_key="tariff1",
        name="Tariff 1",
        value_fn=lambda data: data.get("dsmr", {}).get("tariff1", {}).get("value"),
    )

    binary_sensor = JullixBinarySensor(coordinator, description, "meter")

    device_info = binary_sensor.device_info
    assert device_info["identifiers"] == {(DOMAIN, "meter_123456")}
    assert device_info["name"] == "Smart Meter"
    assert device_info["manufacturer"] == "Jullix"


async def test_inverter_binary_sensor():
    """Test inverter binary sensor."""
    coordinator = AsyncMock()
    coordinator.data = {
        "inverter": {
            "data": {
                "grid-connected": True,
            },
            "model": "TestInverter",
            "desc": "Solar Inverter",
            "running": True,
        }
    }
    coordinator.config_entry = AsyncMock()
    coordinator.config_entry.entry_id = "test_entry"

    description = JullixBinarySensorEntityDescription(
        key="grid-connected",
        translation_key="grid_connected",
        name="Grid connected",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value_fn=lambda data: data.get("inverter", {}).get("data", {}).get("grid-connected"),
    )

    binary_sensor = JullixBinarySensor(coordinator, description, "inverter")

    assert binary_sensor.unique_id == "test_entry_grid-connected"
    assert binary_sensor.is_on is True
    assert binary_sensor.device_class == BinarySensorDeviceClass.CONNECTIVITY

    device_info = binary_sensor.device_info
    assert device_info["identifiers"] == {(DOMAIN, "inverter_test_entry")}
    assert device_info["model"] == "TestInverter"
