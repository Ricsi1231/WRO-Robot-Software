from __future__ import annotations

from wro.config import PinConfig, UltrasonicConfig
from wro.ultrasonic_sensor import UltrasonicSensor


class FakeDistanceSensor:
    def __init__(self, distance: float) -> None:
        self.distance = distance
        self.closed = False

    def close(self) -> None:
        self.closed = True


def test_distance_is_none_when_not_started() -> None:
    sensor = UltrasonicSensor(UltrasonicConfig(), PinConfig())

    assert sensor.distance_cm is None
    assert sensor.is_close is False


def test_distance_cm_converts_gpiozero_meters_to_centimeters() -> None:
    sensor = UltrasonicSensor(UltrasonicConfig(close_distance_cm=25.0), PinConfig())
    sensor._sensor = FakeDistanceSensor(0.2)

    assert sensor.distance_cm == 20.0
    assert sensor.is_close is True


def test_distance_readings_are_smoothed() -> None:
    sensor = UltrasonicSensor(UltrasonicConfig(ema_alpha=0.5), PinConfig())
    fake_sensor = FakeDistanceSensor(0.2)
    sensor._sensor = fake_sensor

    assert sensor.distance_cm == 20.0
    fake_sensor.distance = 0.4

    assert sensor.distance_cm == 30.0


def test_stop_closes_sensor() -> None:
    sensor = UltrasonicSensor(UltrasonicConfig(), PinConfig())
    fake_sensor = FakeDistanceSensor(0.2)
    sensor._sensor = fake_sensor

    sensor.stop()

    assert fake_sensor.closed is True
    assert sensor.distance_cm is None


class FailingDistanceSensor:
    def __init__(self) -> None:
        self.closed = False

    @property
    def distance(self) -> float:
        raise OSError("simulated ultrasonic timeout")

    def close(self) -> None:
        self.closed = True


def test_distance_returns_last_known_below_failure_threshold() -> None:
    sensor = UltrasonicSensor(UltrasonicConfig(max_consecutive_failures=3), PinConfig())
    sensor._sensor = FakeDistanceSensor(0.2)
    assert sensor.distance_cm == 20.0

    sensor._sensor = FailingDistanceSensor()
    assert sensor.distance_cm == 20.0
    assert sensor.distance_cm == 20.0


def test_distance_returns_none_after_max_consecutive_failures() -> None:
    sensor = UltrasonicSensor(UltrasonicConfig(max_consecutive_failures=2), PinConfig())
    sensor._sensor = FakeDistanceSensor(0.2)
    assert sensor.distance_cm == 20.0

    sensor._sensor = FailingDistanceSensor()
    assert sensor.distance_cm == 20.0
    assert sensor.distance_cm is None
    assert sensor.is_close is False


def test_is_close_hysteresis_stays_close_until_clear_threshold() -> None:
    config = UltrasonicConfig(
        close_distance_cm=25.0,
        close_clear_distance_cm=35.0,
        ema_alpha=1.0,
    )
    sensor = UltrasonicSensor(config, PinConfig())
    fake = FakeDistanceSensor(0.5)
    sensor._sensor = fake

    assert sensor.is_close is False

    fake.distance = 0.20
    assert sensor.is_close is True

    fake.distance = 0.30
    assert sensor.is_close is True

    fake.distance = 0.40
    assert sensor.is_close is False


def test_consecutive_failure_counter_resets_on_success() -> None:
    config = UltrasonicConfig(max_consecutive_failures=3)
    sensor = UltrasonicSensor(config, PinConfig())
    fake = FakeDistanceSensor(0.2)
    sensor._sensor = fake
    assert sensor.distance_cm == 20.0

    sensor._sensor = FailingDistanceSensor()
    _ = sensor.distance_cm
    _ = sensor.distance_cm
    assert sensor._consecutive_failures == 2

    sensor._sensor = fake
    _ = sensor.distance_cm
    assert sensor._consecutive_failures == 0
