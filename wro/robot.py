from __future__ import annotations

import time
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
    ServoConfig,
    VisionConfig,
)
from wro.encoder import Encoder
from wro.motion_controller import MotionController
from wro.motor_driver import MotorDriver
from wro.pid import PIDController
from wro.race_controller import RaceController
from wro.reflectance_sensor import ReflectanceSensor
from wro.servo import ServoDriver
from wro.vision import Camera


class Robot:
    def __init__(
        self,
        pins: PinConfig | None = None,
        motor_config: MotorConfig | None = None,
        servo_config: ServoConfig | None = None,
        motion_config: MotionConfig | None = None,
        encoder_config: EncoderConfig | None = None,
        pid_config: PidConfig | None = None,
        reflectance_config: ReflectanceConfig | None = None,
        race_config: RaceConfig | None = None,
        vision_config: VisionConfig | None = None,
    ) -> None:
        self._pins = pins or PinConfig()
        self._running = False

        self._motor = MotorDriver(motor_config or MotorConfig(), self._pins)
        self._servo = ServoDriver(servo_config or ServoConfig(), self._pins)
        self._motion = MotionController(motion_config or MotionConfig(), self._motor, self._servo)
        self._encoder = Encoder(encoder_config or EncoderConfig(), self._pins)
        self._pid = PIDController(pid_config or PidConfig())
        self._reflectance = ReflectanceSensor(reflectance_config or ReflectanceConfig(), self._pins)
        self._camera = Camera(vision_config or VisionConfig())
        self._race = RaceController(
            race_config or RaceConfig(),
            self._motion,
            self._encoder,
            self._reflectance,
            self._pid,
            self._camera,
        )

    def init(self) -> None:
        self._motion.init()
        self._encoder.start()
        self._reflectance.start()
        self._camera.start()
        self._race.start()

    def run(self) -> None:
        self._running = True
        while self._running:
            next_tick = time.monotonic() + MAIN_LOOP_INTERVAL_S
            self._race.update()
            sleep_time = next_tick - time.monotonic()
            if sleep_time > 0:
                time.sleep(sleep_time)

    def on_start_signal(self) -> None:
        self._race.on_start_signal()

    def shutdown(self, _signum: int = 0, _frame: Any = None) -> None:
        self._running = False
        self._camera.stop()
        self._reflectance.stop()
        self._encoder.stop()
        self._motion.stop()
        self._motion.cleanup()
        raise SystemExit(0)
