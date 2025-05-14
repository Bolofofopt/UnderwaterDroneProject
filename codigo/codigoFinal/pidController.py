import time

class PIDController:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = 0.0
        self.prev_error = 0.0
        self.last_time = time.time()

    def reset(self):
        self.integral = 0.0
        self.prev_error = 0.0
        self.last_time = time.time()

    def update(self, error):
        current_time = time.time()
        delta_time = current_time - self.last_time

        self.integral += error * delta_time
        derivative = (error - self.prev_error) / delta_time if delta_time > 0 else 0.0

        output = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)

        self.prev_error = error
        self.last_time = current_time
        return output
