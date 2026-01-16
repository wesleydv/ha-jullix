"""Constants for the Jullix Energy Management integration."""

from datetime import timedelta
from typing import Final

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntityDescription,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfVolume,
)

DOMAIN: Final = "jullix"

# Configuration
CONF_HOST: Final = "host"
DEFAULT_SCAN_INTERVAL: Final = timedelta(seconds=10)

# API Endpoints
API_DSMR_STATUS: Final = "/api/dsmr/status"
API_INVERTER_STATUS: Final = "/api/inverter/status/A"

# Timeout
API_TIMEOUT: Final = 10

# Device identifiers
DEVICE_METER: Final = "meter"
DEVICE_INVERTER: Final = "inverter"

# DSMR Sensor Descriptions
DSMR_SENSORS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="power",
        translation_key="grid_power",
        name="Grid power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        suggested_display_precision=3,
    ),
    SensorEntityDescription(
        key="energy-in",
        translation_key="energy_import",
        name="Energy import",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=2,
    ),
    SensorEntityDescription(
        key="energy-out",
        translation_key="energy_export",
        name="Energy export",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=2,
    ),
    SensorEntityDescription(
        key="gas",
        translation_key="gas",
        name="Gas consumption",
        device_class=SensorDeviceClass.GAS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfVolume.CUBIC_METERS,
        suggested_display_precision=2,
    ),
    SensorEntityDescription(
        key="water",
        translation_key="water",
        name="Water consumption",
        device_class=SensorDeviceClass.WATER,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfVolume.CUBIC_METERS,
        suggested_display_precision=2,
    ),
    SensorEntityDescription(
        key="id",
        translation_key="meter_id",
        name="Meter ID",
        entity_registry_enabled_default=False,
    ),
)

# DSMR Binary Sensor Descriptions
DSMR_BINARY_SENSORS: tuple[BinarySensorEntityDescription, ...] = (
    BinarySensorEntityDescription(
        key="connected",
        translation_key="meter_connected",
        name="Meter connected",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
    BinarySensorEntityDescription(
        key="enabled",
        translation_key="meter_enabled",
        name="Meter enabled",
    ),
)

# Inverter Sensor Descriptions
INVERTER_SENSORS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="voltage_l1",
        translation_key="inverter_voltage_l1",
        name="Voltage L1",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="current_l1",
        translation_key="inverter_current_l1",
        name="Current L1",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=2,
    ),
    SensorEntityDescription(
        key="battery_power",
        translation_key="battery_power",
        name="Battery power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        suggested_display_precision=2,
    ),
    SensorEntityDescription(
        key="battery_voltage",
        translation_key="battery_voltage",
        name="Battery voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="battery_current",
        translation_key="battery_current",
        name="Battery current",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=2,
    ),
    SensorEntityDescription(
        key="battery_SOC",
        translation_key="battery_soc",
        name="Battery level",
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="energy_produced",
        translation_key="solar_production",
        name="Solar energy produced",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="energy_consumed",
        translation_key="house_consumption",
        name="House energy consumed",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="power",
        translation_key="inverter_power",
        name="Inverter power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        suggested_display_precision=2,
    ),
    SensorEntityDescription(
        key="pv_power",
        translation_key="pv_power",
        name="PV power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        suggested_display_precision=2,
    ),
    SensorEntityDescription(
        key="gridpower",
        translation_key="grid_power_inverter",
        name="Grid power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        suggested_display_precision=2,
    ),
)

# Inverter Binary Sensor Descriptions
INVERTER_BINARY_SENSORS: tuple[BinarySensorEntityDescription, ...] = (
    BinarySensorEntityDescription(
        key="ready",
        translation_key="inverter_ready",
        name="Inverter ready",
    ),
    BinarySensorEntityDescription(
        key="low_battery",
        translation_key="battery_low",
        name="Battery low",
        device_class=BinarySensorDeviceClass.BATTERY,
    ),
    BinarySensorEntityDescription(
        key="comm_fail",
        translation_key="comm_fail",
        name="Communication failure",
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    BinarySensorEntityDescription(
        key="dsmr_fail",
        translation_key="dsmr_fail",
        name="DSMR failure",
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    BinarySensorEntityDescription(
        key="charging",
        translation_key="battery_charging",
        name="Battery charging",
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
    ),
    BinarySensorEntityDescription(
        key="discharging",
        translation_key="battery_discharging",
        name="Battery discharging",
    ),
)
