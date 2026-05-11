from __future__ import annotations

import threading
from typing import Any
from unittest.mock import MagicMock

import numpy as np

from wro.config import VisionConfig
from wro.vision import Camera, detect_color, frame_to_hsv


def _solid_rgb_frame(red: int, green: int, blue: int, size: int = 100) -> np.ndarray:
    frame = np.zeros((size, size, 3), dtype=np.uint8)
    frame[:, :, 0] = red
    frame[:, :, 1] = green
    frame[:, :, 2] = blue
    return frame


def test_frame_to_hsv_pure_red_in_rgb_input() -> None:
    frame = _solid_rgb_frame(255, 0, 0, size=1)
    hsv = frame_to_hsv(frame)
    assert hsv[0, 0, 0] == 0
    assert hsv[0, 0, 1] == 255
    assert hsv[0, 0, 2] == 255


def test_frame_to_hsv_preserves_shape() -> None:
    frame = _solid_rgb_frame(100, 100, 100, size=50)
    hsv = frame_to_hsv(frame)
    assert hsv.shape == (50, 50, 3)


def test_detect_color_pure_red_via_pipeline() -> None:
    rgb = _solid_rgb_frame(255, 0, 0, size=120)
    hsv = frame_to_hsv(rgb)
    result = detect_color(hsv, VisionConfig())
    assert result.red_pixels > 0
    assert result.red_detected is True
    assert result.green_pixels == 0


def test_detect_color_pure_green_via_pipeline() -> None:
    rgb = _solid_rgb_frame(0, 220, 0, size=120)
    hsv = frame_to_hsv(rgb)
    result = detect_color(hsv, VisionConfig())
    assert result.green_pixels > 0
    assert result.green_detected is True
    assert result.red_pixels == 0


def test_detect_color_below_threshold_not_flagged() -> None:
    hsv = np.zeros((10, 10, 3), dtype=np.uint8)
    hsv[:, :, 0] = 150
    hsv[:, :, 1] = 240
    hsv[:, :, 2] = 200
    result = detect_color(hsv, VisionConfig())
    assert result.red_pixels == 100
    assert result.red_detected is False


def test_camera_initial_detection_is_empty() -> None:
    cam = Camera(VisionConfig())
    assert cam.latest_detection.red_detected is False
    assert cam.latest_detection.green_detected is False
    assert cam.latest_detection.red_pixels == 0


def test_camera_on_frame_updates_latest_detection_under_lock() -> None:
    cam = Camera(VisionConfig())
    red_rgb = _solid_rgb_frame(255, 0, 0, size=120)

    request: Any = MagicMock()
    request.make_array.return_value = red_rgb
    cam._on_frame(request)

    latest = cam.latest_detection
    assert latest.red_pixels > 0
    assert latest.red_detected is True


def test_camera_latest_detection_serialized_across_threads() -> None:
    cam = Camera(VisionConfig())
    red_rgb = _solid_rgb_frame(255, 0, 0, size=120)

    request: Any = MagicMock()
    request.make_array.return_value = red_rgb

    barrier = threading.Barrier(2)

    def writer() -> None:
        barrier.wait()
        for _ in range(50):
            cam._on_frame(request)

    def reader() -> None:
        barrier.wait()
        for _ in range(50):
            _ = cam.latest_detection

    t1 = threading.Thread(target=writer)
    t2 = threading.Thread(target=reader)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    assert cam.latest_detection.red_detected is True


def test_camera_stop_handles_uninitialized_picam() -> None:
    cam = Camera(VisionConfig())
    cam.stop()
    assert cam._picam2 is None
