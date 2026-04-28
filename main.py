from __future__ import annotations

import signal

from wro.config import BOUNCE_TIME_S, PinConfig
from wro.robot import Robot


def main() -> None:
    pins = PinConfig()
    robot = Robot(pins=pins)
    robot.init()

    if pins.button is not None:
        from gpiozero import Button

        button = Button(pins.button, bounce_time=BOUNCE_TIME_S)
        button.when_pressed = robot.on_start_signal

    signal.signal(signal.SIGTERM, robot.shutdown)
    signal.signal(signal.SIGINT, robot.shutdown)

    robot.run()


if __name__ == "__main__":
    main()
