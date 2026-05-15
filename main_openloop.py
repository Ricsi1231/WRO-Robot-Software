from __future__ import annotations

import signal
import time
from typing import Any

from component_tests.hardware_config import TEST_PINS
from wro.config import MotionConfig, MotorConfig, SteeringConfig
from wro.motion_controller import MotionController
from wro.motor_driver import MotorDriver

FORWARD_DURATIONS_S: tuple[float, float, float, float] = (8.0, 8.0, 8.0, 8.0)
LEFT_DURATION_S: float = 0.6
CENTER_DURATION_S: float = 0.08
FORWARD_VELOCITY: float = 1.0
LEFT_VELOCITY: float = 0.5
COUNTDOWN_S: int = 3
SLEEP_TICK_S: float = 0.05

_running = True


def _request_stop(_signum: int = 0, _frame: Any = None) -> None:
    global _running
    _running = False


def _sleep_interruptible(duration_s: float) -> None:
    end = time.monotonic() + duration_s
    while _running:
        remaining = end - time.monotonic()
        if remaining <= 0:
            return
        time.sleep(min(SLEEP_TICK_S, remaining))


def _require_pin(name: str, value: int | None) -> int:
    if value is None:
        raise SystemExit(f"Pin '{name}' is not set in component_tests/hardware_config.py")
    return value


def main() -> None:
    drive_en = _require_pin("drive_en", TEST_PINS.drive_en)
    drive_in1 = _require_pin("drive_in1", TEST_PINS.drive_in1)
    drive_in2 = _require_pin("drive_in2", TEST_PINS.drive_in2)
    steer_en = _require_pin("steer_en", TEST_PINS.steer_en)
    steer_in1 = _require_pin("steer_in1", TEST_PINS.steer_in1)
    steer_in2 = _require_pin("steer_in2", TEST_PINS.steer_in2)

    steering_config = SteeringConfig()
    motion_config = MotionConfig()
    drive = MotorDriver(MotorConfig(), drive_en, drive_in1, drive_in2)
    steer = MotorDriver(MotorConfig(pwm_frequency=steering_config.pwm_frequency), steer_en, steer_in1, steer_in2)
    motion = MotionController(motion_config, drive, steer, steering_config)

    signal.signal(signal.SIGINT, _request_stop)
    signal.signal(signal.SIGTERM, _request_stop)

    max_left_angle = -motion_config.max_steering_angle
    total_segments = len(FORWARD_DURATIONS_S)

    try:
        motion.init()

        for i in range(COUNTDOWN_S, 0, -1):
            if not _running:
                return
            print(f"Starting in {i}...")
            time.sleep(1.0)

        for idx, forward_duration in enumerate(FORWARD_DURATIONS_S):
            if not _running:
                break

            print(f"Segment {idx + 1}/{total_segments}: forward {forward_duration:.2f}s")
            motion.set_motion(FORWARD_VELOCITY, 0.0)
            _sleep_interruptible(forward_duration)

            if not _running or idx == total_segments - 1:
                continue

            print(f"  Left turn {LEFT_DURATION_S:.2f}s")
            motion.set_motion(LEFT_VELOCITY, max_left_angle)
            _sleep_interruptible(LEFT_DURATION_S)

            if not _running:
                break

            print(f"  Re-center {CENTER_DURATION_S:.2f}s")
            motion.set_motion(0.0, -max_left_angle)
            _sleep_interruptible(CENTER_DURATION_S)

        print("Sequence complete.")
    finally:
        try:
            motion.stop()
        finally:
            motion.cleanup()


if __name__ == "__main__":
    main()
