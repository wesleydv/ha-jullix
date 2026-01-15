"""Tests for Jullix constants and entity descriptions."""

from custom_components.jullix.const import (
    DSMR_BINARY_SENSORS,
    DSMR_SENSORS,
    INVERTER_BINARY_SENSORS,
    INVERTER_SENSORS,
)


def test_sensor_descriptions():
    """Test that sensor descriptions are defined."""
    assert len(DSMR_SENSORS) == 6
    assert len(INVERTER_SENSORS) == 11

    # Check DSMR sensors have required attributes
    for desc in DSMR_SENSORS:
        assert desc.key is not None
        assert desc.name is not None
        assert desc.translation_key is not None


def test_binary_sensor_descriptions():
    """Test that binary sensor descriptions are defined."""
    assert len(DSMR_BINARY_SENSORS) == 2
    assert len(INVERTER_BINARY_SENSORS) == 6

    # Check binary sensors have required attributes
    for desc in DSMR_BINARY_SENSORS:
        assert desc.key is not None
        assert desc.name is not None


def test_energy_sensors_have_correct_classes():
    """Test that energy sensors have the correct device and state classes."""
    energy_sensors = [s for s in DSMR_SENSORS if "energy" in s.key]
    assert len(energy_sensors) == 2

    for sensor in energy_sensors:
        assert sensor.device_class is not None
        assert sensor.state_class is not None
