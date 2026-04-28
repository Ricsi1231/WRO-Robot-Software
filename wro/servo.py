from __future__ import annotations

from typing import Any

from wro.config import PinConfig, ServoConfig


class ServoDriver:
    def __init__(self, config: ServoConfig, pins: PinConfig) -> None:
        self._config = config
        self._pins = pins
        self._angle: float = config.center_angle
        self._servo: Any = None

    def init(self) -> None:
        if self._pins.servo is None:
            return

        from gpiozero import Servo

        min_pw = self._config.min_pulse_ms / 1000.0
        max_pw = self._config.max_pulse_ms / 1000.0

        self._servo = Servo(
            self._pins.servo,
            min_pulse_width=min_pw,
            max_pulse_width=max_pw,
        )
        self.set_angle(self._config.center_angle)

    def set_angle(self, angle_deg: float) -> None:
        angle_deg = max(self._config.min_angle, min(self._config.max_angle, angle_deg))
        self._angle = angle_deg
        if self._servo is not None:
            normalized = (angle_deg - self._config.min_angle) / (self._config.max_angle - self._config.min_angle)
            self._servo.value = normalized * 2.0 - 1.0

    def get_angle(self) -> float:
        return self._angle

    def cleanup(self) -> None:
        if self._servo is not None:
            self._servo.close()
