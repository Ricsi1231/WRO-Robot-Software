#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_DIR/deploy.env"

if [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"
fi

PI_HOST="${PI_HOST:-rasberry@172.31.11.227}"
PI_DIR="${PI_DIR:-/home/rasberry/robot}"

SCRIPT="${1:-main.py}"

echo "Running $SCRIPT on $PI_HOST ..."
ssh "$PI_HOST" "cd '$PI_DIR' && python3 '$SCRIPT'"
