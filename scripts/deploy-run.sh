#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

SCRIPT="${1:-main.py}"

"$SCRIPT_DIR/deploy.sh"

echo ""

"$SCRIPT_DIR/run.sh" "$SCRIPT"
