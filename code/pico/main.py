import time
from temperature import load_config, init_temp_sensors, read_temperatures
from heaters import init_heaters, update_heater, PID

CONFIG_FILE = "config/config.json"


def run_cycle(heater, sensors, cycle_name, cycle_config):
    """
    Runs a single heating cycle for the given heater based on the cycle configuration.
    """
    target_temp = cycle_config["target_temp"]
    duration = cycle_config["time"]
    pid_kp = cycle_config["pid_kp"]
    pid_ki = cycle_config["pid_ki"]
    pid_kd = cycle_config["pid_kd"]

    # Update the PID controller with the cycle's PID parameters
    heater["pid"] = PID(kp=pid_kp, ki=pid_ki, kd=pid_kd, setpoint=target_temp)

    start_time = time.time()
    elapsed_time = 0

    print(f"Starting {cycle_name}: Target Temp = {target_temp}°C, Duration = {duration}s")

    while elapsed_time < duration:
        # Read temperatures
        temperatures = read_temperatures(sensors)

        # Update heater control
        for sensor_name, current_temp in temperatures.items():
            if current_temp is not None:
                output = update_heater(heater, current_temp)
                print(
                    f"[{cycle_name}] {sensor_name}: {current_temp:.2f}°C | Heater Output: {output:.2f}%"
                )
            else:
                print(f"[{cycle_name}] {sensor_name}: Error reading temperature.")

        elapsed_time = time.time() - start_time
        time.sleep(1)

    print(f"{cycle_name} completed. Holding for next cycle...")


if __name__ == "__main__":
    # Load configuration file
    config = load_config(CONFIG_FILE)

    if config:
        # Initialize temperature sensors and heaters
        sensors = init_temp_sensors(config)
        heaters = init_heaters(config)

        if not sensors:
            print("Error: No temperature sensors initialized.")
            exit(1)

        if not heaters:
            print("Error: No heaters initialized.")
            exit(1)

        # Get cycle configuration
        cycles = config.get("Cycles", {})
        cycle_count = config.get("cycle_count", 1)  # Default to 1 cycle

        if not cycles:
            print("Error: No cycles defined in configuration.")
            exit(1)

        heater = heaters.get("heater_1")  # Using the first heater as an example

        if not heater:
            print("Error: No active heater found.")
            exit(1)

        print(f"Running {cycle_count} heating cycle(s)...")

        # Execute the cycles for the specified count
        for cycle_iteration in range(1, cycle_count + 1):
            print(f"\n=== Cycle {cycle_iteration}/{cycle_count} ===")
            for cycle_name, cycle_config in cycles.items():
                try:
                    run_cycle(heater, sensors, cycle_name, cycle_config)
                except Exception as e:
                    print(f"Error during {cycle_name}: {e}")

        print("All cycles completed.")
    else:
        print("Error: Failed to load configuration.")