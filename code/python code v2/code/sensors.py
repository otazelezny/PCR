# code/sensors.py
import machine

def init_sensors(sensor_config):
    """
    Initializes sensors based on the configuration.
    Returns a dictionary mapping sensor keys to sensor objects.
    """
    sensors = {}
    for sensor_key, conf in sensor_config.items():
        if conf.get("enabled", False):
            pin = conf.get("pin")
            # Create an ADC instance for the sensor pin.
            adc = machine.ADC(machine.Pin(pin))
            sensors[sensor_key] = {
                "name": conf.get("name"),
                "adc": adc
            }
    return sensors

def read_temperatures(sensors):
    """
    Reads and returns temperatures from all initialized sensors.
    (Assumes ADC reading 0-65535 maps linearly to 0-120°C.)
    """
    readings = {}
    for sensor_key, sensor in sensors.items():
        adc = sensor["adc"]
        raw = adc.read_u16()
        temperature = (raw / 65535) * 120  # Replace with actual conversion if needed.
        readings[sensor["name"]] = temperature
    return readings