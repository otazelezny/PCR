# code/fan.py
def set_fan_speed(fan, power_percentage):
    """
    Sets the fan speed using its PWM object.
    Expects the fan dictionary to have a "pwm" key.
    """
    power_percentage = max(0, min(100, power_percentage))
    if "pwm" in fan:
        pwm_value = int((power_percentage / 100) * 65535)
        fan["pwm"].duty_u16(pwm_value)
        print("Fan set to {}% power (PWM: {})".format(power_percentage, pwm_value))
    else:
        print("Error: Fan PWM not initialized.")

def stop_fan(fan):
    """
    Stops the fan.
    """
    set_fan_speed(fan, 0)
    print("Fan stopped.")