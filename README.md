# Jullix Energy Management (Local) Integration for Home Assistant

Local custom integration for the Jullix energy management system that connects directly to your Jullix device via HTTP API to expose utility meter (DSMR) data and solar/battery inverter data as Home Assistant entities.

> **Note:** This integration communicates with your Jullix device over your local network. It does not use any cloud API or external services.

## Features

- **DSMR Smart Meter Monitoring**
  - Grid power consumption
  - Energy import/export tracking
  - Gas and water consumption
  - Meter connectivity status

- **Solar Inverter & Battery Monitoring**
  - Real-time power generation and consumption
  - Battery state of charge (SOC)
  - Battery charging/discharging status
  - Voltage and current measurements
  - System status indicators

- **Energy Dashboard Integration**
  - All sensors properly configured for HA Energy Dashboard
  - Track solar production, grid consumption, and battery usage
  - Compatible with utility_meter for daily/monthly tracking

## Installation

### Method 1: Git Clone (Recommended)

Clone directly into your Home Assistant custom_components directory:

```bash
cd /config/custom_components
git clone https://github.com/wesleydv/ha-jullix.git jullix
```

Then restart Home Assistant and add the integration via UI:
- Go to Settings → Devices & Services
- Click "+ Add Integration"
- Search for "Jullix Energy Management (Local)"
- Enter your Jullix device's local IP address

### Method 2: Manual Download

1. Download the latest release from GitHub
2. Extract and copy the `jullix` folder to `/config/custom_components/jullix/`
3. Restart Home Assistant
4. Add the integration via UI as described above

### Method 3: HACS (when available)

This integration can be added to HACS as a custom repository.

## Configuration

The integration is configured through the Home Assistant UI:

1. **Host**: Local IP address of your Jullix device

The integration will automatically:
- Test the connection to both API endpoints
- Create two devices (Smart Meter and Inverter)
- Set up all available sensors and binary sensors
- Start polling data every 10 seconds

## Entities Created

### Smart Meter Device

**Sensors:**
- `sensor.jullix_grid_power` - Current grid power (kW)
- `sensor.jullix_energy_import` - Total energy imported (kWh)
- `sensor.jullix_energy_export` - Total energy exported (kWh)
- `sensor.jullix_gas` - Total gas consumption (m³)
- `sensor.jullix_water` - Total water consumption (m³)
- `sensor.jullix_meter_id` - Meter identification (disabled by default)

**Binary Sensors:**
- `binary_sensor.jullix_meter_connected` - Meter connectivity status
- `binary_sensor.jullix_meter_enabled` - Meter enabled status

### Inverter/Battery Device

**Sensors:**
- `sensor.jullix_inverter_voltage_l1` - Line voltage (V)
- `sensor.jullix_inverter_current_l1` - Line current (A)
- `sensor.jullix_battery_power` - Battery power (W, negative=charging, positive=discharging)
- `sensor.jullix_battery_voltage` - Battery voltage (V)
- `sensor.jullix_battery_current` - Battery current (A)
- `sensor.jullix_battery_level` - Battery state of charge (%)
- `sensor.jullix_solar_energy_produced` - Total solar production (kWh)
- `sensor.jullix_house_energy_consumed` - Total house consumption (kWh)
- `sensor.jullix_inverter_power` - Current inverter power (kW)
- `sensor.jullix_pv_power` - Current PV generation (kW)
- `sensor.jullix_grid_power` - Grid power from inverter (kW)

**Binary Sensors:**
- `binary_sensor.jullix_inverter_ready` - Inverter ready status
- `binary_sensor.jullix_battery_low` - Low battery warning
- `binary_sensor.jullix_comm_fail` - Communication failure indicator
- `binary_sensor.jullix_dsmr_fail` - DSMR communication failure
- `binary_sensor.jullix_battery_charging` - Battery charging status
- `binary_sensor.jullix_battery_discharging` - Battery discharging status

## Energy Dashboard Setup

To use with Home Assistant's Energy Dashboard:

1. Go to Settings → Dashboards → Energy
2. Configure the following:

**Electricity Grid:**
- Grid consumption: `sensor.jullix_energy_import`
- Return to grid: `sensor.jullix_energy_export`

**Solar Panels:**
- Solar production: `sensor.jullix_solar_energy_produced`

**Gas Consumption:**
- Gas consumption: `sensor.jullix_gas`

## Advanced Usage

### Creating Utility Meters

Track daily/monthly consumption:

```yaml
utility_meter:
  daily_energy_import:
    source: sensor.jullix_energy_import
    cycle: daily

  daily_solar_production:
    source: sensor.jullix_solar_energy_produced
    cycle: daily

  monthly_gas:
    source: sensor.jullix_gas
    cycle: monthly
```

## Technical Details

- **Communication**: Local HTTP API (no authentication required)
- **Polling Interval**: 10 seconds
- **API Endpoints**:
  - `/api/dsmr/status` - Smart meter data
  - `/api/inverter/status/A` - Inverter/battery data
- **Quality Scale**: Bronze level compliant

## Support

For issues and feature requests, please open an issue on the GitHub repository.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
