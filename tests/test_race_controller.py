from __future__ import annotations

from unittest.mock import MagicMock, PropertyMock

from wro.config import IrLineConfig, RaceConfig
from wro.race_controller import RaceController, RaceState
from wro.reflectance_sensor import ReflectanceClass
from wro.vision import DetectionResult

NO_DETECTION = DetectionResult(0, 0, False, False)
RED_DETECTION = DetectionResult(1000, 0, True, False)
GREEN_DETECTION = DetectionResult(0, 1000, False, True)


def _make_controller(
    config: RaceConfig | None = None,
    ir_config: IrLineConfig | None = None,
) -> tuple[RaceController, MagicMock, MagicMock, MagicMock, MagicMock, MagicMock]:
    if config is None:
        config = RaceConfig()
    if ir_config is None:
        ir_config = IrLineConfig()

    motion = MagicMock()
    encoder = MagicMock()
    reflectance = MagicMock()
    type(reflectance).detected_class = PropertyMock(return_value=ReflectanceClass.UNKNOWN)
    pid = MagicMock()
    camera = MagicMock()
    type(camera).latest_detection = PropertyMock(return_value=NO_DETECTION)
    ultrasonic = MagicMock()
    type(ultrasonic).is_close = PropertyMock(return_value=False)
    ir_line = MagicMock()
    type(ir_line).detection_count = PropertyMock(return_value=0)

    rc = RaceController(config, motion, encoder, reflectance, pid, camera, ultrasonic, ir_line, ir_config)
    rc.start()
    return rc, motion, camera, reflectance, ultrasonic, ir_line


def test_initial_state_is_idle() -> None:
    rc, _, _, _, _, _ = _make_controller()
    assert rc.state == RaceState.IDLE


def test_start_signal_transitions_to_running() -> None:
    rc, motion, _, _, _, _ = _make_controller()
    rc.on_start_signal()
    rc.update()
    assert rc.state == RaceState.RUNNING
    motion.set_velocity.assert_called_with(0.5)


def test_no_transition_without_start_signal() -> None:
    rc, _, _, _, _, _ = _make_controller()
    rc.update()
    assert rc.state == RaceState.IDLE


def test_red_pillar_steers_right_when_close() -> None:
    rc, motion, camera, _, ultrasonic, _ = _make_controller()
    rc.on_start_signal()
    rc.update()
    motion.reset_mock()

    type(camera).latest_detection = PropertyMock(return_value=RED_DETECTION)
    type(ultrasonic).is_close = PropertyMock(return_value=True)
    rc.update()

    motion.set_steering_angle.assert_called_with(15.0)
    motion.set_velocity.assert_called_with(0.3)


def test_green_pillar_steers_left_when_close() -> None:
    rc, motion, camera, _, ultrasonic, _ = _make_controller()
    rc.on_start_signal()
    rc.update()
    motion.reset_mock()

    type(camera).latest_detection = PropertyMock(return_value=GREEN_DETECTION)
    type(ultrasonic).is_close = PropertyMock(return_value=True)
    rc.update()

    motion.set_steering_angle.assert_called_with(-15.0)


def test_red_pillar_does_not_steer_when_not_close() -> None:
    rc, motion, camera, _, ultrasonic, _ = _make_controller()
    rc.on_start_signal()
    rc.update()
    motion.reset_mock()

    type(camera).latest_detection = PropertyMock(return_value=RED_DETECTION)
    type(ultrasonic).is_close = PropertyMock(return_value=False)
    rc.update()

    motion.set_steering_angle.assert_not_called()
    motion.set_velocity.assert_not_called()


def test_close_obstacle_without_color_does_not_start_pillar_avoidance() -> None:
    rc, motion, _, _, ultrasonic, _ = _make_controller()
    rc.on_start_signal()
    rc.update()
    motion.reset_mock()

    type(ultrasonic).is_close = PropertyMock(return_value=True)
    rc.update()

    motion.set_steering_angle.assert_not_called()
    motion.set_velocity.assert_not_called()


