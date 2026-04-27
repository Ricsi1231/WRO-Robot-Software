import numpy as np

from main import detect_color


def test_detect_red() -> None:
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    frame[:, :, 0] = 10
    frame[:, :, 1] = 200
    frame[:, :, 2] = 200
    red_pixels, green_pixels = detect_color(frame)
    assert red_pixels > 0
    assert green_pixels == 0


def test_detect_red_upper_range() -> None:
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    frame[:, :, 0] = 175
    frame[:, :, 1] = 200
    frame[:, :, 2] = 200
    red_pixels, green_pixels = detect_color(frame)
    assert red_pixels > 0
    assert green_pixels == 0


def test_detect_green() -> None:
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    frame[:, :, 0] = 140
    frame[:, :, 1] = 200
    frame[:, :, 2] = 200
    red_pixels, green_pixels = detect_color(frame)
    assert red_pixels == 0
    assert green_pixels > 0


def test_detect_nothing() -> None:
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    red_pixels, green_pixels = detect_color(frame)
    assert red_pixels == 0
    assert green_pixels == 0
