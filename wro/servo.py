from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ServoConfig:
    pin: int | None = None
    min_pulse_ms: float = 1.0
    max_pulse_ms: float = 2.0
    min_angle: float = 0.0
    max_angle: float = 180.0
    center_angle: float = 90.0


class ServoDriver:
    def __init__(self, config: ServoConfig) -> None:
        self._config = config
        self._angle: float = config.center_angle
        self._servo: Any = None

    def init(self) -> None:
        if self._config.pin is None:
            return

        from gpiozero import Servo

        min_pw = self._config.min_pulse_ms / 1000.0
        max_pw = self._config.max_pulse_ms / 1000.0

        self._servo = Servo(
            self._config.pin,
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
