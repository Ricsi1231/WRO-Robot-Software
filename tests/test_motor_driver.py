from __future__ import annotations

import time
from unittest.mock import MagicMock, patch

from wro.config import MotorConfig
from wro.motor_driver import MotorDriver


def _make_driver(config: MotorConfig | None = None) -> tuple[MotorDriver, MagicMock, MagicMock, MagicMock]:
    config = config or MotorConfig(pwm_frequency=1_000)
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


def test_set_direction_re_applies_pins_after_stop() -> None:
    driver, _, mock_in1, mock_in2 = _make_driver()
    driver.set_direction(True)
    driver.stop()
    mock_in1.reset_mock()
    mock_in2.reset_mock()

    driver.set_direction(True)

    mock_in1.on.assert_called()
    mock_in2.off.assert_called()


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


def test_update_is_noop_when_no_ramp_in_progress() -> None:
    driver, mock_pwm, _, _ = _make_driver()
    driver.set_speed(50)
    mock_pwm.reset_mock()
    driver.update()
    assert not driver.is_ramping
    assert mock_pwm.value == 0.5


def test_set_direction_safe_starts_rampdown_does_not_block() -> None:
    driver, _, _, _ = _make_driver(MotorConfig(ramp_step_percent=5, ramp_step_delay_s=0.02))
    driver._clockwise = True
    driver.set_speed(40)
    with patch.object(time, "monotonic", return_value=1000.0):
        driver.set_direction_safe(False)
    assert driver.is_ramping
    assert driver.speed == 40
    assert driver._clockwise is True


def test_full_reverse_sequence_rampdown_flip_rampup() -> None:
    config = MotorConfig(ramp_step_percent=10, ramp_step_delay_s=0.02)
    driver, _, mock_in1, mock_in2 = _make_driver(config)
    driver._clockwise = True
    driver.set_speed(20)
    mock_in1.reset_mock()
    mock_in2.reset_mock()

    times = [1000.0 + i * 0.02 for i in range(20)]
    with patch.object(time, "monotonic", side_effect=times):
        driver.set_direction_safe(False, target_speed=30)
        for _ in range(15):
            driver.update()

    assert not driver.is_ramping
    assert driver._clockwise is False
    assert driver.speed == 30
    mock_in1.off.assert_called()
    mock_in2.on.assert_called()


def test_set_speed_cancels_in_progress_ramp() -> None:
    driver, _, _, _ = _make_driver(MotorConfig(ramp_step_percent=5, ramp_step_delay_s=0.02))
    driver._clockwise = True
    driver.set_speed(40)
    with patch.object(time, "monotonic", return_value=1000.0):
        driver.set_direction_safe(False, target_speed=30)
        driver.set_speed(50)

    assert not driver.is_ramping
    assert driver.speed == 50
    assert driver._clockwise is True


def test_stop_cancels_ramp() -> None:
    driver, _, _, _ = _make_driver()
    driver._clockwise = True
    driver.set_speed(40)
    with patch.object(time, "monotonic", return_value=1000.0):
        driver.set_direction_safe(False, target_speed=30)
        driver.stop()
    assert not driver.is_ramping
    assert driver.speed == 0


def test_set_direction_safe_same_direction_applies_target_speed() -> None:
    driver, _, _, _ = _make_driver()
    driver._clockwise = True
    driver.set_speed(20)
    driver.set_direction_safe(True, target_speed=60)
    assert not driver.is_ramping
    assert driver.speed == 60
    assert driver._clockwise is True


def test_update_only_advances_after_delay() -> None:
    driver, _, _, _ = _make_driver(MotorConfig(ramp_step_percent=10, ramp_step_delay_s=0.05))
    driver._clockwise = True
    driver.set_speed(50)
    with patch.object(time, "monotonic", side_effect=[1000.0, 1000.01, 1000.02]):
        driver.set_direction_safe(False)
        driver.update()
    assert driver.speed == 40
    with patch.object(time, "monotonic", return_value=1000.03):
        driver.update()
    assert driver.speed == 40
