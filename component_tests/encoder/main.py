from __future__ import annotations

# ruff: noqa: E402
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from component_tests.common import cleanup_safely, require_pins, run_timed_loop
from component_tests.hardware_config import TEST_MOVE_DURATION_S, TEST_PINS, TEST_PRINT_INTERVAL_S
from wro.config import EncoderConfig
from wro.encoder import Encoder


def main() -> None:
    require_pins("Encoder", {"encoder_a": TEST_PINS.encoder_a, "encoder_b": TEST_PINS.encoder_b})

    encoder = Encoder(EncoderConfig(), TEST_PINS)
    try:
        encoder.start()
        print("Rotate the encoder/wheel during this test.")

        def print_reading() -> None:
            print(f"ticks={encoder.position_ticks} rpm={encoder.rpm:.2f} rpm_raw={encoder.rpm_raw:.2f}")

        run_timed_loop(TEST_MOVE_DURATION_S * 5, TEST_PRINT_INTERVAL_S, print_reading)
    finally:
        cleanup_safely(encoder.stop)


if __name__ == "__main__":
    main()
