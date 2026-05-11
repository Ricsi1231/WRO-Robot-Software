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

    def __post_init__(self) -> None:
        if self.min_pulse_ms <= 0 or self.max_pulse_ms <= 0:
            raise ValueError(f"pulse widths must be > 0, got min={self.min_pulse_ms}, max={self.max_pulse_ms}")
        if self.min_pulse_ms >= self.max_pulse_ms:
            raise ValueError(
                f"min_pulse_ms must be < max_pulse_ms, got min={self.min_pulse_ms}, max={self.max_pulse_ms}"
            )
        if self.min_angle >= self.max_angle:
            raise ValueError(f"min_angle must be < max_angle, got min={self.min_angle}, max={self.max_angle}")
        if not self.min_angle <= self.center_angle <= self.max_angle:
            raise ValueError(
                f"center_angle must lie in [min_angle, max_angle], got center={self.center_angle}, "
                f"min={self.min_angle}, max={self.max_angle}"
            )


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
