from __future__ import annotations

import time
from unittest.mock import MagicMock, patch

from wro.config import IrLineConfig, PinConfig
from wro.ir_line_sensor import IrLineSensor


def _sensor(detection_debounce_s: float = 0.30) -> IrLineSensor:
    return IrLineSensor(
        IrLineConfig(detection_debounce_s=detection_debounce_s),
        PinConfig(ir_line=22),
    )


def test_initial_state() -> None:
    sensor = _sensor()
    assert sensor.detection_count == 0
    assert sensor.is_detected is False


def test_start_is_noop_when_pin_is_none() -> None:
    sensor = IrLineSensor(IrLineConfig(), PinConfig(ir_line=None))
    sensor.start()
    assert sensor._input is None
    assert sensor.is_detected is False


def test_on_detected_increments_count() -> None:
    sensor = _sensor()
    with patch.object(time, "monotonic", return_value=1000.0):
        sensor._on_detected()
    assert sensor.detection_count == 1


def test_on_detected_within_debounce_window_does_not_increment() -> None:
    sensor = _sensor(detection_debounce_s=0.30)
    with patch.object(time, "monotonic", side_effect=[1000.0, 1000.10]):
        sensor._on_detected()
        sensor._on_detected()
    assert sensor.detection_count == 1


def test_on_detected_after_debounce_window_increments() -> None:
    sensor = _sensor(detection_debounce_s=0.30)
    with patch.object(time, "monotonic", side_effect=[1000.0, 1000.50]):
        sensor._on_detected()
        sensor._on_detected()
    assert sensor.detection_count == 2


def test_reset_count_clears_counter() -> None:
    sensor = _sensor()
    with patch.object(time, "monotonic", side_effect=[1000.0, 1000.50, 1001.0]):
        sensor._on_detected()
        sensor._on_detected()
    assert sensor.detection_count == 2
    sensor.reset_count()
    assert sensor.detection_count == 0


def test_is_detected_reflects_input_pressed() -> None:
    sensor = _sensor()
    sensor._input = MagicMock(is_pressed=True)
    assert sensor.is_detected is True
    sensor._input.is_pressed = False
    assert sensor.is_detected is False


def test_stop_closes_input_and_clears_counter() -> None:
    sensor = _sensor()
    sensor._input = MagicMock()
    with patch.object(time, "monotonic", return_value=1000.0):
        sensor._on_detected()
    assert sensor.detection_count == 1

    sensor.stop()
    assert sensor._input is None
    assert sensor.detection_count == 0


def test_stop_is_safe_when_input_close_raises() -> None:
    sensor = _sensor()
    bad = MagicMock()
    bad.close.side_effect = RuntimeError("already closed")
    sensor._input = bad
    sensor.stop()
    assert sensor._input is None


def test_cleanup_safe_when_never_started() -> None:
    sensor = _sensor()
    sensor.cleanup()
    assert sensor.detection_count == 0
    assert sensor.is_detected is False
