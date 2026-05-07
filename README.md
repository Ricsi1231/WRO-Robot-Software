# WRO Robot Software

Python control software for a WRO robot running on a Raspberry Pi. The project wires together motor control, steering, encoder feedback, reflectance sensors, camera color detection, race-state logic, PID utilities, and a small path planner.

The code is structured so most control logic can be tested on a development machine, while Raspberry Pi-specific hardware libraries are imported only when the robot runtime starts.

## Requirements

- Python 3.11 or newer
- Raspberry Pi for real robot runs
- Camera support through `picamera2`
- GPIO/PWM support through `gpiozero`
- Encoder support through `pigpio`
- Local development dependencies from `.[dev]`

Runtime dependencies declared by the package are `opencv-python` and `numpy`. Raspberry Pi hardware packages are imported lazily by the modules that need them, so unit tests can run without Pi hardware.

## Quick Start

Create the local virtual environment and install development tools:

```bash
make setup
source .venv/bin/activate
```

Run the full local check suite:

```bash
make check
```

Individual commands are also available:

```bash
make lint
make typecheck
make test
make format
```

`make format` rewrites files with Ruff fixes and formatting. Use `make check` when you only want validation.

## Running The Robot

`main.py` is the robot entry point. It creates a `PinConfig`, initializes `Robot`, registers the start button callback when configured, handles termination signals, and enters the main control loop.

On the Raspberry Pi target:

```bash
python3 main.py
```

From the development machine, configure deployment first:

```bash
cp deploy.env.example deploy.env
```

Then edit `deploy.env` for your Pi:

```bash
PI_HOST=rasberry@172.31.11.227
PI_DIR=/home/rasberry/robot
```

Deploy and run remotely:

```bash
make deploy
make run
make deploy-run
```

To run a different script remotely, pass it to the script wrapper:

```bash
./scripts/deploy-run.sh calibrate.py
```

## Calibration

`calibrate.py` captures one camera frame, prints HSV statistics for the center region, writes them to `calibrate.txt`, and writes `calibrate.jpg`. Use those values to tune the HSV thresholds in `VisionConfig`.

```bash
python3 calibrate.py
```

Generated calibration outputs are ignored by Git.

## Component Tests

Manual per-component test scripts live in `component_tests/`. Each component has its own `main.py` and uses shared pin values from `component_tests/hardware_config.py`.

Edit `TEST_PINS` before running hardware tests on the Pi, then run one component at a time:

```bash
./scripts/deploy-run.sh component_tests/motor/main.py
./scripts/deploy-run.sh component_tests/steering/main.py
./scripts/deploy-run.sh component_tests/motion/main.py
./scripts/deploy-run.sh component_tests/encoder/main.py
./scripts/deploy-run.sh component_tests/reflectance/main.py
./scripts/deploy-run.sh component_tests/camera/main.py
```

Software-only component tests can also run locally:

```bash
python3 component_tests/pid/main.py
python3 component_tests/path_planner/main.py
python3 component_tests/race_controller/main.py
```

## Project Layout

```text
.
├── main.py                 # Robot runtime entry point
├── calibrate.py            # Camera HSV calibration helper
├── component_tests/        # Manual per-component test entrypoints
├── wro/                    # Robot software package
├── tests/                  # Unit tests for off-device logic
├── scripts/                # Setup, check, deploy, and run scripts
├── Makefile                # Common developer commands
└── docs/                   # Project documentation
```

Key modules:

- `wro.robot`: top-level composition, lifecycle, run loop, and cleanup.
- `wro.race_controller`: race state machine and obstacle/corner behavior.
- `wro.motion_controller`: velocity and steering commands.
- `wro.motor_driver`: GPIO/PWM motor driver wrapper.
- `wro.encoder`: quadrature encoder tracking and RPM calculation.
- `wro.reflectance_sensor`: orange/green reflectance inputs.
- `wro.vision`: camera frame processing and red/green detection.
- `wro.pid`: PID controller utility.
- `wro.path_planner`: waypoint graph and A* path planning utility.
- `wro.config`: dataclass configuration defaults.

## Documentation

- [Architecture](docs/architecture.md)
- [Hardware and Configuration](docs/hardware-and-config.md)
- [Deployment](docs/deployment.md)
- [Calibration](docs/calibration.md)

## Development Workflow

The standard validation path is:

```bash
make check
```

This runs:

- `ruff check .`
- `ruff format --check .`
- `mypy wro/ main.py calibrate.py component_tests`
- `pytest`

CI runs the same checks on GitHub Actions for pushes to `dev` and pull requests targeting `main`.
