# code/pid.py
class PID:
    def __init__(self, kp, ki, kd, setpoint=0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.integral = 0
        self.last_error = 0

    def compute(self, current_value):
        """
        Compute the PID output given the current_value.
        """
        error = self.setpoint - current_value
        self.integral += error
        derivative = error - self.last_error
        self.last_error = error
        output = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)
        return output