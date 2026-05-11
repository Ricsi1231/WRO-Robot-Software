from __future__ import annotations

import contextlib
from unittest.mock import MagicMock

from wro.config import PinConfig
from wro.robot import Robot


def _mock_subcomponents(robot: Robot) -> dict[str, MagicMock]:
    mocks = {
        "camera": MagicMock(),
        "reflectance": MagicMock(),
        "ultrasonic": MagicMock(),
        "encoder": MagicMock(),
        "motion": MagicMock(),
        "race": MagicMock(),
    }
    robot._camera = mocks["camera"]
    robot._reflectance = mocks["reflectance"]
    robot._ultrasonic = mocks["ultrasonic"]
    robot._encoder = mocks["encoder"]
    robot._motion = mocks["motion"]
    robot._race = mocks["race"]
    return mocks


def test_constructor_with_default_none_pins_does_not_raise() -> None:
    Robot(pins=PinConfig())


def test_shutdown_flips_running_and_does_not_raise() -> None:
    robot = Robot(pins=PinConfig())
    robot._running = True
    robot.shutdown(_signum=2)
    assert robot._running is False


def test_cleanup_invokes_stop_on_each_subcomponent() -> None:
    robot = Robot(pins=PinConfig())
    mocks = _mock_subcomponents(robot)
    robot._cleanup()
    mocks["camera"].stop.assert_called_once()
    mocks["reflectance"].stop.assert_called_once()
    mocks["ultrasonic"].stop.assert_called_once()
    mocks["encoder"].stop.assert_called_once()
    mocks["motion"].stop.assert_called_once()
    mocks["motion"].cleanup.assert_called_once()


def test_cleanup_is_idempotent() -> None:
    robot = Robot(pins=PinConfig())
    mocks = _mock_subcomponents(robot)
    robot._cleanup()
    robot._cleanup()
    assert mocks["camera"].stop.call_count == 1
    assert mocks["motion"].cleanup.call_count == 1


def test_cleanup_continues_when_a_subcomponent_raises() -> None:
    robot = Robot(pins=PinConfig())
    mocks = _mock_subcomponents(robot)
    mocks["camera"].stop.side_effect = RuntimeError("camera fault")
    robot._cleanup()
    mocks["reflectance"].stop.assert_called_once()
    mocks["motion"].cleanup.assert_called_once()


def test_run_loop_exits_when_running_flips_false_and_calls_cleanup() -> None:
    robot = Robot(pins=PinConfig())
    mocks = _mock_subcomponents(robot)

    def stop_after_first_call() -> None:
        robot._running = False

    mocks["race"].update.side_effect = stop_after_first_call

    robot.run()

    mocks["race"].update.assert_called_once()
    mocks["motion"].tick.assert_called_once()
    mocks["motion"].cleanup.assert_called_once()


def test_run_cleans_up_even_when_race_raises() -> None:
    robot = Robot(pins=PinConfig())
    mocks = _mock_subcomponents(robot)
    mocks["race"].update.side_effect = RuntimeError("boom")

    with contextlib.suppress(RuntimeError):
        robot.run()

    mocks["motion"].cleanup.assert_called_once()


def test_on_start_signal_forwards_to_race() -> None:
    robot = Robot(pins=PinConfig())
    mocks = _mock_subcomponents(robot)
    robot.on_start_signal()
    mocks["race"].on_start_signal.assert_called_once()
