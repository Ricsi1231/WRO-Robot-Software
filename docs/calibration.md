# Calibration

`calibrate.py` is a Raspberry Pi camera helper for tuning HSV color thresholds.

## What It Does

The script:

1. Starts `Picamera2`.
2. Captures one RGB frame.
3. Converts the frame to HSV with OpenCV.
4. Selects the center half of the image.
5. Prints min, max, and mean HSV values for that center region.
6. Saves those HSV values as `calibrate.txt`.
7. Saves the captured frame as `calibrate.jpg`.
8. Stops the camera.

Run it on the Pi:

```bash
python3 calibrate.py
```

Or from the development machine after deployment configuration:

```bash
./scripts/deploy-run.sh calibrate.py
```

## Using The Output

Place the color target in the center of the camera view, run calibration, and compare the printed HSV stats, or the saved values in `calibrate.txt`, to the thresholds in `VisionConfig`.

Relevant fields:

- `red_lower_1` and `red_upper_1`
- `red_lower_2` and `red_upper_2`
- `green_lower` and `green_upper`
- `min_pixel_count`

Red uses two hue ranges because red wraps around the HSV hue boundary. Green uses one configured range.

`detect_color()` creates masks with `cv2.inRange()`, counts non-zero pixels, and marks a color as detected only when the count is greater than `min_pixel_count`.

## Generated Files

`calibrate.jpg` and `calibrate.txt` are ignored by Git. Calibration outputs are local artifacts and should not be committed unless the ignore rules are intentionally changed.
