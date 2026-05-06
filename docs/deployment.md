# Deployment

Deployment is handled by shell scripts in `scripts/` and Makefile targets. The scripts assume SSH access to a Raspberry Pi.

## Configure The Target

Create a private deployment environment file:

```bash
cp deploy.env.example deploy.env
```

Edit `deploy.env`:

```bash
PI_HOST=pi@raspberrypi.local
PI_DIR=/home/pi/robot
```

`deploy.env` is ignored by Git so local hostnames, usernames, and paths are not committed.

## Deploy Files

Deploy with:

```bash
make deploy
```

This runs `scripts/deploy.sh`, which uses `rsync` to copy the project to `$PI_HOST:$PI_DIR/`.

The deployment excludes development-only files and directories:

- `.git`
- `.venv`
- Python caches
- Mypy, Pytest, and Ruff caches
- `tests`
- `scripts`
- `.github`
- `.pre-commit-config.yaml`
- `deploy.env`
- `deploy.env.example`
- `Makefile`

## Run Remotely

Run the default robot entry point on the Pi:

```bash
make run
```

This runs:

```bash
ssh "$PI_HOST" "cd '$PI_DIR' && python3 'main.py'"
```

Run a specific script:

```bash
./scripts/run.sh calibrate.py
```

Deploy and then run in one command:

```bash
make deploy-run
```

Or deploy and run a specific script:

```bash
./scripts/deploy-run.sh calibrate.py
```

## Pi Setup Expectations

The Pi should have:

- Python 3.11 or newer
- Project runtime dependencies installed
- Pi hardware libraries available: `gpiozero`, `pigpio`, `picamera2`
- SSH access from the development machine
- A writable target directory matching `PI_DIR`

The current deployment script copies source files. It does not install system packages or create a remote virtual environment.

