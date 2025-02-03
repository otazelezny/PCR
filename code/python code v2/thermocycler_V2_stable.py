from machine import ADC, Pin, PWM, reset
import math
from lib.simple_pid import PID
import time

### config ###

cycle_count = 5

### cycle settings ###

#Initial_Denaturation
Initial_Denaturatio_temp = 20
Initial_Denaturatio_time = 20
#Denaturation
Denaturation_temp = 90
Denaturatio_time = 5

#Annealing
Annealing_temp = 55
Annealing_time = 3

#Extension
Extension_temp = 72
Extension_time = 5

#Final_extension
Final_extension_temp = 72
Final_extension_time = 10

### pin and freq config ###

Heater_0 = PWM(Pin(6))
Heater_0.freq(50)
Heater_1 = PWM(Pin(7))
Heater_1.freq(50)
Fan = PWM(Pin(8))
Fan.freq(50)

adc = ADC(Pin(26))  # ADC0 is on GPIO 26


### pid ###

pid = PID(1.0, 1, 0.4, setpoint=25.0, sample_time=1.0, output_limits=(0, 95))
pid.auto_mode = True

pid_cooling = PID(1.0, 1, 0.4, setpoint=25.0, sample_time=1.0, output_limits=(0, 100))
pid_cooling.auto_mode = True

# Constants for the thermistor and the circuit
BETA = 3950  # Beta coefficient of the thermistor
R_PULLDOWN = 10000  # Value of the pull-down resistor in ohms
R_NOMINAL = 100000  # Resistance at 25 degrees Celsius
T_NOMINAL = 22 + 273.15  # Reference temperature in Kelvin

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

# Example usage
logger = Logger("log.txt")

def power_control(current_temp, target_temp):
    while True:
        negative_current_temp = -1 * current_temp
        pid.setpoint = target_temp
        print(pid.setpoint)
        pid_cooling.setpoint = -1*target_temp
        print(pid_cooling.setpoint)
        pid_output = pid(current_temp)
        pid_output_cooling = pid_cooling(negative_current_temp)
        Heater_0.duty_u16(int(pid_output * 65535 / 100))
        Heater_1.duty_u16(int(pid_output * 65535 / 100))
        Fan.duty_u16(int(pid_output_cooling * 65535 / 100))
        return pid_output, pid_output_cooling

def Initial_denaturation():
    while True:
        current_temp = read_temperature()
        target_temp = Initial_Denaturatio_temp
        target_time = Initial_Denaturatio_time
        pid_output_cooling, pid_output = power_control(current_temp, target_temp)
        logger.log(current_temp)
        print("temp = ", current_temp, "pid_out = ", pid_output, "pid_output_cooling = ", pid_output_cooling, )
        if current_temp >= target_temp - 5:
            if current_temp < 5+target_temp:
                 time_started = time.time
                 while True:
                    print("Initial denaturation reach the temperature")
                    for i in range(target_time):
                        current_temp = read_temperature()
                        pid_output_cooling, pid_output = power_control(current_temp, target_temp)
                        logger.log(current_temp)
                        print("temp = ", current_temp, "pid_out = ", pid_output, "pid_output_cooling = ", pid_output_cooling, )
                        time.sleep(1)
                    print("on to next one...")
                    return

        time.sleep(1)

def Denaturation():
    while True:
        current_temp = read_temperature()
        target_temp = Denaturation_temp
        target_time = Denaturatio_time
        pid_output_cooling, pid_output = power_control(current_temp, target_temp)
        logger.log(current_temp)
        print("temp = ", current_temp, "pid_out = ", pid_output, "pid_output_cooling = ", pid_output_cooling, )
        if current_temp >= target_temp - 5:
            if current_temp < 5+target_temp:
                 time_started = time.time
                 while True:
                    current_temp = read_temperature()
                    pid_output_cooling, pid_output = power_control(current_temp, target_temp)
                    logger.log(current_temp)
                    print("temp = ", current_temp, "pid_out = ", pid_output, "pid_output_cooling = ", pid_output_cooling, )
                    print("Initial denaturation reach the temperature")
                    print("on to next one...")
                    time_elapsed = time.time - time_started
                    if time_elapsed >= target_time:
                        print("time elapsed")
                        return
        time.sleep(1)
