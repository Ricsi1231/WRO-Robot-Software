from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from component_tests.common import cleanup_safely, require_pins, run_timed_loop  # noqa: E402
from component_tests.hardware_config import TEST_MOVE_DURATION_S, TEST_PINS, TEST_PRINT_INTERVAL_S  # noqa: E402
from wro.config import UltrasonicConfig  # noqa: E402
from wro.ultrasonic_sensor import UltrasonicSensor  # noqa: E402


def main() -> None:
    require_pins(
        "Ultrasonic sensor",
        {
            "ultrasonic_trigger": TEST_PINS.ultrasonic_trigger,
            "ultrasonic_echo": TEST_PINS.ultrasonic_echo,
        },
    )

    sensor = UltrasonicSensor(UltrasonicConfig(), TEST_PINS)
    try:
        sensor.start()

        def print_reading() -> None:
            distance = sensor.distance_cm
            distance_text = "none" if distance is None else f"{distance:.1f}"
            print(f"distance_cm={distance_text} is_close={sensor.is_close}")

        run_timed_loop(TEST_MOVE_DURATION_S * 10, TEST_PRINT_INTERVAL_S, print_reading)
    finally:
        cleanup_safely(sensor.stop)


if __name__ == "__main__":
    main()
