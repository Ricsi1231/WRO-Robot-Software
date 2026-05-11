from __future__ import annotations

from unittest.mock import MagicMock

from wro.servo import ServoConfig, ServoDriver


def test_initial_angle_is_center() -> None:
    driver = ServoDriver(ServoConfig(center_angle=45.0))
    assert driver.get_angle() == 45.0


def test_init_returns_early_when_pin_is_none() -> None:
    driver = ServoDriver(ServoConfig(pin=None))
    driver.init()
    assert driver._servo is None


def test_set_angle_clamps_to_max() -> None:
    driver = ServoDriver(ServoConfig(min_angle=0.0, max_angle=180.0, center_angle=90.0))
    driver._servo = MagicMock()
    driver.set_angle(200.0)
    assert driver.get_angle() == 180.0


def test_set_angle_clamps_to_min() -> None:
    driver = ServoDriver(ServoConfig(min_angle=0.0, max_angle=180.0, center_angle=90.0))
    driver._servo = MagicMock()
    driver.set_angle(-30.0)
    assert driver.get_angle() == 0.0


def test_set_angle_maps_center_to_zero_normalized() -> None:
    driver = ServoDriver(ServoConfig(min_angle=0.0, max_angle=180.0, center_angle=90.0))
    mock_servo = MagicMock()
    driver._servo = mock_servo
    driver.set_angle(90.0)
    assert mock_servo.value == 0.0


def test_set_angle_maps_max_to_positive_one() -> None:
    driver = ServoDriver(ServoConfig(min_angle=0.0, max_angle=180.0, center_angle=90.0))
    mock_servo = MagicMock()
    driver._servo = mock_servo
    driver.set_angle(180.0)
    assert mock_servo.value == 1.0


def test_set_angle_maps_min_to_negative_one() -> None:
    driver = ServoDriver(ServoConfig(min_angle=0.0, max_angle=180.0, center_angle=90.0))
    mock_servo = MagicMock()
    driver._servo = mock_servo
    driver.set_angle(0.0)
    assert mock_servo.value == -1.0


def test_cleanup_is_safe_when_never_initialized() -> None:
    driver = ServoDriver(ServoConfig(pin=None))
    driver.cleanup()


def test_cleanup_closes_servo() -> None:
    driver = ServoDriver(ServoConfig(pin=18))
    mock_servo = MagicMock()
    driver._servo = mock_servo
    driver.cleanup()
    mock_servo.close.assert_called_once()
