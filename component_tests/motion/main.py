from __future__ import annotations

# ruff: noqa: E402
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from component_tests.common import cleanup_safely, confirm_hardware_test, require_pins, sleep_with_status
from component_tests.hardware_config import REQUIRE_CONFIRMATION, TEST_MOVE_DURATION_S, TEST_PINS, TEST_STOP_DURATION_S
from wro.config import MotionConfig, MotorConfig, SteeringConfig
from wro.motion_controller import MotionController
from wro.motor_driver import MotorDriver


def main() -> None:
    require_pins(
        "Motion controller",
        {
            "drive_en": TEST_PINS.drive_en,
            "drive_in1": TEST_PINS.drive_in1,
            "drive_in2": TEST_PINS.drive_in2,
            "steer_en": TEST_PINS.steer_en,
            "steer_in1": TEST_PINS.steer_in1,
            "steer_in2": TEST_PINS.steer_in2,
        },
    )
    confirm_hardware_test("Robot drive and steering will move. Lift the robot before continuing.", REQUIRE_CONFIRMATION)

    steering_config = SteeringConfig()
    drive = MotorDriver(MotorConfig(), TEST_PINS.drive_en, TEST_PINS.drive_in1, TEST_PINS.drive_in2)
    steer = MotorDriver(
        MotorConfig(pwm_frequency=steering_config.pwm_frequency),
        TEST_PINS.steer_en,
        TEST_PINS.steer_in1,
        TEST_PINS.steer_in2,
    )
    motion = MotionController(MotionConfig(), drive, steer, steering_config)

    try:
        motion.init()
        motion.set_motion(0.25, 0.0)
        sleep_with_status(TEST_MOVE_DURATION_S, "Driving forward.")
        motion.set_motion(0.0, 15.0)
        sleep_with_status(TEST_MOVE_DURATION_S, "Steering right.")
        motion.set_motion(0.0, -15.0)
        sleep_with_status(TEST_MOVE_DURATION_S, "Steering left.")
        motion.stop()
        time.sleep(TEST_STOP_DURATION_S)
        motion.emergency_stop()
        print("Emergency stop applied.")
    finally:
        cleanup_safely(motion.stop, motion.cleanup)


if __name__ == "__main__":
    main()
