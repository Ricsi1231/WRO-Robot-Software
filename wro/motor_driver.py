from __future__ import annotations

import time
from typing import Any

from wro.config import MotorConfig

MIN_SPEED = 0
MAX_SPEED = 100


class MotorDriver:
    def __init__(self, config: MotorConfig, en_pin: int | None, in1_pin: int | None, in2_pin: int | None) -> None:
        self._config = config
        self._en_pin = en_pin
        self._in1_pin = in1_pin
        self._in2_pin = in2_pin
        self._speed: int = 0
        self._clockwise: bool = True
        self._pwm: Any = None
        self._in1: Any = None
        self._in2: Any = None

    def init(self) -> None:
        from gpiozero import DigitalOutputDevice, PWMOutputDevice

        if self._en_pin is not None:
            self._pwm = PWMOutputDevice(self._en_pin, frequency=self._config.pwm_frequency)
        if self._in1_pin is not None:
            self._in1 = DigitalOutputDevice(self._in1_pin)
        if self._in2_pin is not None:
            self._in2 = DigitalOutputDevice(self._in2_pin)

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
        self._apply_direction()

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
        if self._in1 is not None:
            self._in1.off()
        if self._in2 is not None:
            self._in2.off()

    def brake(self) -> None:
        self._speed = 0
        if self._pwm is not None:
            self._pwm.value = 0
        if self._in1 is not None:
            self._in1.on()
        if self._in2 is not None:
            self._in2.on()

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
        if self._in1 is not None:
            self._in1.close()
        if self._in2 is not None:
            self._in2.close()

    def _apply_direction(self) -> None:
        if self._in1 is not None and self._in2 is not None:
            if self._clockwise:
                self._in1.on()
                self._in2.off()
            else:
                self._in1.off()
                self._in2.on()

    def _ramp_to(self, target: int) -> None:
        step = self._config.ramp_step_percent
        delay = self._config.ramp_step_delay_s
        current = self._speed
        while current != target:
            current = min(current + step, target) if current < target else max(current - step, target)
            self.set_speed(current)
            time.sleep(delay)
