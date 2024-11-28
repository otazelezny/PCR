import json


# Load configuration
def load_config(file_path):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return None

# Initialize temperature sensors
def init_temp_sensors(config):
    sensors = {}
    for key, sensor in config.items():
        sensors[key] = {
            "name": sensor["name"],
            "frequency": sensor["frequency"],
            "pin": sensor["pin"]
        }
    return sensors

# Initialize heaters
def init_heaters(config):
    heaters = {}
    for key, heater in config.items():
        heaters[key] = {
            "name": heater["name"],
            "frequency": heater["frequency"],
            "pin": heater["pin"],
            "max_temp": heater["max_temperature"]
        }
    return heaters

# Initialize fan
def init_fan(config):
    fan = {
        "name": config["name"],
        "frequency": config["frequency"],
        "pin": config["pin"],
        "max_speed": config["max_speed"]
    }
    return fan

# Main setup function
def setup_thermocycler(config):
    temp_sensors = init_temp_sensors(config["temperature_sensors"])
    heaters = init_heaters(config["heaters"])
    fan = init_fan(config["fan"])
    safety_limits = config["safety_limits"]

    print("Thermocycler initialized!")
    print("Temperature Sensors:", [sensor["name"] for sensor in temp_sensors.values()])
    print("Heaters:", [heater["name"] for heater in heaters.values()])
    print("Fan:", fan["name"])
    return temp_sensors, heaters, fan, safety_limits

# Mock temperature reading function
def read_temp(sensor):
    # Simulate a temperature value based on sensor pin
    import random
    return random.uniform(20.0, 100.0)  # Simulate a temperature reading

# Example usage
if __name__ == "__main__":
    config_path = "config.json"
    print(f"Looking for config file at: {config_path}")
    config = load_config(config_path)

    if config:
        temp_sensors, heaters, fan, safety_limits = setup_thermocycler(config)

        # Example loop to read sensors and simulate control
        try:
            while True:
                for key, sensor in temp_sensors.items():
                    temperature = read_temp(sensor)
                    print(f"{sensor['name']} Temperature: {temperature:.2f}°C")
                
                # Add logic to control heaters and fan based on temperature readings
                # Example placeholder logic:
                for heater in heaters.values():
                    print(f"Controlling {heater['name']} on pin {heater['pin']}")

                print(f"Fan {fan['name']} running at frequency {fan['frequency']} Hz")
                print("Safety limits:", safety_limits)

                import time
                time.sleep()  # Delay for readability
        except KeyboardInterrupt:
            print("Thermocycler simulation stopped.")
            