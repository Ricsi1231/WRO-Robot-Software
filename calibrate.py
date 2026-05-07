import cv2
import numpy as np

CALIBRATION_TEXT_FILE = "calibrate.txt"


def _hsv_stats_text(channel_name: str, channel: np.ndarray) -> str:
    return f"  {channel_name}: min={channel.min()}  max={channel.max()}  mean={channel.mean():.0f}"


if __name__ == "__main__":
    from picamera2 import Picamera2

    picam2 = Picamera2()
    config = picam2.create_still_configuration(main={"format": "RGB888"})
    picam2.configure(config)
    picam2.start()

    frame = picam2.capture_array()
    hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

    h, w = frame.shape[:2]
    center = hsv[h // 4 : 3 * h // 4, w // 4 : 3 * w // 4]

    stats_lines = [
        "Center region HSV stats:",
        _hsv_stats_text("H", center[:, :, 0]),
        _hsv_stats_text("S", center[:, :, 1]),
        _hsv_stats_text("V", center[:, :, 2]),
    ]

    print("\n".join(stats_lines))

    with open(CALIBRATION_TEXT_FILE, "w", encoding="utf-8") as calibration_file:
        calibration_file.write("\n".join(stats_lines))
        calibration_file.write("\n")
    print(f"Saved {CALIBRATION_TEXT_FILE}")

    cv2.imwrite("calibrate.jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
    print("Saved calibrate.jpg")

    picam2.stop()
