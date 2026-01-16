"""Test the Jullix sensor platform."""
# ruff: noqa: SLF001

from datetime import timedelta
from unittest.mock import AsyncMock, patch

from custom_components.jullix.const import BATTERY_ENERGY_SENSORS, DOMAIN
from custom_components.jullix.sensor import (
    BatteryEnergySensor,
    JullixSensor,
    JullixSensorEntityDescription,
)
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


async def test_battery_energy_sensor_initialization():
    """Test battery energy sensor initialization."""
    coordinator = AsyncMock()
    coordinator.data = {
        "inverter": {
            "data": {"battery_power": 0},
            "model": "TestInverter",
            "desc": "Test Battery",
            "running": True,
        }
    }
    coordinator.config_entry = AsyncMock()
    coordinator.config_entry.entry_id = "test_entry"

    # Test charged sensor
    charged_desc = BATTERY_ENERGY_SENSORS[0]
    sensor = BatteryEnergySensor(coordinator, charged_desc)

    assert sensor.unique_id == "test_entry_battery_energy_charged"
    assert sensor.native_value == 0.0
    assert sensor.native_unit_of_measurement == UnitOfEnergy.KILO_WATT_HOUR
    assert sensor._track_charging is True
    assert sensor.available is True


async def test_battery_energy_sensor_charging():
    """Test battery energy accumulation during charging."""
    coordinator = AsyncMock()
    coordinator.config_entry = AsyncMock()
    coordinator.config_entry.entry_id = "test_entry"
    coordinator.data = {
        "inverter": {
            "model": "TestInverter",
            "desc": "Test Battery",
            "running": True,
        }
    }

    charged_desc = BATTERY_ENERGY_SENSORS[0]
    sensor = BatteryEnergySensor(coordinator, charged_desc)

    # Mock async_write_ha_state to avoid hass requirement
    with patch.object(sensor, "async_write_ha_state"):
        # First update: negative power (charging at 2 kW) - initializes tracking
        coordinator.data = {
            "inverter": {
                "data": {"battery_power": -2.0},
                "running": True,
            }
        }
        sensor._handle_coordinator_update()

        # Second update: 1 hour later, still charging at 2 kW
        # This update will calculate: energy = 2 kW × 1 hour = 2 kWh
        with patch("custom_components.jullix.sensor.dt_util.utcnow") as mock_now:
            # Set time to 1 hour after initialization
            mock_now.return_value = sensor._last_update_time + timedelta(hours=1)
            sensor._handle_coordinator_update()

        # Energy should be 2 kW × 1 hour = 2 kWh
        assert sensor.native_value == 2.0


async def test_battery_energy_sensor_discharging():
    """Test battery energy accumulation during discharging."""
    coordinator = AsyncMock()
    coordinator.config_entry = AsyncMock()
    coordinator.config_entry.entry_id = "test_entry"
    coordinator.data = {
        "inverter": {
            "model": "TestInverter",
            "desc": "Test Battery",
            "running": True,
        }
    }

    discharged_desc = BATTERY_ENERGY_SENSORS[1]
    sensor = BatteryEnergySensor(coordinator, discharged_desc)

    # Mock async_write_ha_state to avoid hass requirement
    with patch.object(sensor, "async_write_ha_state"):
        # First update: positive power (discharging at 1.5 kW) - initializes tracking
        coordinator.data = {
            "inverter": {
                "data": {"battery_power": 1.5},
                "running": True,
            }
        }
        sensor._handle_coordinator_update()

        # Second update: 30 minutes later, still discharging at 1.5 kW
        # This update will calculate: energy = 1.5 kW × 0.5 hours = 0.75 kWh
        with patch("custom_components.jullix.sensor.dt_util.utcnow") as mock_now:
            # Set time to 30 minutes after initialization
            mock_now.return_value = sensor._last_update_time + timedelta(minutes=30)
            sensor._handle_coordinator_update()

        # Energy should be 1.5 kW × 0.5 hours = 0.75 kWh
        assert sensor.native_value == 0.75


async def test_battery_energy_sensor_no_accumulation_wrong_direction():
    """Test that energy doesn't accumulate for wrong power direction."""
    coordinator = AsyncMock()
    coordinator.config_entry = AsyncMock()
    coordinator.config_entry.entry_id = "test_entry"
    coordinator.data = {
        "inverter": {
            "model": "TestInverter",
            "desc": "Test Battery",
            "running": True,
        }
    }

    # Test charged sensor with positive power (should not accumulate)
    charged_desc = BATTERY_ENERGY_SENSORS[0]
    sensor = BatteryEnergySensor(coordinator, charged_desc)

    # Mock async_write_ha_state to avoid hass requirement
    with patch.object(sensor, "async_write_ha_state"):
        # First update: positive power (discharging) - but we're tracking charging
        coordinator.data = {
            "inverter": {
                "data": {"battery_power": 2.0},  # Positive = discharging
                "running": True,
            }
        }
        sensor._handle_coordinator_update()

        # Second update: 1 hour later, still discharging
        with patch("custom_components.jullix.sensor.dt_util.utcnow") as mock_now:
            mock_now.return_value = sensor._last_update_time + timedelta(hours=1)
            sensor._handle_coordinator_update()

        # Should still be 0 since we're tracking charging but power is positive
        assert sensor.native_value == 0.0


async def test_battery_energy_sensor_unavailable():
    """Test battery energy sensor unavailability."""
    coordinator = AsyncMock()
    coordinator.config_entry = AsyncMock()
    coordinator.config_entry.entry_id = "test_entry"
    coordinator.last_update_success = True
    coordinator.data = {
        "inverter": {
            "model": "TestInverter",
            "desc": "Test Battery",
            "running": True,
        }
    }

    charged_desc = BATTERY_ENERGY_SENSORS[0]
    sensor = BatteryEnergySensor(coordinator, charged_desc)

    # Inverter not running
    coordinator.data = {
        "inverter": {
            "data": {"battery_power": -2.0},
            "running": False,
        }
    }

    assert sensor.available is False


async def test_battery_energy_sensor_state_restoration():
    """Test battery energy sensor state restoration."""
    coordinator = AsyncMock()
    coordinator.config_entry = AsyncMock()
    coordinator.config_entry.entry_id = "test_entry"
    coordinator.data = {
        "inverter": {
            "model": "TestInverter",
            "desc": "Test Battery",
            "running": True,
        }
    }

    charged_desc = BATTERY_ENERGY_SENSORS[0]
    sensor = BatteryEnergySensor(coordinator, charged_desc)

    # Mock restored state
    mock_sensor_data = AsyncMock()
    mock_sensor_data.native_value = 15.5

    with patch.object(sensor, "async_get_last_sensor_data", return_value=mock_sensor_data):
        await sensor.async_added_to_hass()

    # Should restore the previous total
    assert sensor._total_energy == 15.5
    assert sensor.native_value == 15.5
