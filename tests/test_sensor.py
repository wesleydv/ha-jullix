"""Test the Jullix sensor platform."""

from unittest.mock import AsyncMock

from custom_components.jullix.const import DOMAIN
from custom_components.jullix.sensor import JullixSensor, JullixSensorEntityDescription
from homeassistant.const import UnitOfEnergy


async def test_sensor_entity_properties():
    """Test sensor entity properties."""
    # Create a mock coordinator
    coordinator = AsyncMock()
    coordinator.data = {
        "dsmr": {
            "id": {"value": "ABC123"},
            "energy-in": {"value": 1234.5},
            "power": {"value": 500},
            "connected": True,
        },
        "inverter": {
            "data": {
                "pv-power": 300,
                "battery-soc": 85,
            }
        }
    }
    coordinator.config_entry = AsyncMock()
    coordinator.config_entry.entry_id = "test_entry"

    # Create a sensor description
    description = JullixSensorEntityDescription(
        key="energy-in",
        translation_key="energy_import",
        name="Energy import",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        value_fn=lambda data: data.get("dsmr", {}).get("energy-in", {}).get("value"),
    )

    # Create the sensor entity
    sensor = JullixSensor(coordinator, description, "meter")

    # Test properties
    assert sensor.unique_id == "ABC123_energy-in"
    assert sensor.native_value == 1234.5
    assert sensor.native_unit_of_measurement == UnitOfEnergy.KILO_WATT_HOUR
    assert sensor.available is True


async def test_sensor_entity_no_data():
    """Test sensor entity when data is missing."""
    coordinator = AsyncMock()
    coordinator.data = {}

    description = JullixSensorEntityDescription(
        key="energy-in",
        translation_key="energy_import",
        name="Energy import",
        value_fn=lambda data: data.get("dsmr", {}).get("energy-in", {}).get("value"),
    )

    sensor = JullixSensor(coordinator, description, "meter")

    # Should return None when data is missing
    assert sensor.native_value is None


async def test_sensor_device_info():
    """Test sensor device info."""
    coordinator = AsyncMock()
    coordinator.data = {"dsmr": {"id": {"value": "123456"}, "connected": True}}
    coordinator.config_entry = AsyncMock()
    coordinator.config_entry.entry_id = "test_entry"

    description = JullixSensorEntityDescription(
        key="power",
        translation_key="power",
        name="Power",
        value_fn=lambda data: data.get("dsmr", {}).get("power", {}).get("value"),
    )

    sensor = JullixSensor(coordinator, description, "meter")

    device_info = sensor.device_info
    assert device_info["identifiers"] == {(DOMAIN, "meter_123456")}
    assert device_info["name"] == "Smart Meter"
    assert device_info["manufacturer"] == "Jullix"
    assert device_info["model"] == "DSMR P1 Meter"


async def test_inverter_sensor():
    """Test inverter sensor."""
    coordinator = AsyncMock()
    coordinator.data = {
        "inverter": {
            "data": {
                "pv-power": 300,
            },
            "model": "TestInverter",
            "desc": "Solar Inverter",
            "running": True,
        }
    }
    coordinator.config_entry = AsyncMock()
    coordinator.config_entry.entry_id = "test_entry"

    description = JullixSensorEntityDescription(
        key="pv-power",
        translation_key="pv_power",
        name="PV power",
        value_fn=lambda data: data.get("inverter", {}).get("data", {}).get("pv-power"),
    )

    sensor = JullixSensor(coordinator, description, "inverter")

    assert sensor.unique_id == "test_entry_pv-power"
    assert sensor.native_value == 300
    assert sensor.available is True

    device_info = sensor.device_info
    assert device_info["identifiers"] == {(DOMAIN, "inverter_test_entry")}
    assert device_info["model"] == "TestInverter"
    assert device_info["manufacturer"] == "Testinverter"
    assert device_info["name"] == "Solar Inverter"
