from __future__ import annotations

from unittest.mock import MagicMock

from wro.config import MotorConfig
from wro.motor_driver import MotorDriver


def _make_driver() -> tuple[MotorDriver, MagicMock, MagicMock, MagicMock]:
    config = MotorConfig(pwm_frequency=1_000)
    driver = MotorDriver(config, en_pin=12, in1_pin=5, in2_pin=6)

    mock_pwm = MagicMock()
    mock_in1 = MagicMock()
    mock_in2 = MagicMock()

    driver._pwm = mock_pwm
    driver._in1 = mock_in1
    driver._in2 = mock_in2

    return driver, mock_pwm, mock_in1, mock_in2


def test_set_speed() -> None:
    driver, mock_pwm, _, _ = _make_driver()
    driver.set_speed(50)
    assert driver.speed == 50
    assert mock_pwm.value == 0.5


def test_set_speed_clamped() -> None:
    driver, mock_pwm, _, _ = _make_driver()
    driver.set_speed(150)
    assert driver.speed == 100
    assert mock_pwm.value == 1.0


def test_direction_forward() -> None:
    driver, _, mock_in1, mock_in2 = _make_driver()
    driver._clockwise = False
    driver.set_direction(True)
    mock_in1.on.assert_called()
    mock_in2.off.assert_called()


def test_direction_backward() -> None:
    driver, _, mock_in1, mock_in2 = _make_driver()
    driver.set_direction(False)
    mock_in1.off.assert_called()
    mock_in2.on.assert_called()


def test_stop_coast() -> None:
    driver, mock_pwm, mock_in1, mock_in2 = _make_driver()
    driver.set_speed(50)
    driver.stop()
    assert driver.speed == 0
    assert mock_pwm.value == 0
    mock_in1.off.assert_called()
    mock_in2.off.assert_called()


def test_brake() -> None:
    driver, mock_pwm, mock_in1, mock_in2 = _make_driver()
    driver.set_speed(50)
    driver.brake()
    assert driver.speed == 0
    assert mock_pwm.value == 0
    mock_in1.on.assert_called()
    mock_in2.on.assert_called()


def test_is_running() -> None:
    driver, _, _, _ = _make_driver()
    assert not driver.is_running
    driver.set_speed(10)
    assert driver.is_running
    driver.stop()
    assert not driver.is_running
