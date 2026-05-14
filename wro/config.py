from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class PinConfig:
    drive_en: int | None = None
    drive_in1: int | None = None
    drive_in2: int | None = None
    steer_en: int | None = None
    steer_in1: int | None = None
    steer_in2: int | None = None
    encoder_a: int | None = None
    encoder_b: int | None = None
    reflectance_orange: int | None = None
    reflectance_green: int | None = None
    ultrasonic_trigger: int | None = None
    ultrasonic_echo: int | None = None
    ir_line: int | None = None
    button: int = 23


@dataclass
class MotorConfig:
    pwm_frequency: int = 1_000
    ramp_step_percent: int = 5
    ramp_step_delay_s: float = 0.02
    min_effective_percent: int = 0


@dataclass
class SteeringConfig:
    pwm_frequency: int = 1_000
    max_angle: float = 30.0
    max_speed_percent: float = 100.0
    min_speed_percent: float = 30.0

    def __post_init__(self) -> None:
        if self.pwm_frequency <= 0:
            raise ValueError(f"pwm_frequency must be > 0, got {self.pwm_frequency}")
        if self.max_angle <= 0:
            raise ValueError(f"max_angle must be > 0, got {self.max_angle}")
        if not 0 <= self.min_speed_percent <= self.max_speed_percent <= 100:
            raise ValueError(
                "speed percents must satisfy 0 <= min_speed_percent <= max_speed_percent <= 100; "
                f"got min={self.min_speed_percent}, max={self.max_speed_percent}"
            )


@dataclass
class MotionConfig:
    max_steering_angle: float = 30.0
    forward_is_clockwise: bool = True
    center_on_stop: bool = True
    velocity_deadzone: float = 0.01
    velocity_to_speed_scale: float = 100.0
    steering_deadzone: float = 0.5


@dataclass
class EncoderConfig:
    pulses_per_rev: int = 12
    rpm_calc_period_s: float = 0.05
    ema_alpha: float = 0.3


@dataclass
class PidConfig:
    kp: float = 1.0
    ki: float = 0.0
    kd: float = 0.0
    max_output: float = 100.0
    max_integral: float = 1000.0
    error_epsilon: float = 2.0
    speed_epsilon: float = 7.0
    error_timeout_s: float = 0.6
    stuck_timeout_s: float = 0.5
    derivative_alpha: float = 0.2


@dataclass
class ReflectanceConfig:
    debounce_s: float = 0.05


@dataclass
class IrLineConfig:
    debounce_s: float = 0.05
    detection_debounce_s: float = 0.30
    detections_per_turn: int = 2
    turn_steering_angle: float = 25.0
    turn_duration_s: float = 0.6
    turn_velocity: float = 0.3

    def __post_init__(self) -> None:
        if self.detections_per_turn <= 0:
            raise ValueError(f"detections_per_turn must be > 0, got {self.detections_per_turn}")
        if self.turn_velocity <= 0:
            raise ValueError(f"turn_velocity must be > 0, got {self.turn_velocity}")
        if self.turn_steering_angle <= 0:
            raise ValueError(f"turn_steering_angle must be > 0, got {self.turn_steering_angle}")
        for name in ("debounce_s", "detection_debounce_s", "turn_duration_s"):
            value = getattr(self, name)
            if value < 0:
                raise ValueError(f"{name} must be >= 0, got {value}")


@dataclass
class UltrasonicConfig:
    max_distance_cm: float = 200.0
    close_distance_cm: float = 25.0
    close_clear_distance_cm: float = 35.0
    ema_alpha: float = 0.35
    max_consecutive_failures: int = 5

    def __post_init__(self) -> None:
        if self.close_clear_distance_cm < self.close_distance_cm:
            raise ValueError(
                "close_clear_distance_cm must be >= close_distance_cm "
                f"(got clear={self.close_clear_distance_cm}, close={self.close_distance_cm})"
            )


@dataclass
class RaceConfig:
    cruise_velocity: float = 0.5
    corner_velocity: float = 0.3
    pillar_avoid_angle: float = 15.0
    total_laps: int = 3
    corners_per_lap: int = 4
    corner_debounce_s: float = 0.5
    pillar_steer_duration_s: float = 0.8
    corner_steering_angle: float = 25.0
    corner_steer_duration_s: float = 0.6
    clockwise: bool = True

    def __post_init__(self) -> None:
        if self.total_laps <= 0:
            raise ValueError(f"total_laps must be > 0, got {self.total_laps}")
        if self.corners_per_lap <= 0:
            raise ValueError(f"corners_per_lap must be > 0, got {self.corners_per_lap}")
        if self.cruise_velocity <= 0 or self.corner_velocity <= 0:
            raise ValueError(
                f"velocities must be > 0, got cruise={self.cruise_velocity}, corner={self.corner_velocity}"
            )
        for name in ("corner_debounce_s", "pillar_steer_duration_s", "corner_steer_duration_s"):
            value = getattr(self, name)
            if value < 0:
                raise ValueError(f"{name} must be >= 0, got {value}")


@dataclass
class VisionConfig:
    red_lower_1: np.ndarray = field(default_factory=lambda: np.array([140, 180, 100]))
    red_upper_1: np.ndarray = field(default_factory=lambda: np.array([165, 255, 255]))
    red_lower_2: np.ndarray = field(default_factory=lambda: np.array([0, 180, 100]))
    red_upper_2: np.ndarray = field(default_factory=lambda: np.array([10, 255, 255]))
    green_lower: np.ndarray = field(default_factory=lambda: np.array([45, 80, 60]))
    green_upper: np.ndarray = field(default_factory=lambda: np.array([85, 255, 255]))
    min_pixel_count: int = 10_000

    def __post_init__(self) -> None:
        pairs = (
            ("red_1", self.red_lower_1, self.red_upper_1),
            ("red_2", self.red_lower_2, self.red_upper_2),
            ("green", self.green_lower, self.green_upper),
        )
        for name, lower, upper in pairs:
            if lower.shape != (3,) or upper.shape != (3,):
                raise ValueError(f"{name} HSV bounds must be 3-element arrays")
            if np.any(lower > upper):
                raise ValueError(
                    f"{name} HSV lower > upper per-channel: lower={lower.tolist()}, upper={upper.tolist()}"
                )
        if self.min_pixel_count < 0:
            raise ValueError(f"min_pixel_count must be >= 0, got {self.min_pixel_count}")


MAIN_LOOP_INTERVAL_S = 0.02
BOUNCE_TIME_S = 0.1
