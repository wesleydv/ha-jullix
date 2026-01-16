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
- `sensor.jullix_battery_power` - Battery power (kW, negative=charging, positive=discharging)
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

### Required: Battery Energy Tracking

The Jullix API doesn't provide cumulative battery charge/discharge totals, so you need to create these using Home Assistant helpers.

#### Step 1: Create Integral Sensor Helper

1. Go to **Settings → Devices & Services → Helpers**
2. Click **+ Create Helper** → **Integral sensor**
3. Configure the following fields in order:
   - **Name**: `Battery Energy Total`
   - **Unit prefix**: None (since power is already in kW)
   - **Time unit**: hour
   - **Input sensor**: Your battery power sensor (e.g., `sensor.sofar_hyd_4000_ep_battery_power`)
   - **Integration method**: Left Riemann sum
   - **Precision**: 2
   - **Max sub interval**: Leave at default (0)
4. Click **Submit**

#### Step 2: Create Template Sensors

Go to **Settings → Devices & Services → Helpers** and create two template sensors:

**Battery Energy Charged:**
1. Click **+ Create Helper** → **Template** → **Template a sensor**
2. Configure:
   - **Name**: `Battery Energy Charged`
   - **State template**:
     ```jinja
     {% set power = states('sensor.YOUR_DEVICE_battery_power')|float(0) %}
     {% set total = states('sensor.battery_energy_total')|float(0)|abs %}
     {% if power < 0 %}
       {{ total }}
     {% else %}
       {{ this.state if this is defined and this.state not in ['unknown', 'unavailable', 'none', None] else 0 }}
     {% endif %}
     ```
   - **Unit of measurement**: `kWh`
   - **Device class**: Select "Energy" from the dropdown
   - **State class**: Select "Total increasing" from the dropdown

**Battery Energy Discharged:**
1. Click **+ Create Helper** → **Template** → **Template a sensor**
2. Configure:
   - **Name**: `Battery Energy Discharged`
   - **State template**:
     ```jinja
     {% set power = states('sensor.YOUR_DEVICE_battery_power')|float(0) %}
     {% set total = states('sensor.battery_energy_total')|float(0)|abs %}
     {% if power > 0 %}
       {{ total }}
     {% else %}
       {{ this.state if this is defined and this.state not in ['unknown', 'unavailable', 'none', None] else 0 }}
     {% endif %}
     ```
   - **Unit of measurement**: `kWh`
   - **Device class**: Select "Energy" from the dropdown
   - **State class**: Select "Total increasing" from the dropdown

**Note:** Replace `YOUR_DEVICE` with your actual inverter device name (e.g., `sofar_hyd_4000_ep`).

<details>
<summary>Alternative: YAML Configuration</summary>

If you prefer YAML, add this to your `configuration.yaml`:

```yaml
sensor:
  - platform: integration
    source: sensor.YOUR_DEVICE_battery_power
    name: battery_energy_total
    unit_prefix: none  # Power is already in kW, so kW × hour = kWh
    method: left

template:
  - sensor:
      - name: "Battery Energy Charged"
        unique_id: battery_energy_charged
        unit_of_measurement: "kWh"
        device_class: energy
        state_class: total_increasing
        state: >
          {% set power = states('sensor.YOUR_DEVICE_battery_power')|float(0) %}
          {% set total = states('sensor.battery_energy_total')|float(0)|abs %}
          {% if power < 0 %}
            {{ total }}
          {% else %}
            {{ this.state if this is defined and this.state not in ['unknown', 'unavailable', 'none', None] else 0 }}
          {% endif %}

      - name: "Battery Energy Discharged"
        unique_id: battery_energy_discharged
        unit_of_measurement: "kWh"
        device_class: energy
        state_class: total_increasing
        state: >
          {% set power = states('sensor.YOUR_DEVICE_battery_power')|float(0) %}
          {% set total = states('sensor.battery_energy_total')|float(0)|abs %}
          {% if power > 0 %}
            {{ total }}
          {% else %}
            {{ this.state if this is defined and this.state not in ['unknown', 'unavailable', 'none', None] else 0 }}
          {% endif %}
```

Then restart Home Assistant.
</details>

### Configure Energy Dashboard

1. Go to Settings → Dashboards → Energy
2. Configure the following:

**Electricity Grid:**
- Grid consumption: `sensor.jullix_energy_import`
- Return to grid: `sensor.jullix_energy_export`

**Solar Panels:**
- Solar production: `sensor.jullix_solar_energy_produced`

**Home Battery Storage:**
- Energy going in to the battery: `sensor.jullix_battery_energy_charged`
- Energy coming out of the battery: `sensor.jullix_battery_energy_discharged`

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
