from __future__ import annotations

from wro.config import PinConfig

TEST_PINS = PinConfig(
    drive_en=13,
    drive_in1=5,
    drive_in2=6,
    steer_en=12,
    steer_in1=16,
    steer_in2=26,
    encoder_a=None,
    encoder_b=None,
    reflectance_orange=None,
    reflectance_green=None,
    ultrasonic_trigger=24,
    ultrasonic_echo=23,
    ir_line=17,
    button=23,
)

REQUIRE_CONFIRMATION = True

TEST_MOTOR_SPEED_PERCENT = 100
TEST_STEERING_SPEED_PERCENT = 35
TEST_MOVE_DURATION_S = 1.0
TEST_STOP_DURATION_S = 0.5
TEST_PRINT_INTERVAL_S = 0.25
TEST_CAMERA_DURATION_S = 60.0
