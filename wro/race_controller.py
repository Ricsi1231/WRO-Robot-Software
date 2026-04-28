from __future__ import annotations

import enum
import time

from wro.config import RaceConfig
from wro.encoder import Encoder
from wro.motion_controller import MotionController
from wro.pid import PIDController
from wro.reflectance_sensor import ReflectanceClass, ReflectanceSensor
from wro.vision import Camera


class RaceState(enum.Enum):
    IDLE = 0
    RUNNING = 1
    STOPPING = 2
    FINISHED = 3


class RaceController:
    def __init__(
        self,
        config: RaceConfig,
        motion: MotionController,
        encoder: Encoder,
        reflectance: ReflectanceSensor,
        pid: PIDController,
        camera: Camera,
    ) -> None:
        self._config = config
        self._motion = motion
        self._encoder = encoder
        self._reflectance = reflectance
        self._pid = pid
        self._camera = camera

        self._state = RaceState.IDLE
        self._start_signal_received = False
        self._corner_count = 0
        self._lap_count = 0
        self._clockwise = True

        self._last_corner_time: float = 0.0
        self._in_corner_maneuver = False
        self._corner_start_time: float = 0.0

        self._in_avoidance_maneuver = False
        self._avoidance_start_time: float = 0.0
        self._current_avoidance_angle: float = 0.0

    def start(self) -> None:
        self._state = RaceState.IDLE
        self._start_signal_received = False
        self._corner_count = 0
        self._lap_count = 0
        self._in_corner_maneuver = False
        self._in_avoidance_maneuver = False

    def on_start_signal(self) -> None:
        self._start_signal_received = True

    def update(self) -> None:
        if self._state == RaceState.IDLE:
            self._update_idle()
        elif self._state == RaceState.RUNNING:
            self._update_running()
        elif self._state == RaceState.STOPPING:
            self._update_stopping()

    @property
    def state(self) -> RaceState:
        return self._state

    @property
    def lap_count(self) -> int:
        return self._lap_count

    @property
    def corner_count(self) -> int:
        return self._corner_count

    def _update_idle(self) -> None:
        if self._start_signal_received:
            self._start_signal_received = False
            self._encoder.reset_position()
            self._pid.reset()
            self._corner_count = 0
            self._lap_count = 0
            self._last_corner_time = time.monotonic()

            self._motion.set_velocity(self._config.cruise_velocity)
            self._state = RaceState.RUNNING

    def _update_running(self) -> None:
        now = time.monotonic()
        detection = self._camera.latest_detection

        if self._in_avoidance_maneuver:
            if now - self._avoidance_start_time >= self._config.pillar_steer_duration_s:
                self._in_avoidance_maneuver = False
                self._motion.set_steering_angle(0.0)
        elif detection.green_detected:
            self._in_avoidance_maneuver = True
            self._avoidance_start_time = now
            self._current_avoidance_angle = -self._config.pillar_avoid_angle
            self._motion.set_steering_angle(self._current_avoidance_angle)
            self._motion.set_velocity(self._config.corner_velocity)
        elif detection.red_detected:
            self._in_avoidance_maneuver = True
            self._avoidance_start_time = now
            self._current_avoidance_angle = self._config.pillar_avoid_angle
            self._motion.set_steering_angle(self._current_avoidance_angle)
            self._motion.set_velocity(self._config.corner_velocity)

        if self._in_corner_maneuver:
            if now - self._corner_start_time >= self._config.corner_steer_duration_s:
                self._in_corner_maneuver = False
                self._motion.set_steering_angle(0.0)
                self._motion.set_velocity(self._config.cruise_velocity)
        elif not self._in_avoidance_maneuver:
            detected = self._reflectance.detected_class
            if detected == ReflectanceClass.ORANGE and (now - self._last_corner_time) >= self._config.corner_debounce_s:
                self._corner_count += 1
                self._last_corner_time = now

                if self._corner_count % self._config.corners_per_lap == 0:
                    self._lap_count += 1

                if self._lap_count >= self._config.total_laps:
                    self._state = RaceState.STOPPING
                    return

                corner_angle = (
                    self._config.corner_steering_angle if self._clockwise else -self._config.corner_steering_angle
                )
                self._in_corner_maneuver = True
                self._corner_start_time = now
                self._motion.set_steering_angle(corner_angle)
                self._motion.set_velocity(self._config.corner_velocity)

    def _update_stopping(self) -> None:
        self._motion.stop()
        self._state = RaceState.FINISHED
