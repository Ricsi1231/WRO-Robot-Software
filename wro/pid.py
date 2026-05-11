from __future__ import annotations

import time

from wro.config import PidConfig


class PIDController:
    def __init__(self, config: PidConfig) -> None:
        self._config = config
        self._integral = 0.0
        self._last_error = 0.0
        self._last_output = 0.0
        self._last_derivative = 0.0
        self._prev_measured = 0.0
        self._last_time = 0.0
        self._settled = True

    def reset(self) -> None:
        self._integral = 0.0
        self._last_error = 0.0
        self._last_output = 0.0
        self._last_derivative = 0.0
        self._prev_measured = 0.0
        self._last_time = 0.0
        self._settled = True

    def compute(self, setpoint: float, measured: float) -> float:
        error = setpoint - measured
        now = time.monotonic()

        dt = now - self._last_time
        if self._last_time == 0.0 or dt < 1e-6:
            self._last_time = now
            self._last_error = error
            self._prev_measured = measured
            self._last_derivative = 0.0
            output = self._config.kp * error
            self._last_output = output
            return output

        if abs(error) < self._config.error_epsilon:
            error = 0.0
            self._integral = 0.0
            self._settled = True
        else:
            self._settled = False

        # Derivative-on-measurement (not on error) avoids derivative kick when
        # the setpoint changes; intentional, do not switch to derivative-on-error.
        raw_derivative = -(measured - self._prev_measured) / dt
        alpha = self._config.derivative_alpha
        self._last_derivative = alpha * raw_derivative + (1.0 - alpha) * self._last_derivative

        tentative = self._config.kp * error + self._config.ki * self._integral + self._config.kd * self._last_derivative

        below_max = abs(tentative) < self._config.max_output
        correcting = tentative * error < 0

        if below_max or correcting:
            self._integral += error * dt
            self._integral = max(-self._config.max_integral, min(self._config.max_integral, self._integral))

        output = self._config.kp * error + self._config.ki * self._integral + self._config.kd * self._last_derivative
        output = max(-self._config.max_output, min(self._config.max_output, output))

        self._last_output = output
        self._last_error = error
        self._last_time = now
        self._prev_measured = measured

        return output

    def set_parameters(self, kp: float, ki: float, kd: float) -> None:
        self._config.kp = kp
        self._config.ki = ki
        self._config.kd = kd

    @property
    def is_settled(self) -> bool:
        return self._settled

    @property
    def last_error(self) -> float:
        return self._last_error

    @property
    def last_derivative(self) -> float:
        return self._last_derivative

    @property
    def output(self) -> float:
        return self._last_output
