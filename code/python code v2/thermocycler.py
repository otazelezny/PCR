from machine import ADC, Pin, PWM, reset
import math
from lib.simple_pid import PID
import time

count = 5


Fan = PWM(Pin(8))
Fan.freq(50)
Heater_0 = PWM(Pin(7))
Heater_0.freq(50)
Heater_1 = PWM(Pin(6))
Heater_1.freq(50)
Rpi_fan = PWM(Pin(9))
Rpi_fan.freq(50)

# Constants for the thermistor and the circuit
BETA = 3950  # Beta coefficient of the thermistor
R_PULLDOWN = 10000  # Value of the pull-down resistor in ohms
R_NOMINAL = 100000  # Resistance at 25 degrees Celsius
T_NOMINAL = 22 + 273.15  # Reference temperature in Kelvin

adc = ADC(Pin(26))  # ADC0 is on GPIO 26
adc_2 = ADC(Pin(27))

pid = PID(1.0, 1, 0.4, setpoint=25.0, sample_time=1.0, output_limits=(0, 100))
pid.auto_mode = True

pid_cooling = PID(1.0, 1, 0.4, setpoint=25.0, sample_time=1.0, output_limits=(0, 100))
pid_cooling.auto_mode = True


class Logger:
    def __init__(self, filename="log.txt"):
        self.filename = filename

    def log(self, message):
        # Manually create a timestamp from localtime()
        t = time.localtime()  # Get the current time as a struct_time tuple
        timestamp = f"{t[3]:02d}:{t[4]:02d}:{t[5]:02d}"

        # Append the timestamp and message to the file
        with open(self.filename, "a") as f:
            f.write(f"{timestamp} - {message}\n")
class Logger_probe:
    def __init__(self, filename="log_probe.txt"):
        self.filename = filename

    def log(self, message):
        # Manually create a timestamp from localtime()
        t = time.localtime()  # Get the current time as a struct_time tuple
        timestamp = f"{t[3]:02d}:{t[4]:02d}:{t[5]:02d}"

        # Append the timestamp and message to the file
        with open(self.filename, "a") as f:
            f.write(f"{timestamp} - {message}\n")


# Example usage
logger = Logger("log.txt")
logger_probe = Logger_probe("log_probe.txt")
# Log some messages
logger.log("Program started")
time.sleep(1)
logger.log("Some action happened")


def read_temperature():
    # Read the ADC value (12-bit ADC on Raspberry Pi Pico, range 0-4095)
    adc_value = adc.read_u16()
    
    # Convert the ADC value to a voltage ratio (0.0 to 1.0)
    v_ratio = adc_value / 65535.0  # For 16-bit resolution

    # Calculate the resistance of the thermistor
    if v_ratio == 0:
        return None  # Avoid division by zero
    thermistor_resistance = (R_PULLDOWN * (1 - v_ratio)) / v_ratio

    # Apply the Steinhart-Hart equation to calculate temperature in Kelvin
    temperature_kelvin = 1 / (1 / T_NOMINAL + (1 / BETA) * math.log(thermistor_resistance / R_NOMINAL))
    
    # Convert Kelvin to Celsius
    temperature_celsius = temperature_kelvin - 273.15
    
    return temperature_celsius

def read_probe_temperature():
    # Read the ADC value (12-bit ADC on Raspberry Pi Pico, range 0-4095)
    adc_value = adc.read_u16()
    
    # Convert the ADC value to a voltage ratio (0.0 to 1.0)
    v_ratio = adc_value / 65535.0  # For 16-bit resolution

    # Calculate the resistance of the thermistor
    if v_ratio == 0:
        return None  # Avoid division by zero
    thermistor_resistance = (R_PULLDOWN * (1 - v_ratio)) / v_ratio

    # Apply the Steinhart-Hart equation to calculate temperature in Kelvin
    temperature_kelvin = 1 / (1 / T_NOMINAL + (1 / BETA) * math.log(thermistor_resistance / R_NOMINAL))
    
    # Convert Kelvin to Celsius
    temperature_celsius = temperature_kelvin - 273.15
    
    return temperature_celsius


