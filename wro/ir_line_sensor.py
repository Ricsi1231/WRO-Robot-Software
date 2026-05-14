from __future__ import annotations

import contextlib
import threading
import time
from typing import Any

from wro.config import IrLineConfig, PinConfig


class IrLineSensor:
    def __init__(self, config: IrLineConfig, pins: PinConfig) -> None:
        self._config = config
        self._pins = pins
        self._input: Any = None
        self._lock = threading.Lock()
        self._count: int = 0
        self._last_detection_time: float = 0.0

    def start(self) -> None:
        if self._pins.ir_line is None:
            return

        from gpiozero import Button

        self._input = Button(
            self._pins.ir_line,
            pull_up=True,
            bounce_time=self._config.debounce_s,
        )
        self._input.when_pressed = self._on_detected

    def stop(self) -> None:
        if self._input is not None:
            with contextlib.suppress(Exception):
                self._input.when_pressed = None
            with contextlib.suppress(Exception):
                self._input.close()
            self._input = None
        with self._lock:
            self._count = 0
            self._last_detection_time = 0.0

    @property
    def is_detected(self) -> bool:
        if self._input is None:
            return False
        return bool(self._input.is_pressed)

    @property
    def detection_count(self) -> int:
        with self._lock:
            return self._count

    def reset_count(self) -> None:
        with self._lock:
            self._count = 0

    def cleanup(self) -> None:
        self.stop()

    def _on_detected(self) -> None:
        now = time.monotonic()
        with self._lock:
            if now - self._last_detection_time < self._config.detection_debounce_s:
                return
            self._last_detection_time = now
            self._count += 1
