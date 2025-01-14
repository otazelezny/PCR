import time
from temperature import load_config, init_temp_sensors, read_temperatures
from heaters import init_heaters, update_heater, PID
from machine import PWM, Pin

CONFIG_FILE = "config/config.json"


# Initialize fans
def init_fan(config):
    """
    Initialize the fan from the configuration.
    """
    fan_config = config.get("fan")
    if not fan_config or not fan_config.get("enabled", False):
        print("Fan is disabled or not configured.")
        return None

    try:
        pwm = PWM(Pin(fan_config["pin"]))
        pwm.freq(fan_config["frequency"])
        fan = {
            "pwm": pwm,
            "max_power": fan_config.get("max_power", 100)  # Store max_power separately
        }
        print(f"Initialized fan: {fan_config['name']} on pin {fan_config['pin']}")
        return fan
    except Exception as e:
        print(f"Error initializing fan: {e}")
        return None

# Turn off all heaters
def disable_heaters(heaters):
    """
    Turn off all heaters.
    """
    if not heaters:
        return
    for heater in heaters.values():
        try:
            heater["pwm"].duty_u16(0)  # Set PWM duty cycle to 0
            print(f"Heater {heater['name']} turned off.")
        except Exception as e:
            print(f"Error disabling heater {heater['name']}: {e}")

# Set fan speed
def set_fan_speed(fan, speed_percentage):
    """
    Set the fan speed as a percentage (0-100%), respecting max_power.
    """
    if fan is None:
        print("Fan is not initialized. Skipping fan control.")
        return  # Skip if fan is not initialized

    pwm = fan["pwm"]
    max_power = fan.get("max_power", 100)  # Default to 100%
    speed_percentage = min(speed_percentage, max_power)  # Cap to max_power

    try:
        duty = int((speed_percentage / 100.0) * 65535)  # Scale to 16-bit resolution
        pwm.duty_u16(duty)
        print(f"Fan speed set to {speed_percentage:.2f}%.")
    except Exception as e:
        print(f"Error setting fan speed: {e}")

# Safety mode: wait until resolved
def enter_safety_mode(fan, heaters):
    """
    Enter safety mode: Turn on the fan at full power and disable all heaters.
    Wait indefinitely until the system is manually reset or stopped.
    """
    print("Entering safety mode. All heaters are disabled, and the fan is running at full power.")
    set_fan_speed(fan, 100)  # Ensure fan is running at full power
    disable_heaters(heaters)  # Ensure all heaters are turned off

    try:
        while True:
            print("System in safety mode. Please resolve the issue and restart the machine.")
            time.sleep(5)  # Periodic message and ensure the system stays stable
    except KeyboardInterrupt:
        print("Safety mode interrupted. System requires manual intervention to restart.")

def run_cycle(heaters, sensors, fan, cycle_name, cycle_config):
    """
    Runs a single heating cycle for the given heaters based on the cycle configuration.
    """
    target_temp = cycle_config["target_temp"]
    duration = cycle_config["time"]
    pid_kp = cycle_config["pid_kp"]
    pid_ki = cycle_config["pid_ki"]
    pid_kd = cycle_config["pid_kd"]

    # Update the PID controller with the cycle's PID parameters for each heater
    for heater in heaters.values():
        heater["pid"] = PID(kp=pid_kp, ki=pid_ki, kd=pid_kd, setpoint=target_temp)

    start_time = time.time()
    elapsed_time = 0
    temp_reached = False  # Flag to ensure the temperature reaches the target

    print(f"Starting {cycle_name}: Target Temp = {target_temp}°C, Duration = {duration}s")

    try:
        while elapsed_time < duration or not temp_reached:
            # Read temperatures
            temperatures = read_temperatures(sensors)

            # Update heater and fan control
            for sensor_name, current_temp in temperatures.items():
                if current_temp is not None:
                    for heater in heaters.values():
                        output = update_heater(heater, current_temp)  # Update heater power
                        print(
                            f"[{cycle_name}] {sensor_name}: {current_temp:.2f}°C | Heater {heater['name']} Output: {output:.2f}%"
                        )
                        if current_temp >= target_temp:
                            temp_reached = True

                    # Adjust fan speed for fine temperature control
                    if current_temp > target_temp:
                        set_fan_speed(fan, 80)  # High speed for cooling
                    elif current_temp >= target_temp - 5:
                        set_fan_speed(fan, 30)  # Low speed for stabilization
                    else:
                        set_fan_speed(fan, 0)  # Turn off fan during normal heating

                else:
                    raise RuntimeError(f"Error reading temperature from {sensor_name}")

            elapsed_time = time.time() - start_time
            time.sleep(1)
    except Exception as e:
        print(f"Error during {cycle_name}: {e}")
        print("Activating safety features...")
        enter_safety_mode(fan, heaters)  # Enter safety mode

    print(f"{cycle_name} completed. Holding for next cycle...")
    set_fan_speed(fan, 0)  # Turn off fan after cycle completion


if __name__ == "__main__":
    heaters = None
    fan = None
    sensors = None

    try:
        config = load_config(CONFIG_FILE)

        if config:
            # Initialize temperature sensors, heaters, and fan
            sensors = init_temp_sensors(config)
            heaters = init_heaters(config)
            fan = init_fan(config)

            if not sensors:
                print("Error: No temperature sensors initialized.")
                raise RuntimeError("Initialization failed: No sensors")

            if not heaters:
                print("Error: No heaters initialized.")
                raise RuntimeError("Initialization failed: No heaters")

            # Get cycle configuration
            cycles = config.get("Cycles", {})
            cycle_count = config.get("cycles_count", 1)  # Default to 1 cycle

            if not cycles:
                print("Error: No cycles defined in configuration.")
                raise RuntimeError("No cycles defined")

            print(f"Running {cycle_count} heating cycle(s)...")

            # Execute the cycles for the specified count
            for cycle_iteration in range(1, cycle_count + 1):
                print(f"\n=== Cycle {cycle_iteration}/{cycle_count} ===")
                for cycle_name, cycle_config in cycles.items():
                    run_cycle(heaters, sensors, fan, cycle_name, cycle_config)

            print("All cycles completed. Turning off heaters.")
    except Exception as e:
        print(f"Critical error: {e}")
        if fan or heaters:
            print("Activating safety features.")
            enter_safety_mode(fan, heaters)  # Enter safety mode
    finally:
        print("Program terminated. Turning off heaters and fan.")
        disable_heaters(heaters)
        if fan:
            try:
                fan["pwm"].duty_u16(0)  # Turn off the fan
                print("Fan turned off.")
            except Exception as e:
                print(f"Error turning off fan: {e}")