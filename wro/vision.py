from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Any, cast

import cv2
import numpy as np

from wro.config import VisionConfig


@dataclass(frozen=True)
class DetectionResult:
    red_pixels: int
    green_pixels: int
    red_detected: bool
    green_detected: bool


def detect_color(hsv_frame: np.ndarray, config: VisionConfig) -> DetectionResult:
    red_mask_1 = cv2.inRange(hsv_frame, config.red_lower_1, config.red_upper_1)
    red_mask_2 = cv2.inRange(hsv_frame, config.red_lower_2, config.red_upper_2)
    red_mask = cv2.bitwise_or(red_mask_1, red_mask_2)

    green_mask = cv2.inRange(hsv_frame, config.green_lower, config.green_upper)

    red_pixels: int = cv2.countNonZero(red_mask)
    green_pixels: int = cv2.countNonZero(green_mask)

    return DetectionResult(
        red_pixels=red_pixels,
        green_pixels=green_pixels,
        red_detected=red_pixels > config.min_pixel_count,
        green_detected=green_pixels > config.min_pixel_count,
    )


def frame_to_hsv(frame: np.ndarray) -> np.ndarray:
    # Camera is configured as RGB888 and calibrate.py uses COLOR_RGB2HSV;
    # keep this in sync so HSV thresholds match between calibration and runtime.
    return cast(np.ndarray, cv2.cvtColor(frame, cv2.COLOR_RGB2HSV))


class Camera:
    def __init__(self, config: VisionConfig) -> None:
        self._config = config
        self._latest: DetectionResult = DetectionResult(0, 0, False, False)
        self._lock = threading.Lock()
        self._picam2: Any = None

    def start(self) -> None:
        from picamera2 import Picamera2

        self._picam2 = Picamera2()
        cam_config = self._picam2.create_video_configuration(main={"format": "RGB888"})
        self._picam2.configure(cam_config)
        self._picam2.pre_callback = self._on_frame
        self._picam2.start()

    def stop(self) -> None:
        if self._picam2 is not None:
            self._picam2.stop()
            self._picam2.close()
            self._picam2 = None

    @property
    def latest_detection(self) -> DetectionResult:
        with self._lock:
            return self._latest

    def _on_frame(self, request: Any) -> None:
        frame = request.make_array("main")
        hsv = frame_to_hsv(frame)
        result = detect_color(hsv, self._config)
        with self._lock:
            self._latest = result
