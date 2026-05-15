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
        self._ramp_target: int | None = None
        self._ramp_next_step_at: float = 0.0
        self._pending_direction: bool | None = None
        self._pending_restore_speed: int = 0

    def init(self) -> None:
        from gpiozero import DigitalOutputDevice, PWMOutputDevice

        if self._en_pin is not None:
            self._pwm = PWMOutputDevice(self._en_pin, frequency=self._config.pwm_frequency)
        if self._in1_pin is not None:
            self._in1 = DigitalOutputDevice(self._in1_pin)
        if self._in2_pin is not None:
            self._in2 = DigitalOutputDevice(self._in2_pin)
        self._apply_direction()

    def set_speed(self, percent: int) -> None:
        self._cancel_ramp()
        self._apply_speed(percent)

    def set_direction(self, clockwise: bool) -> None:
        self._cancel_ramp()
        self._clockwise = clockwise
        self._apply_direction()

    def set_direction_safe(self, clockwise: bool, target_speed: int | None = None) -> None:
        if self._clockwise == clockwise:
            if target_speed is not None:
                self.set_speed(target_speed)
            return
        restore = self._speed if target_speed is None else max(MIN_SPEED, min(MAX_SPEED, target_speed))
        self._pending_direction = clockwise
        self._pending_restore_speed = restore
        self._ramp_target = 0
        self._ramp_next_step_at = time.monotonic()

    def stop(self) -> None:
        self._cancel_ramp()
        self._speed = 0
        if self._pwm is not None:
            self._pwm.value = 0
        if self._in1 is not None:
            self._in1.off()
        if self._in2 is not None:
            self._in2.off()

    def brake(self) -> None:
        # NOTE: Active brake mode wiring depends on the H-bridge driver IC.
        # Verify against your driver datasheet (L298N / TB6612 / DRV8833 differ)
        # before relying on this for emergency stops; some drivers need PWM high.
        self._cancel_ramp()
        self._speed = 0
        if self._pwm is not None:
            self._pwm.value = 0
        if self._in1 is not None:
            self._in1.on()
        if self._in2 is not None:
            self._in2.on()

    def update(self) -> None:
        if self._ramp_target is None:
            return
        now = time.monotonic()
        if now < self._ramp_next_step_at:
            return

        step = self._config.ramp_step_percent
        delay = self._config.ramp_step_delay_s
        target = self._ramp_target
        current = self._speed
        if current < target:
            next_speed = min(current + step, target)
        elif current > target:
            next_speed = max(current - step, target)
        else:
            next_speed = target

        self._apply_speed(next_speed)

        if next_speed != target:
            self._ramp_next_step_at = now + delay
            return

        if self._pending_direction is not None and target == 0:
            self._clockwise = self._pending_direction
            self._apply_direction()
            self._pending_direction = None
            restore = self._pending_restore_speed
            self._pending_restore_speed = 0
            if restore > 0:
                self._ramp_target = max(restore, self._config.min_effective_percent)
                self._ramp_next_step_at = now + delay
                return

        self._ramp_target = None

    @property
    def speed(self) -> int:
        return self._speed

    @property
    def is_running(self) -> bool:
        return self._speed > 0

    @property
    def is_ramping(self) -> bool:
        return self._ramp_target is not None

    def cleanup(self) -> None:
        self.stop()
        if self._pwm is not None:
            self._pwm.close()
        if self._in1 is not None:
            self._in1.close()
        if self._in2 is not None:
            self._in2.close()

    def _apply_speed(self, percent: int) -> None:
        percent = max(MIN_SPEED, min(MAX_SPEED, percent))
        if percent > 0 and percent < self._config.min_effective_percent:
            percent = self._config.min_effective_percent
        self._speed = percent
        if self._pwm is not None:
            self._pwm.value = percent / 100.0

    def _cancel_ramp(self) -> None:
        self._ramp_target = None
        self._pending_direction = None
        self._pending_restore_speed = 0

    def _apply_direction(self) -> None:
        if self._in1 is not None and self._in2 is not None:
            if self._clockwise:
                self._in1.on()
                self._in2.off()
            else:
                self._in1.off()
                self._in2.on()
