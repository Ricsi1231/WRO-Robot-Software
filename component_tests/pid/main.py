from __future__ import annotations

# ruff: noqa: E402
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from wro.config import PidConfig
from wro.pid import PIDController


def main() -> None:
    pid = PIDController(PidConfig(kp=0.8, ki=0.15, kd=0.05, max_output=100.0))
    setpoint = 50.0
    measured = 0.0

    print("step,setpoint,measured,output,error,settled")
    for step in range(20):
        output = pid.compute(setpoint, measured)
        measured += output * 0.05
        print(f"{step},{setpoint:.2f},{measured:.2f},{output:.2f},{pid.last_error:.2f},{pid.is_settled}")
        time.sleep(0.05)


if __name__ == "__main__":
    main()
