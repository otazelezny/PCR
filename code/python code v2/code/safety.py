# code/safety.py
from heater import stop_heater
from fan import stop_fan

def check_safety(temperatures, safety_limits, heaters, fan):
    """
    Checks if any sensor reading exceeds safety limits.
    If any temperature is above the maximum or emergency shutdown threshold, 
    an emergency shutdown is initiated.
    """
    max_temp = safety_limits.get("max_temperature", 120)
    emergency = safety_limits.get("emergency_shutdown", {})
    emergency_enabled = emergency.get("enabled", False)
    shutdown_threshold = emergency.get("temperature_threshold", max_temp)
    
    for sensor_name, temp in temperatures.items():
        if temp > max_temp:
            print("Temperature {} exceeds max limit {}! Initiating emergency shutdown.".format(temp, max_temp))
            emergency_shutdown(heaters, fan)
            return False
        if emergency_enabled and temp > shutdown_threshold:
            print("Temperature {} exceeds emergency threshold {}! Initiating emergency shutdown.".format(temp, shutdown_threshold))
            emergency_shutdown(heaters, fan)
            return False
    return True

def emergency_shutdown(heaters, fan):
    """
    Performs an emergency shutdown by stopping all heaters and the fan.
    """
    print("Emergency shutdown initiated!")
    for heater in heaters.values():
        stop_heater(heater)
    stop_fan(fan)