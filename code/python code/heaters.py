import json
from machine import Pin, PWM

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

class PID:
    def __init__(self, kp, ki, kd, setpoint):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.prev_error = 0
        self.integral = 0

    def compute(self, current_value):
        """
        Compute the PID output.
        """
        error = self.setpoint - current_value
        self.integral += error
        derivative = error - self.prev_error
        self.prev_error = error
        return (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)

# Initialize heaters
def init_heaters(config):
    heaters = {}
    if "heaters" not in config:
        print("Error: 'heaters' section is missing in configuration.")
        return heaters

    for key, heater in config["heaters"].items():
        if not heater.get("enabled", False):
            print(f"Heater {heater['name']} is disabled. Skipping initialization.")
            continue
        try:
            pwm = PWM(Pin(heater["pin"]))  # Initialize PWM on the specified pin
            pwm.freq(heater["frequency"])  # Set PWM frequency
            heaters[key] = {
                "name": heater["name"],
                "pwm": pwm,
                "max_temperature": heater["max_temperature"],
                "pid": PID(kp=1.0, ki=0.1, kd=0.01, setpoint=0),  # Default PID values
            }
            print(f"Initialized heater: {heater['name']} on pin {heater['pin']}")
        except Exception as e:
            print(f"Error initializing heater {heater['name']}: {e}")
    return heaters

# Update heater output using PID
def update_heater(heater, current_temperature):
    pid = heater["pid"]
    pwm = heater["pwm"]
    max_temperature = heater["max_temperature"]
    max_power = heater.get("max_power", 100)  # Default to 100%

    # Compute PID output
    output = pid.compute(current_temperature)

    # Limit the power to max_power percentage
    output = min(output, max_power)

    # Scale the output to 16-bit PWM range (0-65535)
    output_u16 = int((output / 100.0) * 65535)

    # Turn off heater if above max_temperature
    if current_temperature > max_temperature:
        output_u16 = 0
        print(f"Warning: {heater['name']} temperature exceeds maximum. Heater turned off.")

    pwm.duty_u16(output_u16)  # Set PWM duty cycle
    return output