def Initial_Denaturation(current_temperature):
    while True:
        print("Initial_Denaturation")
        target_temp = 94

        current_temperature = read_temperature()
        negative_current_temp = -1 * current_temperature
        pid.setpoint = target_temp# Set the setpoint to 25°C
        pid_cooling.setpoint = -1 * target_temp
        pid_output = pid(current_temperature)
        pid_output_negative = pid_cooling(negative_current_temp)
        Heater_0.duty_u16(int(pid_output * 65535 / 100))
        Heater_1.duty_u16(int(pid_output * 65535 / 100))
        Fan.duty_u16(int(pid_output_negative * 65535 / 100))
        print("temp = ", current_temperature, "pid_out = ", pid_output, "pid_output_negative = ", pid_output_negative)# Update the PWM duty cycle
        logger.log(current_temperature)
        probe_temp = read_probe_temperature()
        logger_probe.log(probe_temp)
        if current_temperature >= target_temp - 5:
            if current_temperature < 5+target_temp:
                print("Initial denaturation reach the temperature")
                for x in range(10):
                    print(x,"s")
                    current_temperature = read_temperature()
                    negative_current_temp = -1 * current_temperature
                    pid.setpoint = target_temp# Set the setpoint to 25°C
                    pid_cooling.setpoint = -1 * target_temp
                    pid_output = pid(current_temperature)
                    pid_output_negative = pid_cooling(negative_current_temp)
                    Heater_0.duty_u16(int(pid_output * 65535 / 100))
                    Heater_1.duty_u16(int(pid_output * 65535 / 100))
                    Fan.duty_u16(int(pid_output_negative * 65535 / 100))
                    print("temp = ", current_temperature, "pid_out = ", pid_output, "pid_output_negative = ", pid_output_negative)# Update the PWM duty cycle
                    logger.log(current_temperature)
                    probe_temp = read_probe_temperature()
                    logger_probe.log(probe_temp)
                    time.sleep(1)
                print("on to next one...")
                return
        time.sleep(1)

def Denaturation(current_temperature):
     while True:
        print("Initial_Denaturation")
        target_temp = 94
        current_temperature = read_temperature()
        negative_current_temp = -1 *current_temperature
        pid.setpoint = target_temp# Set the setpoint to 25°C
        pid_cooling.setpoint = -1 * target_temp
        pid_output = pid(current_temperature)
        pid_output_negative = pid_cooling(negative_current_temp)
        Heater_0.duty_u16(int(pid_output * 65535 / 100))
        Heater_1.duty_u16(int(pid_output * 65535 / 100))
        Fan.duty_u16(int(pid_output_negative * 65535 / 100))
        print("temp = ", current_temperature, "pid_out = ", pid_output, "pid_output_negative = ", pid_output_negative)# Update the PWM duty cycle
        logger.log(current_temperature)
        probe_temp = read_probe_temperature()
        logger_probe.log(probe_temp)
        if current_temperature >= target_temp - 5:
            if current_temperature < 5+target_temp:
                print("Denaturation reach the temperature")
                for x in range(count):
                    print(x,"s")
                    current_temperature = read_temperature()
                    negative_current_temp = -1 * current_temperature
                    pid.setpoint = target_temp# Set the setpoint to 25°C
                    pid_cooling.setpoint = -1 * target_temp
                    pid_output = pid(current_temperature)
                    pid_output_negative = pid_cooling(negative_current_temp)
                    Heater_0.duty_u16(int(pid_output * 65535 / 100))
                    Heater_1.duty_u16(int(pid_output * 65535 / 100))
                    Fan.duty_u16(int(pid_output_negative * 65535 / 100))
                    print("temp = ", current_temperature, "pid_out = ", pid_output, "pid_output_negative = ", pid_output_negative)# Update the PWM duty cycle
                    logger.log(current_temperature)
                    probe_temp = read_probe_temperature()
                    logger_probe.log(probe_temp)
                    time.sleep(1)
                print("on to next one...")
                return
        time.sleep(1)
    
