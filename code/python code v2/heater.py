# code/heater.py
def set_heater_power(heater, power_percentage):
    """
    Sets the heater power using its PWM object.
    Expects the heater dictionary to have a "pwm" key.
    """
    # Clamp power between 0 and the heater's max_power (default 100)
    max_power = heater.get("max_power", 100)
    power_percentage = max(0, min(max_power, power_percentage))
    
    if "pwm" in heater:
        pwm_value = int((power_percentage / 100) * 65535)
        heater["pwm"].duty_u16(pwm_value)
        print("Heater {} set to {}% (PWM: {})".format(heater["name"], power_percentage, pwm_value))
    else:
        print("Error: Heater PWM not initialized for {}.".format(heater["name"]))

def stop_heater(heater):
    """
    Stops the heater.
    """
    set_heater_power(heater, 0)
    print("Heater {} stopped.".format(heater["name"]))