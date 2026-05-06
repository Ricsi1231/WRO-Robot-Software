# Hardware And Configuration

All default configuration is defined in `wro.config` as dataclasses. The project currently uses code defaults directly; there is no external config file loader.

## Pin Configuration

`PinConfig` defines the Raspberry Pi GPIO pins used by the robot:

| Field | Purpose | Default |
| --- | --- | --- |
| `drive_en` | Drive motor PWM/enable pin | `None` |
| `drive_in1` | Drive motor direction pin 1 | `None` |
| `drive_in2` | Drive motor direction pin 2 | `None` |
| `steer_en` | Steering motor PWM/enable pin | `None` |
| `steer_in1` | Steering motor direction pin 1 | `None` |
| `steer_in2` | Steering motor direction pin 2 | `None` |
| `encoder_a` | Encoder channel A | `None` |
| `encoder_b` | Encoder channel B | `None` |
| `reflectance_orange` | Orange/corner reflectance input | `None` |
| `reflectance_green` | Green reflectance input | `None` |
| `button` | Start button input | `23` |

Most pins default to `None`, which disables those hardware outputs or inputs. Set real pin numbers before running on the physical robot.

## Motor And Motion Configuration

`MotorConfig` controls PWM frequency, speed ramping, and minimum effective motor speed.

`SteeringConfig` controls steering motor PWM frequency, maximum steering angle, and the speed range used while steering.

`MotionConfig` controls normalized velocity conversion, forward motor direction, deadzones, maximum steering angle, and whether steering is centered on stop.

## Sensor Configuration

`EncoderConfig` controls pulses per revolution, RPM calculation interval, and exponential moving average smoothing.

`ReflectanceConfig` controls reflectance input debounce time.

`VisionConfig` contains HSV threshold arrays for red and green detection plus `min_pixel_count`, the minimum number of masked pixels required for a detection flag.

## Race Configuration

`RaceConfig` controls behavior-level tuning:

- Cruise and corner velocities
- Pillar avoidance angle and duration
- Corner steering angle and duration
- Corner debounce timing
- Corners per lap and total laps
- Clockwise/counter-clockwise corner steering direction

## Raspberry Pi Runtime Libraries

The following libraries are used at runtime on the Pi:

- `gpiozero` for motor outputs, reflectance inputs, start button, and servo support.
- `pigpio` for encoder callbacks.
- `picamera2` for camera capture.
- `opencv-python` and `numpy` for image processing.

The Pi-specific imports are intentionally inside runtime methods such as `init()` and `start()`. This lets unit tests run on a development machine without Pi hardware packages.

