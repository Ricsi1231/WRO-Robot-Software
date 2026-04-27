#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"
source "$PROJECT_DIR/.venv/bin/activate"

echo "=== Ruff fix ==="
ruff check --fix .

echo ""
echo "=== Ruff format ==="
ruff format .

echo ""
echo "Done."