def Annealing(current_temperature):
    while True:
        print("Annealing")
        target_temp = 55
        current_temperature = read_temperature()
        negative_current_temp = -1 *current_temperature
        pid.setpoint = target_temp# Set the setpoint to 25°C
        pid_cooling.setpoint = -1 * target_temp
        pid_output = pid(current_temperature)
        pid_output_negative = pid_cooling(negative_current_temp)
        Heater_0.duty_u16(int(pid_output * 65535 / 100))
        Heater_1.duty_u16(int(pid_output * 65535 / 100))
        Fan.duty_u16(int(pid_output_negative * 65535 / 100))
        print("temp = ", current_temperature, "pid_out = ", pid_output, "pid_output_negative = ", pid_output_negative)# Update the PWM duty cycle
        logger.log(current_temperature)
        probe_temp = read_probe_temperature()
        logger_probe.log(probe_temp)
        if current_temperature >= target_temp - 5:
            if current_temperature < 5+target_temp:
                print("Anealing reach the temperature")
                for x in range(10):
                    print(x,"s")
                    current_temperature = read_temperature()
                    negative_current_temp = -1 * current_temperature
                    pid.setpoint = target_temp# Set the setpoint to 25°C
                    pid_cooling.setpoint = -1 * target_temp
                    pid_output = pid(current_temperature)
                    pid_output_negative = pid_cooling(negative_current_temp)
                    Heater_0.duty_u16(int(pid_output * 65535 / 100))
                    Heater_1.duty_u16(int(pid_output * 65535 / 100))
                    Fan.duty_u16(int(pid_output_negative * 65535 / 100))
                    print("temp = ", current_temperature, "pid_out = ", pid_output, "pid_output_negative = ", pid_output_negative)# Update the PWM duty cycle
                    logger.log(current_temperature)
                    probe_temp = read_probe_temperature()
                    logger_probe.log(probe_temp)
                    time.sleep(1)
                
                print("on to next one...")
                return
        time.sleep(1)
        
def Extension(current_temperature):
    while True:
        print("Extension")
        target_temp = 72
        current_temperature = read_temperature()
        negative_current_temp = -1 *current_temperature
        pid.setpoint = target_temp# Set the setpoint to 25°C
        pid_cooling.setpoint = -1 * target_temp
        pid_output = pid(current_temperature)
        pid_output_negative = pid_cooling(negative_current_temp)
        Heater_0.duty_u16(int(pid_output * 65535 / 100))
        Heater_1.duty_u16(int(pid_output * 65535 / 100))
        Fan.duty_u16(int(pid_output_negative * 65535 / 100))
        print("temp = ", current_temperature, "pid_out = ", pid_output, "pid_output_negative = ", pid_output_negative)# Update the PWM duty cycle
        logger.log(current_temperature)
        probe_temp = read_probe_temperature()
        logger_probe.log(probe_temp)
        if current_temperature >= target_temp - 5:
            if current_temperature < 5+target_temp:
                print("Denaturation reach the temperature")
                for x in range(10):
                    print(x,"s")
                    current_temperature = read_temperature()
                    negative_current_temp = -1 * current_temperature
                    pid.setpoint = target_temp# Set the setpoint to 25°C
                    pid_cooling.setpoint = -1 * target_temp
                    pid_output = pid(current_temperature)
                    pid_output_negative = pid_cooling(negative_current_temp)
                    Heater_0.duty_u16(int(pid_output * 65535 / 100))
                    Heater_1.duty_u16(int(pid_output * 65535 / 100))
                    Fan.duty_u16(int(pid_output_negative * 65535 / 100))
                    print("temp = ", current_temperature, "pid_out = ", pid_output, "pid_output_negative = ", pid_output_negative)# Update the PWM duty cycle
                    logger.log(current_temperature)
                    probe_temp = read_probe_temperature()
                    logger_probe.log(probe_temp)
                    time.sleep(1)
                
                print("on to next one...")
                return
        time.sleep(1)
    
