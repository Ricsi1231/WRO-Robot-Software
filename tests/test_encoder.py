from __future__ import annotations

import sys
import types
from unittest.mock import MagicMock

import pytest

from wro.config import EncoderConfig, PinConfig
from wro.encoder import Encoder


def _encoder(a_pin: int | None = 4, b_pin: int | None = 17) -> Encoder:
    pins = PinConfig(encoder_a=a_pin, encoder_b=b_pin)
    return Encoder(EncoderConfig(pulses_per_rev=12, ema_alpha=1.0), pins)


def test_position_is_zero_at_init() -> None:
    enc = _encoder()
    assert enc.position_ticks == 0
    assert enc.rpm == 0.0
    assert enc.healthy is False


def test_start_returns_early_when_no_pins() -> None:
    enc = Encoder(EncoderConfig(), PinConfig())
    enc.start()
    enc.stop()
    assert enc.healthy is False


def test_on_edge_increments_for_forward_quadrature() -> None:
    enc = _encoder(a_pin=4, b_pin=17)
    mock_pi = MagicMock()
    mock_pi.read.side_effect = lambda pin: 1 if pin == 4 else 0
    enc._pi = mock_pi
    enc._on_edge(gpio=4, level=1, tick=0)
    assert enc.position_ticks == 1


def test_on_edge_decrements_for_reverse_quadrature() -> None:
    enc = _encoder(a_pin=4, b_pin=17)
    mock_pi = MagicMock()
    mock_pi.read.return_value = 1
    enc._pi = mock_pi
    enc._on_edge(gpio=4, level=1, tick=0)
    assert enc.position_ticks == -1


def test_on_edge_b_channel_uses_inverted_rule() -> None:
    enc = _encoder(a_pin=4, b_pin=17)
    mock_pi = MagicMock()
    mock_pi.read.return_value = 1
    enc._pi = mock_pi
    enc._on_edge(gpio=17, level=1, tick=0)
    assert enc.position_ticks == 1


def test_on_edge_is_noop_when_pi_unavailable() -> None:
    enc = _encoder()
    enc._pi = None
    enc._on_edge(gpio=4, level=1, tick=0)
    assert enc.position_ticks == 0


def test_reset_position_clears_state() -> None:
    enc = _encoder()
    mock_pi = MagicMock()
    mock_pi.read.side_effect = lambda pin: 1 if pin == 4 else 0
    enc._pi = mock_pi
    enc._on_edge(gpio=4, level=1, tick=0)
    enc._on_edge(gpio=4, level=1, tick=0)
    assert enc.position_ticks == 2

    enc.reset_position()
    assert enc.position_ticks == 0
    assert enc.rpm == 0.0


def test_calc_rpm_computes_revolutions_per_minute() -> None:
    enc = _encoder()
    enc._running = True
    enc._last_calc_time = 0.0
    enc._ticks = 12 * 4
    enc._last_ticks = 0

    import time as _t

    original = _t.monotonic
    _t.monotonic = lambda: 1.0  # type: ignore[assignment]
    try:
        enc._calc_rpm()
    finally:
        _t.monotonic = original

    assert enc.rpm_raw == 60.0
    assert enc.rpm == 60.0
    enc._running = False
    if enc._timer is not None:
        enc._timer.cancel()


def test_start_logs_and_continues_when_pigpio_init_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_pigpio = types.ModuleType("pigpio")

    def failing_pi() -> object:
        raise RuntimeError("daemon not running")

    fake_pigpio.pi = failing_pi  # type: ignore[attr-defined]
    fake_pigpio.INPUT = 0  # type: ignore[attr-defined]
    fake_pigpio.PUD_UP = 0  # type: ignore[attr-defined]
    fake_pigpio.EITHER_EDGE = 0  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "pigpio", fake_pigpio)

    enc = _encoder()
    enc.start()
    try:
        assert enc.healthy is False
    finally:
        enc.stop()
