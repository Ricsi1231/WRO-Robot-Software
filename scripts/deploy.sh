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

cd "$PROJECT_DIR"

echo "Deploying to $PI_HOST:$PI_DIR ..."

rsync -avz \
    --exclude '.git' \
    --exclude '.venv' \
    --exclude '__pycache__' \
    --exclude '.mypy_cache' \
    --exclude '.pytest_cache' \
    --exclude '.ruff_cache' \
    --exclude 'tests' \
    --exclude 'scripts' \
    --exclude '.github' \
    --exclude '.pre-commit-config.yaml' \
    --exclude 'deploy.env' \
    --exclude 'deploy.env.example' \
    --exclude 'Makefile' \
    ./ "$PI_HOST:$PI_DIR/"

echo ""
echo "Deploy complete."
