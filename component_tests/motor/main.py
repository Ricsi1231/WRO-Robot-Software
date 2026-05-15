from __future__ import annotations

# ruff: noqa: E402
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from component_tests.common import cleanup_safely, confirm_hardware_test, require_pins, sleep_with_status
from component_tests.hardware_config import (
    REQUIRE_CONFIRMATION,
    TEST_MOTOR_SPEED_PERCENT,
    TEST_MOVE_DURATION_S,
    TEST_PINS,
)
from wro.config import MotorConfig
from wro.motor_driver import MotorDriver


def main() -> None:
    require_pins(
        "Drive motor",
        {
            "drive_en": TEST_PINS.drive_en,
            "drive_in1": TEST_PINS.drive_in1,
            "drive_in2": TEST_PINS.drive_in2,
        },
    )
    confirm_hardware_test("Drive motor will move reverse at full speed.", REQUIRE_CONFIRMATION)

    motor = MotorDriver(MotorConfig(), TEST_PINS.drive_en, TEST_PINS.drive_in1, TEST_PINS.drive_in2)
    try:
        motor.init()
        motor.set_direction(False)
        motor.set_speed(TEST_MOTOR_SPEED_PERCENT)
        sleep_with_status(TEST_MOVE_DURATION_S, "Drive motor reverse.")
        motor.stop()
    finally:
        cleanup_safely(motor.cleanup)


if __name__ == "__main__":
    main()
