from __future__ import annotations

# ruff: noqa: E402
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from component_tests.common import cleanup_safely, run_timed_loop
from component_tests.hardware_config import TEST_CAMERA_DURATION_S, TEST_PRINT_INTERVAL_S
from wro.config import VisionConfig
from wro.vision import Camera


def main() -> None:
    camera = Camera(VisionConfig())
    try:
        camera.start()
        print("Show red and green targets to the camera.")

        def print_reading() -> None:
            detection = camera.latest_detection
            print(
                f"red_pixels={detection.red_pixels} "
                f"green_pixels={detection.green_pixels} "
                f"red_detected={detection.red_detected} "
                f"green_detected={detection.green_detected}"
            )

        run_timed_loop(TEST_CAMERA_DURATION_S, TEST_PRINT_INTERVAL_S, print_reading)
    finally:
        cleanup_safely(camera.stop)


if __name__ == "__main__":
    main()
