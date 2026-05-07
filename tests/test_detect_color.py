import numpy as np

from wro.config import VisionConfig
from wro.vision import detect_color, frame_to_hsv

CONFIG = VisionConfig()


def test_detect_red() -> None:
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    frame[:, :, 0] = 150
    frame[:, :, 1] = 240
    frame[:, :, 2] = 200
    result = detect_color(frame, CONFIG)
    assert result.red_pixels > 0
    assert result.green_pixels == 0


def test_normal_red_hue_not_detected_for_this_camera_calibration() -> None:
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    frame[:, :, 0] = 10
    frame[:, :, 1] = 200
    frame[:, :, 2] = 200
    result = detect_color(frame, CONFIG)
    assert result.red_pixels == 0
    assert result.green_pixels == 0


def test_detect_green() -> None:
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    frame[:, :, 0] = 60
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
    frame = np.zeros((101, 100, 3), dtype=np.uint8)
    frame[:, :, 0] = 150
    frame[:, :, 1] = 240
    frame[:, :, 2] = 200
    result = detect_color(frame, CONFIG)
    assert result.red_detected is True
    assert result.green_detected is False


def test_below_threshold_not_detected() -> None:
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    frame[0:50, 0:50, 0] = 150
    frame[0:50, 0:50, 1] = 240
    frame[0:50, 0:50, 2] = 200
    result = detect_color(frame, CONFIG)
    assert result.red_pixels > 0
    assert result.red_pixels < CONFIG.min_pixel_count
    assert result.red_detected is False


def test_red_noise_below_threshold_not_detected() -> None:
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    frame[0:95, :, 0] = 150
    frame[0:95, :, 1] = 240
    frame[0:95, :, 2] = 200
    result = detect_color(frame, CONFIG)
    assert result.red_pixels == 9_500
    assert result.red_pixels < CONFIG.min_pixel_count
    assert result.red_detected is False


def test_measured_red_hue_not_detected_as_green() -> None:
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    frame[:, :, 0] = 150
    frame[:, :, 1] = 250
    frame[:, :, 2] = 220
    result = detect_color(frame, CONFIG)
    assert result.red_pixels > 0
    assert result.green_pixels == 0


def test_frame_to_hsv_treats_camera_frame_as_bgr() -> None:
    frame = np.zeros((1, 1, 3), dtype=np.uint8)
    frame[0, 0, 2] = 255
    hsv = frame_to_hsv(frame)
    assert hsv[0, 0, 0] == 0
    assert hsv[0, 0, 1] == 255
    assert hsv[0, 0, 2] == 255