def Final_Extension(current_temperature):
    while True:
        print("Final extension")
        target_temp = 72
        current_temperature = read_temperature()
        negative_current_temp = -1 *current_temperature
        pid.setpoint = target_temp# Set the setpoint to 25°C
        pid_cooling.setpoint = -1 * target_temp
        pid_output = pid(current_temperature)
        pid_output_negative = pid_cooling(negative_current_temp)
        Heater_0.duty_u16(int(pid_output * 65535 / 100))
        Heater_1.duty_u16(int(pid_output * 65535 / 100))
        Fan.duty_u16(int(pid_output_negative * 65535 / 100))
        print("temp = ", current_temperature, "pid_out = ", pid_output, "pid_output_negative = ", pid_output_negative)# Update the PWM duty cycle
        logger.log(current_temperature)
        probe_temp = read_probe_temperature()
        logger_probe.log(probe_temp)
        if current_temperature >= target_temp - 5:
            if current_temperature < 5+target_temp:
                print("Denaturation reach the temperature")
                for x in range(30):
                    print(x,"s")
                    current_temperature = read_temperature()
                    negative_current_temp = -1 * current_temperature
                    pid.setpoint = target_temp# Set the setpoint to 25°C
                    pid_cooling.setpoint = -1 * target_temp
                    pid_output = pid(current_temperature)
                    pid_output_negative = pid_cooling(negative_current_temp)
                    Heater_0.duty_u16(int(pid_output * 65535 / 100))
                    Heater_1.duty_u16(int(pid_output * 65535 / 100))
                    Fan.duty_u16(int(pid_output_negative * 65535 / 100))
                    print("temp = ", current_temperature, "pid_out = ", pid_output, "pid_output_negative = ", pid_output_negative)# Update the PWM duty cycle
                    logger.log(current_temperature)
                    probe_temp = read_probe_temperature()
                    logger_probe.log(probe_temp)
                    time.sleep(1)
                
                print("on to next one...")
                return
        time.sleep(1)
        
def final_cooling(current_temperature):
    while True:
        print("final_cooling")
        current_temperature = read_temperature()
        negative_current_temp = -1 *current_temperature
        target_temp = 25
        pid.setpoint = target_temp# Set the setpoint to 25°C
        pid_cooling.setpoint = -1 * target_temp
        pid_output_negative = pid_cooling(negative_current_temp)
        Heater_0.duty_u16(int(0 * 65535 / 100))
        Heater_1.duty_u16(int(pid_output * 65535 / 100))
        Fan.duty_u16(int(pid_output_negative * 65535 / 100))
        print("temp = ", current_temperature, "pid_output_negative = ", pid_output_negative)# Update the PWM duty cycle
        logger.log(current_temperature)
        if current_temperature >= target_temp:
            print("cooling down")
            time.sleep(120)
            print("End")
            return
        time.sleep(1)
    
while True:
    Rpi_fan.duty_u16(int(100 * 65535 / 100))
    temperature = read_temperature()
    print("Temperature:", temperature, "°C")
    
    Initial_Denaturation(temperature)
    Annealing(temperature)
    Extension(temperature)

    # Loop for X cycles
    for i in range(count):
        print("starting loop")
        print(i)
        Denaturation(temperature)
        Annealing(temperature)
        Extension(temperature)
    Denaturation(temperature)
    Annealing(temperature)
    Final_Extension(temperature)
    final_cooling(temperature)
    print("End")
    
    reset()
    time.sleep(1)  # Wait for 2 seconds before reading again



