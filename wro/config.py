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
    derivative_alpha: float = 1.0


@dataclass
class ReflectanceConfig:
    debounce_s: float = 0.05


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


@dataclass
class VisionConfig:
    red_lower_1: np.ndarray = field(default_factory=lambda: np.array([0, 100, 80]))
    red_upper_1: np.ndarray = field(default_factory=lambda: np.array([15, 255, 255]))
    red_lower_2: np.ndarray = field(default_factory=lambda: np.array([170, 100, 80]))
    red_upper_2: np.ndarray = field(default_factory=lambda: np.array([180, 255, 255]))
    green_lower: np.ndarray = field(default_factory=lambda: np.array([45, 80, 60]))
    green_upper: np.ndarray = field(default_factory=lambda: np.array([85, 255, 255]))
    min_pixel_count: int = 500


MAIN_LOOP_INTERVAL_S = 0.02
BOUNCE_TIME_S = 0.1
