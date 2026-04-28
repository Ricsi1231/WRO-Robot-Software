from __future__ import annotations

import threading
import time
from typing import Any

from wro.config import EncoderConfig, PinConfig


class Encoder:
    def __init__(self, config: EncoderConfig, pins: PinConfig) -> None:
        self._config = config
        self._pins = pins
        self._ticks: int = 0
        self._last_ticks: int = 0
        self._rpm: float = 0.0
        self._rpm_raw: float = 0.0
        self._lock = threading.Lock()
        self._running = False
        self._timer: threading.Timer | None = None
        self._last_calc_time: float = 0.0
        self._pi: Any = None
        self._cb_a: Any = None
        self._cb_b: Any = None

    def start(self) -> None:
        if self._pins.encoder_a is None or self._pins.encoder_b is None:
            return
        try:
            import pigpio

            self._pi = pigpio.pi()
            pi = self._pi
            pi.set_mode(self._pins.encoder_a, pigpio.INPUT)  # type: ignore[union-attr]
            pi.set_mode(self._pins.encoder_b, pigpio.INPUT)  # type: ignore[union-attr]
            pi.set_pull_up_down(self._pins.encoder_a, pigpio.PUD_UP)  # type: ignore[union-attr]
            pi.set_pull_up_down(self._pins.encoder_b, pigpio.PUD_UP)  # type: ignore[union-attr]
            self._cb_a = pi.callback(self._pins.encoder_a, pigpio.EITHER_EDGE, self._on_edge)  # type: ignore[union-attr]
            self._cb_b = pi.callback(self._pins.encoder_b, pigpio.EITHER_EDGE, self._on_edge)  # type: ignore[union-attr]
        except Exception:
            self._pi = None

        self._running = True
        self._last_calc_time = time.monotonic()
        self._schedule_rpm_calc()

    def stop(self) -> None:
        self._running = False
        if self._timer is not None:
            self._timer.cancel()
        if self._cb_a is not None:
            self._cb_a.cancel()  # type: ignore[union-attr]
        if self._cb_b is not None:
            self._cb_b.cancel()  # type: ignore[union-attr]
        if self._pi is not None:
            self._pi.stop()  # type: ignore[union-attr]

    def reset_position(self) -> None:
        with self._lock:
            self._ticks = 0
            self._last_ticks = 0
            self._rpm = 0.0
            self._rpm_raw = 0.0

    @property
    def position_ticks(self) -> int:
        with self._lock:
            return self._ticks

    @property
    def rpm(self) -> float:
        with self._lock:
            return self._rpm

    @property
    def rpm_raw(self) -> float:
        with self._lock:
            return self._rpm_raw

    def cleanup(self) -> None:
        self.stop()

    def _on_edge(self, gpio: int, level: int, tick: int) -> None:
        if self._pi is None or self._pins.encoder_a is None or self._pins.encoder_b is None:
            return
        a = self._pi.read(self._pins.encoder_a)  # type: ignore[union-attr]
        b = self._pi.read(self._pins.encoder_b)  # type: ignore[union-attr]
        with self._lock:
            if gpio == self._pins.encoder_a:
                self._ticks += 1 if a != b else -1
            else:
                self._ticks += 1 if a == b else -1

    def _schedule_rpm_calc(self) -> None:
        if not self._running:
            return
        self._timer = threading.Timer(self._config.rpm_calc_period_s, self._calc_rpm)
        self._timer.daemon = True
        self._timer.start()

    def _calc_rpm(self) -> None:
        now = time.monotonic()
        dt = now - self._last_calc_time
        self._last_calc_time = now

        if dt <= 0:
            self._schedule_rpm_calc()
            return

        with self._lock:
            delta = self._ticks - self._last_ticks
            self._last_ticks = self._ticks

        counts_per_rev = self._config.pulses_per_rev * 4
        revolutions = delta / counts_per_rev
        raw_rpm = revolutions / dt * 60.0

        alpha = self._config.ema_alpha
        with self._lock:
            self._rpm_raw = raw_rpm
            self._rpm = alpha * raw_rpm + (1.0 - alpha) * self._rpm

        self._schedule_rpm_calc()
