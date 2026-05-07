from __future__ import annotations

# ruff: noqa: E402
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from component_tests.common import cleanup_safely, require_pins, run_timed_loop
from component_tests.hardware_config import TEST_MOVE_DURATION_S, TEST_PINS, TEST_PRINT_INTERVAL_S
from wro.config import ReflectanceConfig
from wro.reflectance_sensor import ReflectanceSensor


def main() -> None:
    require_pins(
        "Reflectance sensor",
        {
            "reflectance_orange": TEST_PINS.reflectance_orange,
            "reflectance_green": TEST_PINS.reflectance_green,
        },
    )

    sensor = ReflectanceSensor(ReflectanceConfig(), TEST_PINS)
    try:
        sensor.start()
        print("Move orange and green targets under the reflectance sensors.")

        def print_reading() -> None:
            print(f"detected={sensor.detected_class.name}")

        run_timed_loop(TEST_MOVE_DURATION_S * 10, TEST_PRINT_INTERVAL_S, print_reading)
    finally:
        cleanup_safely(sensor.stop)


if __name__ == "__main__":
    main()
