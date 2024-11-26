import json
from machine import ADC, Pin

# Load configuration
def load_config(file_path):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except OSError as e:
        print(f"Error loading config file '{file_path}': {e}")
        return None
    except ValueError as e:
        print(f"Error parsing JSON in config file '{file_path}': {e}")
        return None

# Initialize temperature sensors
def init_temp_sensors(config):
    sensors = {}
    if "temperature_sensors" not in config:
        print("Error: 'temperature_sensors' section is missing in configuration.")
        return sensors

    for key, sensor in config["temperature_sensors"].items():
        if not sensor.get("enabled", False):
            print(f"Sensor {sensor['name']} is disabled. Skipping initialization.")
            continue
        try:
            adc = ADC(Pin(sensor["pin"]))  # Initialize ADC for the pin
            sensors[key] = {
                "name": sensor["name"],
                "adc": adc,
                "resistor_value": sensor["resistor_value"]
            }
            print(f"Initialized sensor: {sensor['name']} on pin {sensor['pin']}")
        except Exception as e:
            print(f"Error initializing sensor {sensor['name']}: {e}")
    return sensors

# Calculate temperature
def calculate_temperature(raw_value, resistor_value):
    V_REF = 3.3  # Reference voltage
    adc_voltage = (raw_value / 4095) * V_REF
    thermistor_resistance = resistor_value * (V_REF / adc_voltage - 1)
    temperature = 25 + (thermistor_resistance / 1000)  # Placeholder formula
    return temperature

# Read temperatures from sensors
def read_temperatures(sensors):
    temperatures = {}
    for key, sensor in sensors.items():
        try:
            raw_value = sensor["adc"].read()
            resistor_value = sensor["resistor_value"]
            temperature = calculate_temperature(raw_value, resistor_value)
            temperatures[sensor["name"]] = temperature
        except Exception as e:
            print(f"Error reading sensor {sensor['name']}: {e}")
            temperatures[sensor["name"]] = None
    return temperatures