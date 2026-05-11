from __future__ import annotations

import contextlib
import time
import traceback
from typing import Any

from wro.config import (
    MAIN_LOOP_INTERVAL_S,
    EncoderConfig,
    MotionConfig,
    MotorConfig,
    PidConfig,
    PinConfig,
    RaceConfig,
    ReflectanceConfig,
    SteeringConfig,
    UltrasonicConfig,
    VisionConfig,
)
from wro.encoder import Encoder
from wro.motion_controller import MotionController
from wro.motor_driver import MotorDriver
from wro.pid import PIDController
from wro.race_controller import RaceController
from wro.reflectance_sensor import ReflectanceSensor
from wro.ultrasonic_sensor import UltrasonicSensor
from wro.vision import Camera


class Robot:
    def __init__(
        self,
        pins: PinConfig | None = None,
        motor_config: MotorConfig | None = None,
        steering_config: SteeringConfig | None = None,
        motion_config: MotionConfig | None = None,
        encoder_config: EncoderConfig | None = None,
        pid_config: PidConfig | None = None,
        reflectance_config: ReflectanceConfig | None = None,
        ultrasonic_config: UltrasonicConfig | None = None,
        race_config: RaceConfig | None = None,
        vision_config: VisionConfig | None = None,
    ) -> None:
        self._pins = pins or PinConfig()
        self._running = False
        self._cleaned_up = False

        _mc = motor_config or MotorConfig()
        _sc = steering_config or SteeringConfig()

        self._drive_motor = MotorDriver(_mc, self._pins.drive_en, self._pins.drive_in1, self._pins.drive_in2)
        steer_motor_config = MotorConfig(pwm_frequency=_sc.pwm_frequency)
        self._steer_motor = MotorDriver(
            steer_motor_config, self._pins.steer_en, self._pins.steer_in1, self._pins.steer_in2
        )

        self._motion = MotionController(motion_config or MotionConfig(), self._drive_motor, self._steer_motor, _sc)
        self._encoder = Encoder(encoder_config or EncoderConfig(), self._pins)
        self._pid = PIDController(pid_config or PidConfig())
        self._reflectance = ReflectanceSensor(reflectance_config or ReflectanceConfig(), self._pins)
        self._ultrasonic = UltrasonicSensor(ultrasonic_config or UltrasonicConfig(), self._pins)
        self._camera = Camera(vision_config or VisionConfig())
        self._race = RaceController(
            race_config or RaceConfig(),
            self._motion,
            self._encoder,
            self._reflectance,
            self._pid,
            self._camera,
            self._ultrasonic,
        )

    def init(self) -> None:
        try:
            self._motion.init()
            self._encoder.start()
            self._reflectance.start()
            self._ultrasonic.start()
            self._camera.start()
            self._race.start()
        except Exception:
            traceback.print_exc()
            self._cleanup()
            raise

    def run(self) -> None:
        self._running = True
        try:
            while self._running:
                next_tick = time.monotonic() + MAIN_LOOP_INTERVAL_S
                self._race.update()
                self._motion.tick()
                sleep_time = next_tick - time.monotonic()
                if sleep_time > 0:
                    time.sleep(sleep_time)
        finally:
            self._cleanup()

    def on_start_signal(self) -> None:
        self._race.on_start_signal()

    def shutdown(self, _signum: int = 0, _frame: Any = None) -> None:
        self._running = False

    def _cleanup(self) -> None:
        if self._cleaned_up:
            return
        self._cleaned_up = True
        with contextlib.suppress(Exception):
            self._camera.stop()
        with contextlib.suppress(Exception):
            self._reflectance.stop()
        with contextlib.suppress(Exception):
            self._ultrasonic.stop()
        with contextlib.suppress(Exception):
            self._encoder.stop()
        with contextlib.suppress(Exception):
            self._motion.stop()
            self._motion.cleanup()
