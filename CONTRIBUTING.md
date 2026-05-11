# Contributing

Short guide for working on the WRO Robot Software.

## Setup

```bash
make setup
source .venv/bin/activate
```

This creates `.venv`, installs the package with dev extras, and registers pre-commit hooks.

## Day-to-day

Before pushing, run:

```bash
make check
```

This runs the same checks as CI: ruff lint, ruff format check, mypy, and pytest.

To auto-fix lint/format issues:

```bash
make format
```

For local coverage feedback:

```bash
make coverage
```

## Tests

There are two kinds:

- **Unit tests** in `tests/` — pure Python, no hardware. These run in CI and on every pre-commit. They use mocks for hardware libraries (`gpiozero`, `pigpio`, `picamera2`).
- **Component / hardware tests** in `component_tests/` — manual scripts that exercise a single subsystem against a real Raspberry Pi. **Not collected by pytest** and **not run in CI**. Run them via `make deploy-run` or `./scripts/deploy-run.sh component_tests/<name>/main.py`.

Tests that need a real Pi should be marked `@pytest.mark.hardware` so they remain easy to filter out (`pytest -m "not hardware"`).

## Style

- `ruff` enforces formatting and a focused lint selection (`E F I UP B SIM W RUF`).
- `mypy --disallow-untyped-defs` covers `wro/`, `main.py`, `calibrate.py`, and `component_tests/`. New code must include type annotations.
- Line length is 120.
- Configuration lives in `wro/config.py` as dataclasses with `__post_init__` validators. Add validators when introducing new fields — they have caught real bugs (see PR 1).

## Pull requests

CI runs on every PR targeting `main`, and on pushes to `dev`. Keep PRs small and focused; the recent history is a good template.

## Deploying to the Pi

Copy `deploy.env.example` to `deploy.env`, fill in `PI_HOST` and `PI_DIR`, then:

```bash
make deploy        # rsync project to the Pi
make run           # run main.py over SSH
make deploy-run    # both, with a one-shot script wrapper
```
