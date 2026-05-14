from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from component_tests.common import cleanup_safely, require_pins, run_timed_loop  # noqa: E402
from component_tests.hardware_config import TEST_MOVE_DURATION_S, TEST_PINS, TEST_PRINT_INTERVAL_S  # noqa: E402
from wro.config import IrLineConfig  # noqa: E402
from wro.ir_line_sensor import IrLineSensor  # noqa: E402


def main() -> None:
    require_pins(
        "IR line sensor",
        {
            "ir_line": TEST_PINS.ir_line,
        },
    )

    sensor = IrLineSensor(IrLineConfig(), TEST_PINS)
    try:
        sensor.start()

        def print_reading() -> None:
            print(f"is_detected={sensor.is_detected} detection_count={sensor.detection_count}")

        run_timed_loop(TEST_MOVE_DURATION_S * 10, TEST_PRINT_INTERVAL_S, print_reading)
    finally:
        cleanup_safely(sensor.stop)


if __name__ == "__main__":
    main()
