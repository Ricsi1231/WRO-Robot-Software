#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

if [ ! -d "$PROJECT_DIR/.venv" ]; then
    echo "Error: .venv not found. Run 'make setup' first."
    exit 1
fi

source "$PROJECT_DIR/.venv/bin/activate"

FAILED=0

echo "=== Ruff lint ==="
if ruff check .; then
    echo "PASSED"
else
    FAILED=1
fi

echo ""
echo "=== Ruff format ==="
if ruff format --check .; then
    echo "PASSED"
else
    FAILED=1
fi

echo ""
echo "=== Mypy ==="
if mypy wro/ main.py calibrate.py component_tests; then
    echo "PASSED"
else
    FAILED=1
fi

echo ""
echo "=== Pytest ==="
if pytest; then
    echo "PASSED"
else
    FAILED=1
fi

echo ""
if [ "$FAILED" -eq 0 ]; then
    echo "All checks passed."
else
    echo "Some checks failed."
    exit 1
fi
