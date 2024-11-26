import json
import os


# Load configuration file
def load_config(file_path):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except OSError as e:
        print(f"Error: Cannot open config file '{file_path}': {e}")
        return None
    except ValueError as e:
        print(f"Error: Invalid JSON format in config file '{file_path}': {e}")
        return None

# Initialize temperature sensors
def init_temp_sensors(config):
    sensors = {}
    if "temperature_sensors" not in config:
        print("Error: 'temperature_sensors' section is missing in config.json")
        return sensors
    for key, sensor in config["temperature_sensors"].items():
        sensors[key] = {
            "name": sensor["name"],
            "frequency": sensor["frequency"],
            "pin": sensor["pin"]
        }
    return sensors

# Initialize heaters
def init_heaters(config):
    heaters = {}
    if "heaters" not in config:
        print("Error: 'heaters' section is missing in config.json")
        return heaters
    for key, heater in config["heaters"].items():
        heaters[key] = {
            "name": heater["name"],
            "frequency": heater["frequency"],
            "pin": heater["pin"],
            "max_temp": heater["max_temperature"]
        }
    return heaters

# Initialize fan
def init_fan(config):
    if "fan" not in config:
        print("Error: 'fan' section is missing in config.json")
        return None
    return {
        "name": config["fan"]["name"],
        "frequency": config["fan"]["frequency"],
        "pin": config["fan"]["pin"],
        "max_speed": config["fan"]["max_speed"]
    }

# Main setup function
def setup_thermocycler(config):
    temp_sensors = init_temp_sensors(config)
    heaters = init_heaters(config)
    fan = init_fan(config)
    safety_limits = config.get("safety_limits", {})
    
    if not temp_sensors or not heaters or not fan:
        print("Error: Initialization failed due to missing configuration sections.")
        return None, None, None, None

    print("Thermocycler initialized!")
    print("Temperature Sensors:", [sensor["name"] for sensor in temp_sensors.values()])
    print("Heaters:", [heater["name"] for heater in heaters.values()])
    print("Fan:", fan["name"])
    return temp_sensors, heaters, fan, safety_limits

# Simulated temperature reading function
def read_temp(sensor):
    import random
    return random.uniform(20.0, 100.0)  # Simulate a temperature reading

# Main execution
if __name__ == "__main__":
    CONFIG_FILE = "config.json"

    # Check if file exists in MicroPython environment
    if CONFIG_FILE not in os.listdir():
        print(f"Error: Configuration file '{CONFIG_FILE}' not found in the filesystem.")
    else:
        config = load_config(CONFIG_FILE)

        if config:
            temp_sensors, heaters, fan, safety_limits = setup_thermocycler(config)

            if temp_sensors and heaters and fan:
                try:
                    while True:
                        for key, sensor in temp_sensors.items():
                            temperature = read_temp(sensor)
                            print(f"{sensor['name']} Temperature: {temperature:.2f}°C")
                        
                        # Add your logic for heater and fan control
                        for heater in heaters.values():
                            print(f"Controlling {heater['name']} on pin {heater['pin']}")

                        print(f"Fan {fan['name']} running at frequency {fan['frequency']} Hz")
                        print("Safety limits:", safety_limits)

                        import time
                        time.sleep(1)  # Delay for readability
                except KeyboardInterrupt:
                    print("Thermocycler simulation stopped.")