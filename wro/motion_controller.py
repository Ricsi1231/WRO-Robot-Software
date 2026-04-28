from __future__ import annotations

from wro.config import MotionConfig, SteeringConfig
from wro.motor_driver import MotorDriver

MIN_VELOCITY = -1.0
MAX_VELOCITY = 1.0


class MotionController:
    def __init__(
        self, config: MotionConfig, drive_motor: MotorDriver, steer_motor: MotorDriver, steering_config: SteeringConfig
    ) -> None:
        self._config = config
        self._drive = drive_motor
        self._steer = steer_motor
        self._steering_config = steering_config
        self._velocity: float = 0.0
        self._steering_angle: float = 0.0

    def init(self) -> None:
        self._drive.init()
        self._steer.init()
        self.set_steering_angle(0.0)

    def set_velocity(self, velocity: float) -> None:
        clamped = max(MIN_VELOCITY, min(MAX_VELOCITY, velocity))

        if abs(clamped) < self._config.velocity_deadzone:
            self._velocity = 0.0
            self._drive.stop()
            return

        desired_cw = self._velocity_to_clockwise(clamped)

        if self._would_reverse(clamped):
            self._drive.set_direction_safe(desired_cw)
        else:
            self._drive.set_direction(desired_cw)

        speed_percent = int(abs(clamped) * self._config.velocity_to_speed_scale)
        self._drive.set_speed(speed_percent)
        self._velocity = clamped

    def set_steering_angle(self, angle_deg: float) -> None:
        clamped = max(-self._config.max_steering_angle, min(self._config.max_steering_angle, angle_deg))
        self._steering_angle = clamped

        if abs(clamped) < self._config.steering_deadzone:
            self._steer.stop()
            return

        self._steer.set_direction(clamped > 0)

        t = abs(clamped) / self._steering_config.max_angle
        speed = self._steering_config.min_speed_percent + t * (
            self._steering_config.max_speed_percent - self._steering_config.min_speed_percent
        )
        self._steer.set_speed(int(speed))

    def set_motion(self, velocity: float, angle_deg: float) -> None:
        self.set_velocity(velocity)
        self.set_steering_angle(angle_deg)

    def stop(self) -> None:
        self._drive.stop()
        self._velocity = 0.0
        if self._config.center_on_stop:
            self._steer.stop()
            self._steering_angle = 0.0

    def emergency_stop(self) -> None:
        self._drive.brake()
        self._steer.brake()
        self._velocity = 0.0

    @property
    def velocity(self) -> float:
        return self._velocity

    @property
    def steering_angle(self) -> float:
        return self._steering_angle

    @property
    def is_moving(self) -> bool:
        return self._drive.is_running

    def cleanup(self) -> None:
        self._drive.cleanup()
        self._steer.cleanup()

    def _velocity_to_clockwise(self, velocity: float) -> bool:
        if velocity >= 0:
            return self._config.forward_is_clockwise
        return not self._config.forward_is_clockwise

    def _would_reverse(self, new_velocity: float) -> bool:
        dz = self._config.velocity_deadzone
        return (self._velocity > dz and new_velocity < -dz) or (self._velocity < -dz and new_velocity > dz)
