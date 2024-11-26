from machine import ADC, Pin, PWM, reset
import math
from simple_pid import PID
import time
from main.pid_control import 
count = 5


Peltier = PWM(Pin(10))
Peltier.freq(50)
Heater = PWM(Pin(11))
Peltier.freq(50)
Ch_fan = PWM(Pin(12))
Ch_fan.freq(50)
Rpi_fan = PWM(Pin(13))
Ch_fan.freq(50)


# Constants for the thermistor
BETA = 3950  # Beta value
T0 = 298.15  # Reference temperature (25°C in Kelvin)
R0 = 100000  # Resistance of the thermistor at 25°C (100k Ohms)

adc = ADC(Pin(26))  # ADC0 is on GPIO 26

pid = PID(1.0, 0.2, 0.4, setpoint=25.0, sample_time=1.0, output_limits=(0, 100))
pid.auto_mode = True

pid_cooling = PID(1.0, 0.2, 0.4, setpoint=25.0, sample_time=1.0, output_limits=(0, 80))
pid_cooling.auto_mode = True

def read_temperature():
    adc_value = adc.read_u16()
    # Convert ADC reading to voltage
    voltage = (adc_value / 65535.0) * 3.3
    # Calculate the resistance of the thermistor
    R = (100000 * voltage) / (3.3 - voltage)  # 100k resistor in divider

    # Calculate temperature using the Beta equation
    inv_T = 1/T0 + (1/BETA) * math.log(R/R0)
    T = 1/inv_T

    return T - 273.15  # Convert from Kelvin to Celsius

def Initial_Denaturation(current_temperature):
    while True:
        print("Initial_Denaturation")
        current_temperature = read_temperature()
        negative_current_temp = -1 *current_temperature
        target_temp = 94
        pid.setpoint = target_temp# Set the setpoint to 25°C
        pid_cooling.setpoint = -1 * target_temp
        pid_output = pid(current_temperature)
        pid_output_negative = pid_cooling(negative_current_temp)
        Heater.duty_u16(int(pid_output * 65535 / 100))
        Peltier.duty_u16(int(pid_output_negative * 65535 / 200))
        Ch_fan.duty_u16(int(pid_output_negative * 65535 / 100))
        print("temp = ", current_temperature, "pid_out = ", pid_output, "pid_output_negative = ", pid_output_negative)# Update the PWM duty cycle
        if current_temperature >= target_temp - 5:
            if current_temperature < 5+target_temp:
                print("Initial denaturation reach the temperature")
                time.sleep(10)
                print("on to next one...")
                return
        time.sleep(1)

def Denaturation(current_temperature):
     while True:
        print("Denaturation")
        current_temperature = read_temperature()
        negative_current_temp = -1 *current_temperature
        target_temp = 94
        pid.setpoint = target_temp# Set the setpoint to 25°C
        pid_cooling.setpoint = -1 * target_temp
        pid_output = pid(current_temperature)
        pid_output_negative = pid_cooling(negative_current_temp)
        Heater.duty_u16(int(pid_output * 65535 / 100))
        Peltier.duty_u16(int(pid_output_negative * 65535 / 200))
        Ch_fan.duty_u16(int(pid_output_negative * 65535 / 100))
        print("temp = ", current_temperature, "pid_out = ", pid_output, "pid_output_negative = ", pid_output_negative)# Update the PWM duty cycle
        if current_temperature >= target_temp - 5:
            if current_temperature < 5+target_temp:
                print("Denaturation reach the temperature")
                time.sleep(3)
                print("on to next one...")
                return
        time.sleep(1)
    
def Annealing(current_temperature):
    while True:
        print("Annealing")
        current_temperature = read_temperature()
        negative_current_temp = -1 *current_temperature
        target_temp = 55
        pid.setpoint = target_temp# Set the setpoint to 25°C
        pid_cooling.setpoint = -1 * target_temp
        pid_output = pid(current_temperature)
        pid_output_negative = pid_cooling(negative_current_temp)
        Heater.duty_u16(int(pid_output * 65535 / 100))
        Peltier.duty_u16(int(pid_output_negative * 65535 / 200))
        Ch_fan.duty_u16(int(pid_output_negative * 65535 / 100))
        print("temp = ", current_temperature, "pid_out = ", pid_output, "pid_output_negative = ", pid_output_negative)# Update the PWM duty cycle
        if current_temperature >= target_temp - 5:
            if current_temperature < 5+target_temp:
                print("Annealing reach the temperature")
                time.sleep(3)
                print("on to next one...")
                return
        time.sleep(1)
        
def Extension(current_temperature):
    while True:
        print("Extension")
        current_temperature = read_temperature()
        negative_current_temp = -1 *current_temperature
        target_temp = 72
        pid.setpoint = target_temp# Set the setpoint to 25°C
        pid_cooling.setpoint = -1 * target_temp
        pid_output = pid(current_temperature)
        pid_output_negative = pid_cooling(negative_current_temp)
        Heater.duty_u16(int(pid_output * 65535 / 100))
        Peltier.duty_u16(int(pid_output_negative * 65535 / 100))
        Ch_fan.duty_u16(int(pid_output_negative * 65535 / 100))
        print("temp = ", current_temperature, "pid_out = ", pid_output, "pid_output_negative = ", pid_output_negative)# Update the PWM duty cycle
        if current_temperature >= target_temp - 5:
            if current_temperature < 5+target_temp:
                print("Annealing reach the temperature")
                time.sleep(3)
                print("on to next one...")
                return
        time.sleep(1)
    
def Final_Extension(current_temperature):
    while True:
        print("final_extension")
        current_temperature = read_temperature()
        negative_current_temp = -1 *current_temperature
        target_temp = 72
        pid.setpoint = target_temp# Set the setpoint to 25°C
        pid_cooling.setpoint = -1 * target_temp
        pid_output = pid(current_temperature)
        pid_output_negative = pid_cooling(negative_current_temp)
        Heater.duty_u16(int(pid_output * 65535 / 100))
        Peltier.duty_u16(int(pid_output_negative * 65535 / 200))
        Ch_fan.duty_u16(int(pid_output_negative * 65535 / 100))
        print("temp = ", current_temperature, "pid_out = ", pid_output, "pid_output_negative = ", pid_output_negative)# Update the PWM duty cycle
        if current_temperature >= target_temp - 5:
            if current_temperature < 5+target_temp:
                print("Final extension reach the temperature")
                time.sleep(10)
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
        Heater.duty_u16(int(0 * 65535 / 100))
        Peltier.duty_u16(int(pid_output_negative * 65535 / 100))
        Ch_fan.duty_u16(int(pid_output_negative * 65535 / 100))
        print("temp = ", current_temperature, "pid_output_negative = ", pid_output_negative)# Update the PWM duty cycle
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