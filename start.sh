#!/bin/bash
set -e
echo "Starting setup process..."

echo "📦 Syncing dependencies with uv..."
uv sync

echo "Starting Flask server..."
uv run python main.py