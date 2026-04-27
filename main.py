from __future__ import annotations

import signal
import threading
import time
from typing import Any

import cv2
import numpy as np

RED_GPIO_PIN = 17
GREEN_GPIO_PIN = 27

PULSE_DURATION = 0.3
MIN_PIXEL_COUNT = 500

RED_LOWER_1 = np.array([0, 100, 100])
RED_UPPER_1 = np.array([30, 255, 255])
RED_LOWER_2 = np.array([170, 100, 100])
RED_UPPER_2 = np.array([180, 255, 255])

GREEN_LOWER = np.array([130, 100, 80])
GREEN_UPPER = np.array([165, 255, 255])

last_red_pulse: float = 0
last_green_pulse: float = 0


def pulse(device: Any) -> None:
    device.on()
    time.sleep(PULSE_DURATION)
    device.off()


def detect_color(hsv_frame: np.ndarray) -> tuple[int, int]:
    red_mask_1 = cv2.inRange(hsv_frame, RED_LOWER_1, RED_UPPER_1)
    red_mask_2 = cv2.inRange(hsv_frame, RED_LOWER_2, RED_UPPER_2)
    red_mask = cv2.bitwise_or(red_mask_1, red_mask_2)

    green_mask = cv2.inRange(hsv_frame, GREEN_LOWER, GREEN_UPPER)

    red_pixels: int = cv2.countNonZero(red_mask)
    green_pixels: int = cv2.countNonZero(green_mask)

    return red_pixels, green_pixels


def process_frame(request: Any) -> None:
    global last_red_pulse, last_green_pulse

    frame = request.make_array("main")
    hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

    red_pixels, green_pixels = detect_color(hsv)
    red_detected = red_pixels > MIN_PIXEL_COUNT
    green_detected = green_pixels > MIN_PIXEL_COUNT
    now = time.monotonic()

    print(f"Red: {red_pixels:6d} px  Green: {green_pixels:6d} px", end="")

    if red_detected and (now - last_red_pulse) > PULSE_DURATION:
        threading.Thread(target=pulse, args=(red_output,), daemon=True).start()
        last_red_pulse = now
        print("  -> RED PULSE", end="")

    if green_detected and (now - last_green_pulse) > PULSE_DURATION:
        threading.Thread(target=pulse, args=(green_output,), daemon=True).start()
        last_green_pulse = now
        print("  -> GREEN PULSE", end="")

    print()


if __name__ == "__main__":
    from gpiozero import OutputDevice
    from picamera2 import Picamera2

    red_output = OutputDevice(RED_GPIO_PIN)
    green_output = OutputDevice(GREEN_GPIO_PIN)

    picam2 = Picamera2()
    config = picam2.create_video_configuration(main={"format": "RGB888"})
    picam2.configure(config)
    picam2.pre_callback = process_frame
    picam2.start()

    signal.pause()
