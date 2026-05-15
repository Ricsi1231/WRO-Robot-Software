from __future__ import annotations

import signal
import time
from typing import Any

from component_tests.hardware_config import TEST_PINS
from wro.config import MotionConfig, MotorConfig, SteeringConfig
from wro.motion_controller import MotionController
from wro.motor_driver import MotorDriver

RIGHT_DURATION_S: float = 0.3
LEFT_DURATION_S: float = 0.3
STEERING_ACTIVATION_S: float = 3.0
STEERING_OFF_S: float = 1.0
END_RECENTER_S: float = 0.1
CYCLES: int = 5
DRIVE_VELOCITY: float = 0.85
STEERING_MAX_SPEED_PERCENT: float = 100.0
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


def _run_phase(motion: MotionController, steering_angle: float, total_duration_s: float) -> None:
    """Steer to the target angle for STEERING_ACTIVATION_S, then release the
    steering motor and drive forward straight for any remainder of the phase
    plus STEERING_OFF_S of post-turn cooldown."""
    activation = min(STEERING_ACTIVATION_S, total_duration_s)
    motion.set_motion(DRIVE_VELOCITY, steering_angle)
    _sleep_interruptible(activation)

    if not _running:
        return

    off_duration = max(0.0, total_duration_s - activation) + STEERING_OFF_S
    motion.set_motion(DRIVE_VELOCITY, 0.0)
    _sleep_interruptible(off_duration)


def main() -> None:
    drive_en = _require_pin("drive_en", TEST_PINS.drive_en)
    drive_in1 = _require_pin("drive_in1", TEST_PINS.drive_in1)
    drive_in2 = _require_pin("drive_in2", TEST_PINS.drive_in2)
    steer_en = _require_pin("steer_en", TEST_PINS.steer_en)
    steer_in1 = _require_pin("steer_in1", TEST_PINS.steer_in1)
    steer_in2 = _require_pin("steer_in2", TEST_PINS.steer_in2)

    steering_config = SteeringConfig(max_speed_percent=STEERING_MAX_SPEED_PERCENT)
    motion_config = MotionConfig()
    drive = MotorDriver(MotorConfig(), drive_en, drive_in1, drive_in2)
    steer = MotorDriver(MotorConfig(pwm_frequency=steering_config.pwm_frequency), steer_en, steer_in1, steer_in2)
    motion = MotionController(motion_config, drive, steer, steering_config)

    signal.signal(signal.SIGINT, _request_stop)
    signal.signal(signal.SIGTERM, _request_stop)

    max_left_angle = -motion_config.max_steering_angle
    max_right_angle = motion_config.max_steering_angle

    try:
        motion.init()

        for i in range(COUNTDOWN_S, 0, -1):
            if not _running:
                return
            print(f"Starting in {i}...")
            time.sleep(1.0)

        for cycle in range(1, CYCLES + 1):
            if not _running:
                break

            print(f"Cycle {cycle}/{CYCLES}: right phase {RIGHT_DURATION_S:.2f}s")
            _run_phase(motion, max_right_angle, RIGHT_DURATION_S)

            if not _running:
                break

            print(f"Cycle {cycle}/{CYCLES}: left phase {LEFT_DURATION_S:.2f}s")
            _run_phase(motion, max_left_angle, LEFT_DURATION_S)

        if _running and END_RECENTER_S > 0:
            print(f"Re-centering steering {END_RECENTER_S:.2f}s")
            motion.set_motion(0.0, max_right_angle)
            _sleep_interruptible(END_RECENTER_S)

        print("Sequence complete.")
    finally:
        try:
            motion.stop()
        finally:
            motion.cleanup()


if __name__ == "__main__":
    main()
