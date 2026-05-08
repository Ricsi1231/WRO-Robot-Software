from __future__ import annotations

from unittest.mock import MagicMock, PropertyMock

from wro.config import RaceConfig
from wro.race_controller import RaceController, RaceState
from wro.reflectance_sensor import ReflectanceClass
from wro.vision import DetectionResult

NO_DETECTION = DetectionResult(0, 0, False, False)
RED_DETECTION = DetectionResult(1000, 0, True, False)
GREEN_DETECTION = DetectionResult(0, 1000, False, True)


def _make_controller(
    config: RaceConfig | None = None,
) -> tuple[RaceController, MagicMock, MagicMock, MagicMock, MagicMock]:
    if config is None:
        config = RaceConfig()

    motion = MagicMock()
    encoder = MagicMock()
    reflectance = MagicMock()
    type(reflectance).detected_class = PropertyMock(return_value=ReflectanceClass.UNKNOWN)
    pid = MagicMock()
    camera = MagicMock()
    type(camera).latest_detection = PropertyMock(return_value=NO_DETECTION)
    ultrasonic = MagicMock()
    type(ultrasonic).is_close = PropertyMock(return_value=False)

    rc = RaceController(config, motion, encoder, reflectance, pid, camera, ultrasonic)
    rc.start()
    return rc, motion, camera, reflectance, ultrasonic


def test_initial_state_is_idle() -> None:
    rc, _, _, _, _ = _make_controller()
    assert rc.state == RaceState.IDLE


def test_start_signal_transitions_to_running() -> None:
    rc, motion, _, _, _ = _make_controller()
    rc.on_start_signal()
    rc.update()
    assert rc.state == RaceState.RUNNING
    motion.set_velocity.assert_called_with(0.5)


def test_no_transition_without_start_signal() -> None:
    rc, _, _, _, _ = _make_controller()
    rc.update()
    assert rc.state == RaceState.IDLE


def test_red_pillar_steers_right_when_close() -> None:
    rc, motion, camera, _, ultrasonic = _make_controller()
    rc.on_start_signal()
    rc.update()
    motion.reset_mock()

    type(camera).latest_detection = PropertyMock(return_value=RED_DETECTION)
    type(ultrasonic).is_close = PropertyMock(return_value=True)
    rc.update()

    motion.set_steering_angle.assert_called_with(15.0)
    motion.set_velocity.assert_called_with(0.3)


def test_green_pillar_steers_left_when_close() -> None:
    rc, motion, camera, _, ultrasonic = _make_controller()
    rc.on_start_signal()
    rc.update()
    motion.reset_mock()

    type(camera).latest_detection = PropertyMock(return_value=GREEN_DETECTION)
    type(ultrasonic).is_close = PropertyMock(return_value=True)
    rc.update()

    motion.set_steering_angle.assert_called_with(-15.0)


def test_red_pillar_does_not_steer_when_not_close() -> None:
    rc, motion, camera, _, ultrasonic = _make_controller()
    rc.on_start_signal()
    rc.update()
    motion.reset_mock()

    type(camera).latest_detection = PropertyMock(return_value=RED_DETECTION)
    type(ultrasonic).is_close = PropertyMock(return_value=False)
    rc.update()

    motion.set_steering_angle.assert_not_called()
    motion.set_velocity.assert_not_called()


def test_close_obstacle_without_color_does_not_start_pillar_avoidance() -> None:
    rc, motion, _, _, ultrasonic = _make_controller()
    rc.on_start_signal()
    rc.update()
    motion.reset_mock()

    type(ultrasonic).is_close = PropertyMock(return_value=True)
    rc.update()

    motion.set_steering_angle.assert_not_called()
    motion.set_velocity.assert_not_called()


def test_stopping_after_three_laps() -> None:
    config = RaceConfig(total_laps=3, corners_per_lap=4, corner_debounce_s=0.0, corner_steer_duration_s=0.0)
    rc, motion, _, reflectance, _ = _make_controller(config)
    rc.on_start_signal()
    rc.update()

    type(reflectance).detected_class = PropertyMock(return_value=ReflectanceClass.ORANGE)

    for _ in range(30):
        rc.update()
        if rc.state in (RaceState.STOPPING, RaceState.FINISHED):
            break

    assert rc.state in (RaceState.STOPPING, RaceState.FINISHED)


def test_finished_after_stopping() -> None:
    config = RaceConfig(total_laps=1, corners_per_lap=1, corner_debounce_s=0.0, corner_steer_duration_s=0.0)
    rc, motion, _, reflectance, _ = _make_controller(config)
    rc.on_start_signal()
    rc.update()

    type(reflectance).detected_class = PropertyMock(return_value=ReflectanceClass.ORANGE)
    rc.update()

    if rc.state == RaceState.STOPPING:
        rc.update()

    assert rc.state == RaceState.FINISHED
    motion.stop.assert_called()


def test_lap_count_increments() -> None:
    config = RaceConfig(corners_per_lap=2, corner_debounce_s=0.0, corner_steer_duration_s=0.0)
    rc, _, _, reflectance, _ = _make_controller(config)
    rc.on_start_signal()
    rc.update()

    type(reflectance).detected_class = PropertyMock(return_value=ReflectanceClass.ORANGE)

    for _ in range(10):
        rc.update()
        if rc.corner_count >= 2:
            break

    assert rc.corner_count >= 2
    assert rc.lap_count >= 1
