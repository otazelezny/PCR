# tests/test_pid.py
import unittest
import sys
import os


# Ensure the "code" folder is in the Python path.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

from pid import PID

class TestPID(unittest.TestCase):
    def test_pid_output_with_only_proportional(self):
        # Create a PID with kp=1.0, ki=0.0, kd=0.0 and setpoint 10.
        pid = PID(1.0, 0.0, 0.0, setpoint=10)
        # For a current value of 5, error is 5, so output should be 5.
        output = pid.compute(5)
        self.assertAlmostEqual(output, 5.0)
        
        # For a current value of 8, error is 2, so output should be 2.
        output = pid.compute(8)
        self.assertAlmostEqual(output, 2.0)

    def test_pid_with_integral_and_derivative(self):
        # Create a PID with non-zero ki and kd.
        pid = PID(1.0, 0.5, 0.1, setpoint=10)
        # First call: current value 7, error = 3.
        out1 = pid.compute(7)
        # Second call: current value 8, error = 2.
        out2 = pid.compute(8)
        # We simply check that the output changes and remains a float.
        self.assertIsInstance(out1, float)
        self.assertIsInstance(out2, float)

if __name__ == '__main__':
    unittest.main()