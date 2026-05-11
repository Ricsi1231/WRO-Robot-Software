from __future__ import annotations

import numpy as np
import pytest

from wro.config import RaceConfig, SteeringConfig, UltrasonicConfig, VisionConfig
from wro.servo import ServoConfig


def test_race_config_rejects_zero_corners_per_lap() -> None:
    with pytest.raises(ValueError, match="corners_per_lap"):
        RaceConfig(corners_per_lap=0)


def test_race_config_rejects_zero_total_laps() -> None:
    with pytest.raises(ValueError, match="total_laps"):
        RaceConfig(total_laps=0)


def test_race_config_rejects_negative_velocity() -> None:
    with pytest.raises(ValueError, match="velocities"):
        RaceConfig(cruise_velocity=-0.1)


def test_race_config_accepts_zero_durations() -> None:
    RaceConfig(corner_debounce_s=0.0, corner_steer_duration_s=0.0, pillar_steer_duration_s=0.0)


def test_steering_config_rejects_inverted_speed_range() -> None:
    with pytest.raises(ValueError, match="speed percents"):
        SteeringConfig(min_speed_percent=80.0, max_speed_percent=40.0)


def test_steering_config_rejects_zero_max_angle() -> None:
    with pytest.raises(ValueError, match="max_angle"):
        SteeringConfig(max_angle=0.0)


def test_vision_config_rejects_inverted_red_range() -> None:
    with pytest.raises(ValueError, match="red_2"):
        VisionConfig(
            red_lower_2=np.array([20, 100, 100]),
            red_upper_2=np.array([5, 255, 255]),
        )


def test_vision_config_rejects_inverted_green_range() -> None:
    with pytest.raises(ValueError, match="green"):
        VisionConfig(
            green_lower=np.array([90, 100, 100]),
            green_upper=np.array([60, 255, 255]),
        )


def test_ultrasonic_config_rejects_close_clear_below_close() -> None:
    with pytest.raises(ValueError, match="close_clear_distance_cm"):
        UltrasonicConfig(close_distance_cm=30.0, close_clear_distance_cm=20.0)


def test_servo_config_rejects_inverted_pulse() -> None:
    with pytest.raises(ValueError, match="min_pulse_ms"):
        ServoConfig(min_pulse_ms=2.0, max_pulse_ms=1.0)


def test_servo_config_rejects_center_outside_range() -> None:
    with pytest.raises(ValueError, match="center_angle"):
        ServoConfig(min_angle=0.0, max_angle=180.0, center_angle=200.0)
