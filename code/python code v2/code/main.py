# code/main.py
import time
from machine import Pin, PWM
from config.config_loader import load_config
from sensors import init_sensors
from logger import create_log_file
from cycle_control import run_cycles

from heater import set_heater_power
from fan import set_fan_speed

def initialize_heaters(heater_config):
    """
    Initializes heaters by creating PWM objects for each enabled heater.
    """
    heaters = {}
    for key, conf in heater_config.items():
        if conf.get("enabled", False):
            pin = conf.get("pin")
            pwm = PWM(Pin(pin))
            pwm.freq(conf.get("frequency", 50))
            conf["pwm"] = pwm
            heaters[key] = conf
    return heaters

def initialize_fan(fan_config):
    """
    Initializes the fan by creating a PWM object if enabled.
    """
    if fan_config.get("enabled", False):
        pin = fan_config.get("pin")
        pwm = PWM(Pin(pin))
        pwm.freq(fan_config.get("frequency", 1500))
        fan_config["pwm"] = pwm
        return fan_config
    return fan_config

def initialize():
    """
    Loads the config and initializes sensors, heaters, fan, and logging.
    """
    config = load_config("/config/config.json")
    sensors = init_sensors(config["temperature_sensors"])
    heaters = initialize_heaters(config["heaters"])
    fan = initialize_fan(config["fan"])
    log_filename = create_log_file()
    return config, sensors, heaters, fan, log_filename

def main():
    config, sensors, heaters, fan, log_filename = initialize()
    
    print("Press Enter to start the PCR cycles...")
    input()
    
    run_cycles(config, sensors, heaters, fan, log_filename)
    
    print("PCR Thermocycler process complete.")

if __name__ == "__main__":
    main()