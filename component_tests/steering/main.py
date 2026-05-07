from __future__ import annotations

# ruff: noqa: E402
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from component_tests.common import cleanup_safely, confirm_hardware_test, require_pins, sleep_with_status
from component_tests.hardware_config import (
    REQUIRE_CONFIRMATION,
    TEST_MOVE_DURATION_S,
    TEST_PINS,
    TEST_STEERING_SPEED_PERCENT,
    TEST_STOP_DURATION_S,
)
from wro.config import MotorConfig, SteeringConfig
from wro.motor_driver import MotorDriver


def main() -> None:
    require_pins(
        "Steering motor",
        {
            "steer_en": TEST_PINS.steer_en,
            "steer_in1": TEST_PINS.steer_in1,
            "steer_in2": TEST_PINS.steer_in2,
        },
    )
    confirm_hardware_test("Steering motor will move left and right at low speed.", REQUIRE_CONFIRMATION)

    steering_config = SteeringConfig()
    motor = MotorDriver(
        MotorConfig(pwm_frequency=steering_config.pwm_frequency),
        TEST_PINS.steer_en,
        TEST_PINS.steer_in1,
        TEST_PINS.steer_in2,
    )
    try:
        motor.init()
        motor.set_direction(False)
        motor.set_speed(TEST_STEERING_SPEED_PERCENT)
        sleep_with_status(TEST_MOVE_DURATION_S, "Steering left.")
        motor.stop()
        time.sleep(TEST_STOP_DURATION_S)

        motor.set_direction(True)
        motor.set_speed(TEST_STEERING_SPEED_PERCENT)
        sleep_with_status(TEST_MOVE_DURATION_S, "Steering right.")
        motor.stop()
    finally:
        cleanup_safely(motor.cleanup)


if __name__ == "__main__":
    main()
