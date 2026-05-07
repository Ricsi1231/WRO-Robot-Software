from __future__ import annotations

import contextlib
import time
from collections.abc import Callable


def confirm_hardware_test(description: str, enabled: bool) -> None:
    if not enabled:
        return

    print(description)
    answer = input("Type 'yes' to continue: ").strip().lower()
    if answer != "yes":
        raise SystemExit("Cancelled.")


def require_pins(component: str, pins: dict[str, int | None]) -> None:
    missing = [name for name, value in pins.items() if value is None]
    if missing:
        joined = ", ".join(missing)
        raise SystemExit(f"{component} test is missing pin values in component_tests/hardware_config.py: {joined}")


def sleep_with_status(duration_s: float, message: str) -> None:
    print(message)
    time.sleep(duration_s)


def run_timed_loop(duration_s: float, interval_s: float, callback: Callable[[], None]) -> None:
    end_time = time.monotonic() + duration_s
    while time.monotonic() < end_time:
        callback()
        time.sleep(interval_s)


def cleanup_safely(*callbacks: Callable[[], None]) -> None:
    for callback in callbacks:
        with contextlib.suppress(Exception):
            callback()
