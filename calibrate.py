import cv2

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

    print("Center region HSV stats:")
    print(f"  H: min={center[:, :, 0].min()}  max={center[:, :, 0].max()}  mean={center[:, :, 0].mean():.0f}")
    print(f"  S: min={center[:, :, 1].min()}  max={center[:, :, 1].max()}  mean={center[:, :, 1].mean():.0f}")
    print(f"  V: min={center[:, :, 2].min()}  max={center[:, :, 2].max()}  mean={center[:, :, 2].mean():.0f}")

    cv2.imwrite("calibrate.jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
    print("Saved calibrate.jpg")

    picam2.stop()
