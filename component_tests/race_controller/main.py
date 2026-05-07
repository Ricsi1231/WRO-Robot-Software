from __future__ import annotations

# ruff: noqa: E402
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from wro.config import RaceConfig
from wro.race_controller import RaceController
from wro.reflectance_sensor import ReflectanceClass
from wro.vision import DetectionResult


class FakeMotion:
    def __init__(self) -> None:
        self.velocity = 0.0
        self.steering_angle = 0.0

    def set_velocity(self, velocity: float) -> None:
        self.velocity = velocity
        print(f"motion.velocity={velocity:.2f}")

    def set_steering_angle(self, angle_deg: float) -> None:
        self.steering_angle = angle_deg
        print(f"motion.steering_angle={angle_deg:.2f}")

    def stop(self) -> None:
        self.velocity = 0.0
        print("motion.stop")


class FakeEncoder:
    def reset_position(self) -> None:
        print("encoder.reset_position")


class FakePid:
    def reset(self) -> None:
        print("pid.reset")


class FakeReflectance:
    def __init__(self) -> None:
        self.detected_class = ReflectanceClass.UNKNOWN


class FakeCamera:
    def __init__(self) -> None:
        self.latest_detection = DetectionResult(0, 0, False, False)


def main() -> None:
    config = RaceConfig(
        total_laps=1,
        corners_per_lap=2,
        corner_debounce_s=0.0,
        corner_steer_duration_s=0.01,
        pillar_steer_duration_s=0.01,
    )
    motion = FakeMotion()
    encoder = FakeEncoder()
    reflectance = FakeReflectance()
    pid = FakePid()
    camera = FakeCamera()
    controller = RaceController(config, motion, encoder, reflectance, pid, camera)  # type: ignore[arg-type]

    controller.start()
    print(f"state={controller.state.name}")
    controller.on_start_signal()
    controller.update()
    print(f"state={controller.state.name}")

    camera.latest_detection = DetectionResult(1000, 0, True, False)
    controller.update()
    time.sleep(0.02)
    camera.latest_detection = DetectionResult(0, 0, False, False)
    controller.update()

    reflectance.detected_class = ReflectanceClass.ORANGE
    controller.update()
    time.sleep(0.02)
    controller.update()
    controller.update()
    print(f"corners={controller.corner_count} laps={controller.lap_count} state={controller.state.name}")
    controller.update()
    print(f"final_state={controller.state.name}")


if __name__ == "__main__":
    main()
