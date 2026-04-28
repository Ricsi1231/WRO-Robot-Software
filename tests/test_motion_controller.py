from __future__ import annotations

from unittest.mock import MagicMock

from wro.config import MotionConfig, SteeringConfig
from wro.motion_controller import MotionController


def _make_controller() -> tuple[MotionController, MagicMock, MagicMock]:
    drive = MagicMock()
    drive.is_running = False
    steer = MagicMock()
    config = MotionConfig()
    steering_config = SteeringConfig(max_angle=30.0, min_speed_percent=30.0, max_speed_percent=100.0)
    mc = MotionController(config, drive, steer, steering_config)
    return mc, drive, steer


def test_set_velocity_forward() -> None:
    mc, drive, _ = _make_controller()
    mc.set_velocity(0.5)
    drive.set_speed.assert_called_with(50)
    assert mc.velocity == 0.5


def test_set_velocity_zero_stops() -> None:
    mc, drive, _ = _make_controller()
    mc.set_velocity(0.0)
    drive.stop.assert_called()
    assert mc.velocity == 0.0


def test_set_steering_right() -> None:
    mc, _, steer = _make_controller()
    mc.set_steering_angle(15.0)
    steer.set_direction.assert_called_with(True)
    steer.set_speed.assert_called()
    assert mc.steering_angle == 15.0


def test_set_steering_left() -> None:
    mc, _, steer = _make_controller()
    mc.set_steering_angle(-15.0)
    steer.set_direction.assert_called_with(False)
    steer.set_speed.assert_called()
    assert mc.steering_angle == -15.0


def test_set_steering_zero_stops() -> None:
    mc, _, steer = _make_controller()
    mc.set_steering_angle(0.0)
    steer.stop.assert_called()
    assert mc.steering_angle == 0.0


def test_steering_speed_interpolation() -> None:
    mc, _, steer = _make_controller()
    mc.set_steering_angle(30.0)
    steer.set_speed.assert_called_with(100)

    steer.reset_mock()
    mc.set_steering_angle(15.0)
    steer.set_speed.assert_called_with(65)


def test_stop_stops_both() -> None:
    mc, drive, steer = _make_controller()
    mc.set_velocity(0.5)
    mc.set_steering_angle(10.0)
    mc.stop()
    drive.stop.assert_called()
    steer.stop.assert_called()
    assert mc.velocity == 0.0


def test_emergency_stop_brakes_both() -> None:
    mc, drive, steer = _make_controller()
    mc.emergency_stop()
    drive.brake.assert_called()
    steer.brake.assert_called()
