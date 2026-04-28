from __future__ import annotations

import time
from unittest.mock import patch

from wro.config import PidConfig
from wro.pid import PIDController

FIXED_TIME = 1000.0


def _make_pid(kp: float = 1.0, ki: float = 0.0, kd: float = 0.0) -> PIDController:
    return PIDController(PidConfig(kp=kp, ki=ki, kd=kd))


def test_proportional_only() -> None:
    pid = _make_pid(kp=2.0)
    with patch.object(time, "monotonic", side_effect=[FIXED_TIME, FIXED_TIME + 0.02]):
        pid.compute(100.0, 0.0)
        output = pid.compute(100.0, 50.0)
    assert output == 100.0


def test_output_clamped() -> None:
    pid = _make_pid(kp=10.0)
    with patch.object(time, "monotonic", side_effect=[FIXED_TIME, FIXED_TIME + 0.02]):
        pid.compute(100.0, 0.0)
        output = pid.compute(100.0, 0.0)
    assert output == 100.0


def test_settled_within_epsilon() -> None:
    pid = _make_pid(kp=1.0)
    with patch.object(time, "monotonic", side_effect=[FIXED_TIME, FIXED_TIME + 0.02]):
        pid.compute(50.0, 50.0)
        pid.compute(50.0, 49.5)
    assert pid.is_settled


def test_not_settled_outside_epsilon() -> None:
    pid = _make_pid(kp=1.0)
    with patch.object(time, "monotonic", side_effect=[FIXED_TIME, FIXED_TIME + 0.02]):
        pid.compute(50.0, 50.0)
        pid.compute(50.0, 40.0)
    assert not pid.is_settled


def test_reset_clears_state() -> None:
    pid = _make_pid(kp=1.0)
    with patch.object(time, "monotonic", return_value=FIXED_TIME):
        pid.compute(100.0, 0.0)
    pid.reset()
    assert pid.output == 0.0
    assert pid.last_error == 0.0
    assert pid.is_settled


def test_set_parameters() -> None:
    pid = _make_pid(kp=1.0)
    pid.set_parameters(2.0, 0.5, 0.1)
    with patch.object(time, "monotonic", return_value=FIXED_TIME):
        output = pid.compute(10.0, 0.0)
    assert output == 20.0


def test_zero_error_zero_output() -> None:
    pid = _make_pid(kp=1.0)
    with patch.object(time, "monotonic", side_effect=[FIXED_TIME, FIXED_TIME + 0.02]):
        pid.compute(50.0, 50.0)
        output = pid.compute(50.0, 50.0)
    assert output == 0.0


def test_negative_error() -> None:
    pid = _make_pid(kp=1.0)
    with patch.object(time, "monotonic", side_effect=[FIXED_TIME, FIXED_TIME + 0.02]):
        pid.compute(0.0, 0.0)
        output = pid.compute(0.0, 50.0)
    assert output < 0
