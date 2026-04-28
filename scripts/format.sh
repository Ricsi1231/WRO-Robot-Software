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

echo "=== Ruff fix ==="
ruff check --fix .

echo ""
echo "=== Ruff format ==="
ruff format .

echo ""
echo "Done."
