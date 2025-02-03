from machine import ADC, Pin, PWM, reset
import math
from lib.simple_pid import PID
import time

Heater_0 = PWM(Pin(6))
Heater_0.freq(50)
Heater_1 = PWM(Pin(7))
Heater_1.freq(50)
Fan = PWM(Pin(8))
Fan.freq(50)
while True:
    Heater_0.duty_u16(int(0 * 65535 / 100))
    Heater_1.duty_u16(int(0 * 65535 / 100))
    Fan.duty_u16(int(100 * 65535 / 100))