from __future__ import annotations

from unittest.mock import MagicMock

from wro.config import PinConfig, ReflectanceConfig
from wro.reflectance_sensor import ReflectanceClass, ReflectanceSensor


def test_detected_class_unknown_when_nothing_started() -> None:
    sensor = ReflectanceSensor(ReflectanceConfig(), PinConfig())
    assert sensor.detected_class == ReflectanceClass.UNKNOWN


def test_orange_takes_priority_over_green_when_both_pressed() -> None:
    sensor = ReflectanceSensor(ReflectanceConfig(), PinConfig())
    orange = MagicMock(is_pressed=True)
    green = MagicMock(is_pressed=True)
    sensor._orange_input = orange
    sensor._green_input = green
    assert sensor.detected_class == ReflectanceClass.ORANGE


def test_green_detected_when_only_green_pressed() -> None:
    sensor = ReflectanceSensor(ReflectanceConfig(), PinConfig())
    sensor._orange_input = MagicMock(is_pressed=False)
    sensor._green_input = MagicMock(is_pressed=True)
    assert sensor.detected_class == ReflectanceClass.GREEN


def test_stop_closes_both_inputs_and_clears_state() -> None:
    sensor = ReflectanceSensor(ReflectanceConfig(), PinConfig())
    orange = MagicMock()
    green = MagicMock()
    sensor._orange_input = orange
    sensor._green_input = green
    sensor.stop()
    orange.close.assert_called_once()
    green.close.assert_called_once()
    assert sensor._orange_input is None
    assert sensor._green_input is None


def test_stop_is_safe_when_close_raises() -> None:
    sensor = ReflectanceSensor(ReflectanceConfig(), PinConfig())
    orange = MagicMock()
    orange.close.side_effect = RuntimeError("already closed")
    sensor._orange_input = orange
    sensor.stop()
    assert sensor._orange_input is None


def test_cleanup_is_safe_when_never_started() -> None:
    sensor = ReflectanceSensor(ReflectanceConfig(), PinConfig())
    sensor.cleanup()
    assert sensor.detected_class == ReflectanceClass.UNKNOWN
