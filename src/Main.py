import os
import time
from temperature import load_config, init_temp_sensors, read_temperatures

CONFIG_FILE = "config.json"

if __name__ == "__main__":
    if CONFIG_FILE not in os.listdir():
        print(f"Error: Configuration file '{CONFIG_FILE}' not found.")
    else:
        config = load_config(CONFIG_FILE)

        if config:
            # Initialize temperature sensors
            temp_sensors = init_temp_sensors(config)

            # Check fan and heaters status
            fan_enabled = config["fan"].get("enabled", False)
            heaters_enabled = {
                key: heater.get("enabled", False) for key, heater in config["heaters"].items()
            }

            if temp_sensors:
                print("Temperature sensors initialized.")

                try:
                    while True:
                        # Read temperatures
                        temperatures = read_temperatures(temp_sensors)
                        for name, temp in temperatures.items():
                            if temp is not None:
                                print(f"{name}: {temp:.2f}°C")
                            else:
                                print(f"{name}: Error reading temperature")

                        # Control fan
                        if fan_enabled:
                            print(f"Fan is enabled and running.")

                        # Control heaters
                        for heater_name, enabled in heaters_enabled.items():
                            if enabled:
                                print(f"Heater {heater_name} is enabled.")

                        time.sleep(1)  # Delay for readability
                except KeyboardInterrupt:
                    print("Program stopped.")