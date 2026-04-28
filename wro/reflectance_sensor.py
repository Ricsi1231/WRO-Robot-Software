from __future__ import annotations

import enum
from typing import Any

from wro.config import PinConfig, ReflectanceConfig


class ReflectanceClass(enum.Enum):
    UNKNOWN = 0
    ORANGE = 1
    GREEN = 2


class ReflectanceSensor:
    def __init__(self, config: ReflectanceConfig, pins: PinConfig) -> None:
        self._config = config
        self._pins = pins
        self._orange_input: Any = None
        self._green_input: Any = None

    def start(self) -> None:
        from gpiozero import Button

        if self._pins.reflectance_orange is not None:
            self._orange_input = Button(self._pins.reflectance_orange, bounce_time=self._config.debounce_s)
        if self._pins.reflectance_green is not None:
            self._green_input = Button(self._pins.reflectance_green, bounce_time=self._config.debounce_s)

    def stop(self) -> None:
        if self._orange_input is not None:
            self._orange_input.close()
            self._orange_input = None
        if self._green_input is not None:
            self._green_input.close()
            self._green_input = None

    @property
    def detected_class(self) -> ReflectanceClass:
        if self._orange_input is not None and self._orange_input.is_pressed:
            return ReflectanceClass.ORANGE
        if self._green_input is not None and self._green_input.is_pressed:
            return ReflectanceClass.GREEN
        return ReflectanceClass.UNKNOWN

    def cleanup(self) -> None:
        self.stop()