def Annealing():
    while True:
        current_temp = read_temperature()
        target_temp = Annealing_temp
        target_time = Annealing_time
        pid_output_cooling, pid_output = power_control(current_temp, target_temp)
        logger.log(current_temp)
        print("temp = ", current_temp, "pid_out = ", pid_output, "pid_output_cooling = ", pid_output_cooling, )
        if current_temp >= target_temp - 5:
            if current_temp < 5+target_temp:
                 time_started = time.time
                 while True:
                    current_temp = read_temperature()
                    pid_output_cooling, pid_output = power_control(current_temp, target_temp)
                    logger.log(current_temp)
                    print("temp = ", current_temp, "pid_out = ", pid_output, "pid_output_cooling = ", pid_output_cooling, )
                    print("Initial denaturation reach the temperature")
                    print("on to next one...")
                    time_elapsed = time.time - time_started
                    if time_elapsed >= target_time:
                        print("time elapsed")
                        return
        time.sleep(1)
def Extension():
    while True:
        current_temp = read_temperature()
        target_temp = Extension_temp
        target_time = Extension_time
        pid_output_cooling, pid_output = power_control(current_temp, target_temp)
        logger.log(current_temp)
        print("temp = ", current_temp, "pid_out = ", pid_output, "pid_output_cooling = ", pid_output_cooling, )
        if current_temp >= target_temp - 5:
            if current_temp < 5+target_temp:
                 time_started = time.time
                 while True:
                    current_temp = read_temperature()
                    pid_output_cooling, pid_output = power_control(current_temp, target_temp)
                    logger.log(current_temp)
                    print("temp = ", current_temp, "pid_out = ", pid_output, "pid_output_cooling = ", pid_output_cooling, )
                    print("Initial denaturation reach the temperature")
                    print("on to next one...")
                    time_elapsed = time.time - time_started
                    if time_elapsed >= target_time:
                        print("time elapsed")
                        return
        time.sleep(1)
def Final_extension():
    while True:
        current_temp = read_temperature()
        target_temp = Final_extension_temp
        target_time = Final_extension_time
        pid_output_cooling, pid_output = power_control(current_temp, target_temp)
        logger.log(current_temp)
        print("temp = ", current_temp, "pid_out = ", pid_output, "pid_output_cooling = ", pid_output_cooling, )
        if current_temp >= target_temp - 5:
            if current_temp < 5+target_temp:
                 time_started = time.time
                 while True:
                    current_temp = read_temperature()
                    pid_output_cooling, pid_output = power_control(current_temp, target_temp)
                    logger.log(current_temp)
                    print("temp = ", current_temp, "pid_out = ", pid_output, "pid_output_cooling = ", pid_output_cooling, )
                    print("Initial denaturation reach the temperature")
                    print("on to next one...")
                    time_elapsed = time.time - time_started
                    if time_elapsed >= target_time:
                        print("time elapsed")
                        return
        time.sleep(1)
def Cooling():
    while True:
        current_temp = read_temperature()
        target_temp = 0
        target_time = 10
        pid_output_cooling, pid_output = power_control(current_temp, target_temp)
        logger.log(current_temp)
        print("temp = ", current_temp, "pid_out = ", pid_output, "pid_output_cooling = ", pid_output_cooling, )
        if current_temp >= target_temp - 5:
            if current_temp < 5+target_temp:
                 time_started = time.time
                 while True:
                    current_temp = read_temperature()
                    pid_output_cooling, pid_output = power_control(current_temp, target_temp)
                    logger.log(current_temp)
                    print("temp = ", current_temp, "pid_out = ", pid_output, "pid_output_cooling = ", pid_output_cooling, )
                    print("Initial denaturation reach the temperature")
                    print("on to next one...")
                    time_elapsed = (time.time - time_started) * 1000
                    if time_elapsed >= target_time:
                        print("time elapsed")
                        return
        time.sleep(1)
while True:
    Initial_denaturation()
