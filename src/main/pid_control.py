from machine import Pin, ADC, PWM
import time
import math

# Thermistor and PID settings
THERMISTOR_PIN = 26  # ADC pin for the thermistor
HEATER_PIN = 15  # GPIO pin for the heater control
FAN_PIN = 14  # GPIO pin for the fan control

R_REF = 100000  # Reference resistor value in voltage divider (100kΩ)
BETA = 3950     # Beta value of the thermistor
T0 = 298.15     # Temperature in Kelvin at 25 degrees Celsius (273.15 + 25)
R0 = 100000     # Resistance of the thermistor at 25 degrees Celsius

# PID constants
Kp = 2.0  # Proportional gain
Ki = 0.5  # Integral gain
Kd = 1.0  # Derivative gain

# Control setup
MAX_PWM = 65535  # Max PWM value for the heater
SET_TEMP = 60    # Target temperature in Celsius

# GPIO and ADC setup
adc = ADC(Pin(THERMISTOR_PIN))
heater = PWM(Pin(HEATER_PIN))
heater.freq(1000)  # Set PWM frequency to 1 kHz
fan = Pin(FAN_PIN, Pin.OUT)

# PID control variables
previous_error = 0
integral = 0
last_time = time.ticks_ms()

def read_temp():
    """Read the ADC value and convert it to temperature."""
    adc_value = adc.read_u16()  # Read ADC value (0-65535)
    voltage = adc_value / 65535 * 3.3  # Convert to voltage (3.3V ref)
    
    # Calculate thermistor resistance
    R_thermistor = R_REF * (3.3 / voltage - 1)
    
    # Steinhart-Hart equation or beta equation to calculate temperature in Kelvin
    temp_kelvin = 1 / ((1 / T0) + (1 / BETA) * math.log(R_thermistor / R0))
    temp_celsius = temp_kelvin - 273.15  # Convert Kelvin to Celsius
    return temp_celsius

def pid_control(current_temp, target_temp):
    """Compute the PID output."""
    global previous_error, integral, last_time
    
    error = target_temp - current_temp
    current_time = time.ticks_ms()
    delta_time = (current_time - last_time) / 1000  # Convert to seconds
    last_time = current_time
    
    # Integral term
    integral += error * delta_time
    
    # Derivative term
    derivative = (error - previous_error) / delta_time
    
    # PID formula
    output = Kp * error + Ki * integral + Kd * derivative
    previous_error = error
    
    # Limit the output to the range of PWM
    output = max(0, min(MAX_PWM, output))
    return output

def control_heater(output):
    """Control the heater based on the PID output."""
    heater.duty_u16(int(output))  # Adjust heater power with PWM

def control_fan(current_temp, target_temp):
    """Control the fan based on current temperature."""
    if current_temp > target_temp + 2:
        fan.on()  # Turn fan on if temp exceeds target by 2 degrees
    else:
        fan.off()

while True:
    # Read the current temperature
    current_temp = read_temp()
    
    # Compute PID output
    pid_output = pid_control(current_temp, SET_TEMP)
    
    # Control heater and fan
    control_heater(pid_output)
    control_fan(current_temp, SET_TEMP)
    
    # Debug print
    print("Temp: {:.2f} C, PID Output: {}".format(current_temp, pid_output))
    
    # Delay for stability (adjust as needed)
    time.sleep(0.5)