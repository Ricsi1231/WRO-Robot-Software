from __future__ import annotations

import time
from typing import Any

from wro.config import MotorConfig, PinConfig

MIN_SPEED = 0
MAX_SPEED = 100


class MotorDriver:
    def __init__(self, config: MotorConfig, pins: PinConfig) -> None:
        self._config = config
        self._pins = pins
        self._speed: int = 0
        self._clockwise: bool = True
        self._pwm: Any = None
        self._dir_pin: Any = None
        self._sleep_pin: Any = None

    def init(self) -> None:
        from gpiozero import DigitalOutputDevice, PWMOutputDevice

        if self._pins.motor_pwm is not None:
            self._pwm = PWMOutputDevice(self._pins.motor_pwm, frequency=self._config.pwm_frequency)
        if self._pins.motor_direction is not None:
            self._dir_pin = DigitalOutputDevice(self._pins.motor_direction)
        if self._pins.motor_sleep is not None:
            self._sleep_pin = DigitalOutputDevice(self._pins.motor_sleep, initial_value=True)

    def set_speed(self, percent: int) -> None:
        percent = max(MIN_SPEED, min(MAX_SPEED, percent))
        if percent > 0 and percent < self._config.min_effective_percent:
            percent = self._config.min_effective_percent
        self._speed = percent
        if self._pwm is not None:
            self._pwm.value = percent / 100.0

    def set_direction(self, clockwise: bool) -> None:
        if self._clockwise == clockwise:
            return
        self._clockwise = clockwise
        if self._dir_pin is not None:
            self._dir_pin.value = clockwise

    def set_direction_safe(self, clockwise: bool) -> None:
        if self._clockwise == clockwise:
            return
        original_speed = self._speed
        self._ramp_to(0)
        self.set_direction(clockwise)
        if original_speed > 0:
            target = max(original_speed, self._config.min_effective_percent)
            self._ramp_to(target)

    def stop(self) -> None:
        self._speed = 0
        if self._pwm is not None:
            self._pwm.value = 0

    def brake(self) -> None:
        self._speed = 0
        if self._pwm is not None:
            self._pwm.value = 0

    @property
    def speed(self) -> int:
        return self._speed

    @property
    def is_running(self) -> bool:
        return self._speed > 0

    def cleanup(self) -> None:
        self.stop()
        if self._pwm is not None:
            self._pwm.close()
        if self._dir_pin is not None:
            self._dir_pin.close()
        if self._sleep_pin is not None:
            self._sleep_pin.close()

    def _ramp_to(self, target: int) -> None:
        step = self._config.ramp_step_percent
        delay = self._config.ramp_step_delay_s
        current = self._speed
        while current != target:
            current = min(current + step, target) if current < target else max(current - step, target)
            self.set_speed(current)
            time.sleep(delay)
