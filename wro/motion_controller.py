from __future__ import annotations

from wro.config import MotionConfig
from wro.motor_driver import MotorDriver
from wro.servo import ServoDriver

MIN_VELOCITY = -1.0
MAX_VELOCITY = 1.0


class MotionController:
    def __init__(self, config: MotionConfig, motor: MotorDriver, servo: ServoDriver) -> None:
        self._config = config
        self._motor = motor
        self._servo = servo
        self._velocity: float = 0.0
        self._steering_angle: float = 0.0

    def init(self) -> None:
        self._motor.init()
        self._servo.init()
        self.set_steering_angle(0.0)

    def set_velocity(self, velocity: float) -> None:
        clamped = max(MIN_VELOCITY, min(MAX_VELOCITY, velocity))

        if abs(clamped) < self._config.velocity_deadzone:
            self._velocity = 0.0
            self._motor.stop()
            return

        desired_cw = self._velocity_to_clockwise(clamped)

        if self._would_reverse(clamped):
            self._motor.set_direction_safe(desired_cw)
        else:
            self._motor.set_direction(desired_cw)

        speed_percent = int(abs(clamped) * self._config.velocity_to_speed_scale)
        self._motor.set_speed(speed_percent)
        self._velocity = clamped

    def set_steering_angle(self, angle_deg: float) -> None:
        clamped = max(-self._config.max_steering_angle, min(self._config.max_steering_angle, angle_deg))
        servo_angle = self._config.servo_center_angle + clamped
        self._servo.set_angle(servo_angle)
        self._steering_angle = clamped

    def set_motion(self, velocity: float, angle_deg: float) -> None:
        self.set_velocity(velocity)
        self.set_steering_angle(angle_deg)

    def stop(self) -> None:
        self._motor.stop()
        self._velocity = 0.0
        if self._config.center_on_stop:
            self.set_steering_angle(0.0)

    def emergency_stop(self) -> None:
        self._motor.brake()
        self._velocity = 0.0

    @property
    def velocity(self) -> float:
        return self._velocity

    @property
    def steering_angle(self) -> float:
        return self._steering_angle

    @property
    def is_moving(self) -> bool:
        return self._motor.is_running

    def cleanup(self) -> None:
        self._motor.cleanup()
        self._servo.cleanup()

    def _velocity_to_clockwise(self, velocity: float) -> bool:
        if velocity >= 0:
            return self._config.forward_is_clockwise
        return not self._config.forward_is_clockwise

    def _would_reverse(self, new_velocity: float) -> bool:
        dz = self._config.velocity_deadzone
        return (self._velocity > dz and new_velocity < -dz) or (self._velocity < -dz and new_velocity > dz)
