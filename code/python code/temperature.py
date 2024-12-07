import math, json
from machine import ADC, Pin

# Constants for the thermistor
BETA = 3950  # Beta coefficient of the thermistor
R_NOMINAL = 100000  # Resistance at 25 degrees Celsius
T_NOMINAL = 22 + 273.15  # Reference temperature in Kelvin

# Load configuration
def load_config(file_path):
    """
    Load the configuration file from the filesystem.
    """
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
    """
    Initialize temperature sensors from the configuration.
    """
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
                "resistor_value": sensor["resistor_value"]  # Resistor value from config
            }
            print(f"Initialized sensor: {sensor['name']} on pin {sensor['pin']}")
        except Exception as e:
            print(f"Error initializing sensor {sensor['name']}: {e}")
    return sensors

# Read temperature using Steinhart-Hart equation
def read_temperature(adc, resistor_value):
    """
    Read temperature from the thermistor using Steinhart-Hart equation.
    """
    try:
        # Read the ADC value (16-bit ADC on Raspberry Pi Pico)
        adc_value = adc.read_u16()
        
        # Convert the ADC value to a voltage ratio (0.0 to 1.0)
        v_ratio = adc_value / 65535.0  # For 16-bit resolution

        # Calculate the resistance of the thermistor
        if v_ratio == 0:
            return None  # Avoid division by zero
        thermistor_resistance = (resistor_value * (1 - v_ratio)) / v_ratio

        # Apply the Steinhart-Hart equation to calculate temperature in Kelvin
        temperature_kelvin = 1 / (
            1 / T_NOMINAL + (1 / BETA) * math.log(thermistor_resistance / R_NOMINAL)
        )

        # Convert Kelvin to Celsius
        temperature_celsius = temperature_kelvin - 273.15
        return round(temperature_celsius, 2)
    except Exception as e:
        print(f"Error reading temperature: {e}")
        return None

# Read temperatures from all sensors
def read_temperatures(sensors):
    """
    Read temperatures from all initialized sensors.
    """
    temperatures = {}
    for key, sensor in sensors.items():
        try:
            adc = sensor["adc"]
            resistor_value = sensor["resistor_value"]  # Use resistor value from config
            temperature = read_temperature(adc, resistor_value)
            temperatures[sensor["name"]] = temperature
        except Exception as e:
            print(f"Error reading sensor {sensor['name']}: {e}")
            temperatures[sensor["name"]] = None
    return temperatures
