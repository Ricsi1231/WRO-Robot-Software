import numpy as np

from wro.config import VisionConfig
from wro.vision import detect_color

CONFIG = VisionConfig()


def test_detect_red() -> None:
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    frame[:, :, 0] = 10
    frame[:, :, 1] = 200
    frame[:, :, 2] = 200
    result = detect_color(frame, CONFIG)
    assert result.red_pixels > 0
    assert result.green_pixels == 0


def test_detect_red_upper_range() -> None:
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    frame[:, :, 0] = 175
    frame[:, :, 1] = 200
    frame[:, :, 2] = 200
    result = detect_color(frame, CONFIG)
    assert result.red_pixels > 0
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
    frame[:, :, 0] = 10
    frame[:, :, 1] = 200
    frame[:, :, 2] = 200
    result = detect_color(frame, CONFIG)
    assert result.red_detected is True
    assert result.green_detected is False