def test_stopping_after_three_laps() -> None:
    config = RaceConfig(total_laps=3, corners_per_lap=4, corner_debounce_s=0.0, corner_steer_duration_s=0.0)
    rc, _motion, _, reflectance, _, _ = _make_controller(config)
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
    rc, motion, _, reflectance, _, _ = _make_controller(config)
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
    rc, _, _, reflectance, _, _ = _make_controller(config)
    rc.on_start_signal()
    rc.update()

    type(reflectance).detected_class = PropertyMock(return_value=ReflectanceClass.ORANGE)

    for _ in range(10):
        rc.update()
        if rc.corner_count >= 2:
            break

    assert rc.corner_count >= 2
    assert rc.lap_count >= 1


def test_start_resets_ir_detection_count() -> None:
    _rc, _, _, _, _, ir_line = _make_controller()
    ir_line.reset_count.assert_called()


def test_two_ir_detections_trigger_turn() -> None:
    rc, motion, _, _, _, ir_line = _make_controller()
    rc.on_start_signal()
    rc.update()
    motion.reset_mock()
    ir_line.reset_count.reset_mock()

    type(ir_line).detection_count = PropertyMock(return_value=2)
    rc.update()

    motion.set_steering_angle.assert_called_with(25.0)
    motion.set_velocity.assert_called_with(0.3)
    ir_line.reset_count.assert_called_once()
    assert rc._in_ir_turn is True


def test_ir_turn_uses_negative_angle_when_counter_clockwise() -> None:
    rc, motion, _, _, _, ir_line = _make_controller(config=RaceConfig(clockwise=False))
    rc.on_start_signal()
    rc.update()
    motion.reset_mock()

    type(ir_line).detection_count = PropertyMock(return_value=2)
    rc.update()

    motion.set_steering_angle.assert_called_with(-25.0)


def test_ir_turn_does_not_trigger_below_threshold() -> None:
    rc, motion, _, _, _, ir_line = _make_controller()
    rc.on_start_signal()
    rc.update()
    motion.reset_mock()
    ir_line.reset_count.reset_mock()

    type(ir_line).detection_count = PropertyMock(return_value=1)
    rc.update()

    ir_line.reset_count.assert_not_called()
    assert rc._in_ir_turn is False


def test_ir_turn_ends_after_duration() -> None:
    ir_config = IrLineConfig(turn_duration_s=0.0)
    rc, motion, _, _, _, ir_line = _make_controller(ir_config=ir_config)
    rc.on_start_signal()
    rc.update()

    type(ir_line).detection_count = PropertyMock(return_value=2)
    rc.update()
    assert rc._in_ir_turn is True

    type(ir_line).detection_count = PropertyMock(return_value=0)
    motion.reset_mock()
    rc.update()

    assert rc._in_ir_turn is False
    motion.set_steering_angle.assert_called_with(0.0)
    motion.set_velocity.assert_called_with(0.5)


def test_ir_turn_does_not_increment_corner_or_lap_count() -> None:
    rc, _, _, _, _, ir_line = _make_controller()
    rc.on_start_signal()
    rc.update()

    type(ir_line).detection_count = PropertyMock(return_value=2)
    rc.update()

    assert rc.corner_count == 0
    assert rc.lap_count == 0


def test_ir_turn_suppressed_during_pillar_avoidance() -> None:
    rc, motion, camera, _, ultrasonic, ir_line = _make_controller()
    rc.on_start_signal()
    rc.update()

    type(camera).latest_detection = PropertyMock(return_value=RED_DETECTION)
    type(ultrasonic).is_close = PropertyMock(return_value=True)
    rc.update()
    assert rc._in_avoidance_maneuver is True

    motion.reset_mock()
    ir_line.reset_count.reset_mock()
    type(ir_line).detection_count = PropertyMock(return_value=2)
    rc.update()

    ir_line.reset_count.assert_not_called()
    assert rc._in_ir_turn is False
