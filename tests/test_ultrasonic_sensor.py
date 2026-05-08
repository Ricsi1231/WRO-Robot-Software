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
