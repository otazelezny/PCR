# tests/test_fan.py
import unittest
import sys
import os

# Add the "code" folder to the Python path.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

from fan import set_fan_speed, stop_fan

# Create a dummy PWM class to simulate the PWM hardware.
class DummyPWM:
    def __init__(self):
        self.last_value = None
    def duty_u16(self, value):
        self.last_value = value

class TestFan(unittest.TestCase):
    def setUp(self):
        # Create a dummy fan object with a fake PWM instance.
        self.dummy_pwm = DummyPWM()
        self.fan = {
            "pwm": self.dummy_pwm,
            "enabled": True
        }
    
    def test_set_fan_speed(self):
        # Set fan speed to 50% and check the PWM value.
        set_fan_speed(self.fan, 50)
        expected_pwm = int((50 / 100) * 65535)
        self.assertEqual(self.dummy_pwm.last_value, expected_pwm)
        
    def test_stop_fan(self):
        # First, set a non-zero speed then stop the fan.
        set_fan_speed(self.fan, 80)
        stop_fan(self.fan)
        expected_pwm = int((0 / 100) * 65535)
        self.assertEqual(self.dummy_pwm.last_value, expected_pwm)

if __name__ == '__main__':
    unittest.main()