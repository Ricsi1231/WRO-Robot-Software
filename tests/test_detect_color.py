import numpy as np

from wro.config import VisionConfig
from wro.vision import detect_color

CONFIG = VisionConfig()


def test_detect_red() -> None:
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    frame[:, :, 0] = 112
    frame[:, :, 1] = 200
    frame[:, :, 2] = 200
    result = detect_color(frame, CONFIG)
    assert result.red_pixels > 0
    assert result.green_pixels == 0


def test_old_red_wraparound_range_not_detected() -> None:
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    frame[:, :, 0] = 175
    frame[:, :, 1] = 200
    frame[:, :, 2] = 200
    result = detect_color(frame, CONFIG)
    assert result.red_pixels == 0
    assert result.green_pixels == 0


def test_detect_green() -> None:
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    frame[:, :, 0] = 140
    frame[:, :, 1] = 200
    frame[:, :, 2] = 200
    result = detect_color(frame, CONFIG)
    assert result.red_pixels == 0
    assert result.green_pixels > 0


def test_detect_nothing() -> None:
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    result = detect_color(frame, CONFIG)
    assert result.red_pixels == 0
    assert result.green_pixels == 0


def test_detection_flags() -> None:
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    frame[:, :, 0] = 112
    frame[:, :, 1] = 200
    frame[:, :, 2] = 200
    result = detect_color(frame, CONFIG)
    assert result.red_detected is True
    assert result.green_detected is False


def test_below_threshold_not_detected() -> None:
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    frame[0:2, 0:2, 0] = 112
    frame[0:2, 0:2, 1] = 200
    frame[0:2, 0:2, 2] = 200
    result = detect_color(frame, CONFIG)
    assert result.red_pixels > 0
    assert result.red_pixels < CONFIG.min_pixel_count
    assert result.red_detected is False
