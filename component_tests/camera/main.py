from __future__ import annotations

# ruff: noqa: E402
import argparse
import sys
import time
from pathlib import Path
from typing import Any, TextIO

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import cv2
import numpy as np

from component_tests.common import cleanup_safely
from component_tests.hardware_config import TEST_CAMERA_DURATION_S, TEST_PRINT_INTERVAL_S
from wro.config import VisionConfig
from wro.vision import DetectionResult, detect_color

DIAGNOSTIC_MODES = ("background", "red", "green")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run camera color detection diagnostics.")
    parser.add_argument(
        "mode",
        choices=DIAGNOSTIC_MODES,
        nargs="?",
        default="background",
        help="Scene being captured for the diagnostic log.",
    )
    return parser.parse_args()


def _hsv_stats_lines(hsv_frame: np.ndarray) -> list[str]:
    h, w = hsv_frame.shape[:2]
    center = hsv_frame[h // 4 : 3 * h // 4, w // 4 : 3 * w // 4]

    return [
        _channel_stats_text("H", center[:, :, 0]),
        _channel_stats_text("S", center[:, :, 1]),
        _channel_stats_text("V", center[:, :, 2]),
    ]


def _channel_stats_text(channel_name: str, channel: np.ndarray) -> str:
    return f"{channel_name}: min={channel.min()} max={channel.max()} mean={channel.mean():.0f}"


def _reading_lines(mode: str, detection: DetectionResult, total_pixels: int, hsv_frame: np.ndarray) -> list[str]:
    red_percent = detection.red_pixels / total_pixels * 100.0
    green_percent = detection.green_pixels / total_pixels * 100.0

    lines = [
        f"mode={mode}",
        (
            f"total_pixels={total_pixels} "
            f"red_pixels={detection.red_pixels} "
            f"green_pixels={detection.green_pixels} "
            f"red_percent={red_percent:.2f} "
            f"green_percent={green_percent:.2f} "
            f"red_detected={detection.red_detected} "
            f"green_detected={detection.green_detected}"
        ),
        "center_hsv_stats:",
    ]
    lines.extend(f"  {line}" for line in _hsv_stats_lines(hsv_frame))
    return lines


def _print_and_write(lines: list[str], output_file: TextIO) -> None:
    for line in lines:
        print(line)
        output_file.write(line)
        output_file.write("\n")
    print("")
    output_file.write("\n")
    output_file.flush()


def _configure_camera() -> Any:
    from picamera2 import Picamera2

    picam2 = Picamera2()
    config = picam2.create_video_configuration(main={"format": "RGB888"})
    picam2.configure(config)
    picam2.start()
    return picam2


def main() -> None:
    args = _parse_args()
    mode = args.mode
    output_path = Path(f"camera_diagnostic_{mode}.txt")
    vision_config = VisionConfig()
    picam2: Any = None

    print(f"Camera diagnostic mode: {mode}")
    print(f"Writing diagnostic output to {output_path}")
    print("Use modes: background, red, green.")

    try:
        picam2 = _configure_camera()
        end_time = time.monotonic() + TEST_CAMERA_DURATION_S
        with output_path.open("w", encoding="utf-8") as output_file:
            while time.monotonic() < end_time:
                frame = picam2.capture_array()
                hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
                detection = detect_color(hsv, vision_config)
                total_pixels = frame.shape[0] * frame.shape[1]
                _print_and_write(_reading_lines(mode, detection, total_pixels, hsv), output_file)
                time.sleep(TEST_PRINT_INTERVAL_S)
    finally:
        if picam2 is not None:
            cleanup_safely(picam2.stop, picam2.close)


if __name__ == "__main__":
    main()
