# Architecture

This project is organized around a small runtime composition layer and testable control modules. `main.py` creates a `Robot`, initializes it, connects the optional start button callback, registers shutdown handlers, and starts the loop.

## Runtime Lifecycle

`Robot` owns the main runtime objects:

- Drive and steering `MotorDriver` instances
- `MotionController`
- `Encoder`
- `PIDController`
- `ReflectanceSensor`
- `Camera`
- `RaceController`

`Robot.init()` initializes hardware-facing components in order, starts the sensors and camera, then resets the race controller. If startup fails, it prints the traceback, cleans up initialized resources, and re-raises the exception.

`Robot.run()` executes the race controller every `MAIN_LOOP_INTERVAL_S`, currently 20 ms. `Robot.shutdown()` stops the loop and closes camera, reflectance, encoder, and motion resources.

## Race State Machine

`RaceController` is the main behavior controller. It has four states:

- `IDLE`: waits for `on_start_signal()`.
- `RUNNING`: drives the race behavior.
- `STOPPING`: stops motion after the configured lap count is reached.
- `FINISHED`: terminal state after the robot stops.

On start, the controller resets encoder position, PID state, corner count, and lap count, then starts moving at `RaceConfig.cruise_velocity`.

While running:

- Camera red detection triggers a temporary right avoidance steer.
- Camera green detection triggers a temporary left avoidance steer.
- Orange reflectance detection counts corners after debounce.
- Every `RaceConfig.corners_per_lap` corners increments the lap count.
- When `RaceConfig.total_laps` is reached, the state moves to `STOPPING`.

## Motion And Motors

`MotionController` turns normalized velocity and steering-angle requests into motor-driver commands.

- Velocity is clamped to `-1.0..1.0`.
- Small velocity values inside `MotionConfig.velocity_deadzone` stop the drive motor.
- Direction changes across forward/reverse use `MotorDriver.set_direction_safe()`, which ramps down before reversing.
- Steering angles are clamped by `MotionConfig.max_steering_angle`.
- Steering speed is interpolated between `SteeringConfig.min_speed_percent` and `SteeringConfig.max_speed_percent`.

`MotorDriver` wraps a PWM enable pin and two direction pins. It can coast with `stop()`, actively brake with `brake()`, clamp speed percentages, and ramp speed during safe direction changes.

## Sensors And Vision

`Encoder` uses `pigpio` callbacks for quadrature encoder edges when both encoder pins are configured. It tracks ticks and periodically calculates raw and exponentially smoothed RPM.

`ReflectanceSensor` uses two optional `gpiozero.Button` inputs and reports `ORANGE`, `GREEN`, or `UNKNOWN`.

`Camera` uses `picamera2` video callbacks. Each RGB frame is converted to HSV and passed to `detect_color()`, which counts red and green mask pixels using OpenCV thresholds from `VisionConfig`.

Hardware imports happen inside startup methods. This keeps imports and most tests usable on machines without Raspberry Pi libraries installed.

## Utility Modules

`PIDController` provides proportional, integral, and derivative control with output clamping, integral anti-windup, derivative smoothing, and settled/error state tracking.

`PathPlanner` provides a small waypoint graph with A* search. It supports Manhattan, Euclidean, and octagonal heuristics, blocked nodes, duplicate-edge handling, and map clearing.

