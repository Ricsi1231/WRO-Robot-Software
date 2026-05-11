from __future__ import annotations

import logging
from typing import Any

from wro.config import PinConfig, UltrasonicConfig

_logger = logging.getLogger(__name__)


class UltrasonicSensor:
    def __init__(self, config: UltrasonicConfig, pins: PinConfig) -> None:
        self._config = config
        self._pins = pins
        self._sensor: Any = None
        self._distance_cm: float | None = None
        self._consecutive_failures: int = 0

    def start(self) -> None:
        if self._pins.ultrasonic_trigger is None or self._pins.ultrasonic_echo is None:
            return

        from gpiozero import DistanceSensor

        self._sensor = DistanceSensor(
            echo=self._pins.ultrasonic_echo,
            trigger=self._pins.ultrasonic_trigger,
            max_distance=self._config.max_distance_cm / 100.0,
        )
        self._consecutive_failures = 0

    def stop(self) -> None:
        if self._sensor is not None:
            self._sensor.close()
            self._sensor = None
        self._distance_cm = None
        self._consecutive_failures = 0

    @property
    def distance_cm(self) -> float | None:
        if self._sensor is None:
            return None

        try:
            measured_cm = float(self._sensor.distance) * 100.0
        except Exception:
            self._consecutive_failures += 1
            _logger.warning(
                "Ultrasonic read failed (consecutive=%d)",
                self._consecutive_failures,
                exc_info=True,
            )
            if self._consecutive_failures >= self._config.max_consecutive_failures:
                self._distance_cm = None
                return None
            return self._distance_cm

        self._consecutive_failures = 0
        if self._distance_cm is None:
            self._distance_cm = measured_cm
        else:
            alpha = self._config.ema_alpha
            self._distance_cm = alpha * measured_cm + (1.0 - alpha) * self._distance_cm

        return self._distance_cm

    @property
    def is_close(self) -> bool:
        distance = self.distance_cm
        return distance is not None and distance <= self._config.close_distance_cm

    def cleanup(self) -> None:
        self.stop()
