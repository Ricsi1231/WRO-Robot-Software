#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_DIR/deploy.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "Error: $ENV_FILE not found. Copy deploy.env.example and edit PI_HOST/PI_DIR." >&2
    exit 1
fi

# shellcheck disable=SC1090
source "$ENV_FILE"

if [ -z "${PI_HOST:-}" ] || [ -z "${PI_DIR:-}" ]; then
    echo "Error: PI_HOST and PI_DIR must both be set in $ENV_FILE." >&2
    exit 1
fi

SCRIPT="${1:-main.py}"

echo "Running $SCRIPT on $PI_HOST ..."
ssh -o ConnectTimeout=5 "$PI_HOST" "cd '$PI_DIR' && python3 '$SCRIPT'"
