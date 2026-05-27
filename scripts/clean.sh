#!/bin/bash

. "$(dirname "$0")"/lib/get_dir.sh

set -e

cd "$DIR/.."

echo "Removing Python build artifacts..."
find . -type d -name "__pycache__" -not -path "./.venv/*" -not -path "./node_modules/*" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "*.egg-info" -not -path "./.venv/*" -not -path "./node_modules/*" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".pytest_cache" -not -path "./.venv/*" -not -path "./node_modules/*" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".ruff_cache" -not -path "./.venv/*" -not -path "./node_modules/*" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "dist" -not -path "./.venv/*" -not -path "./node_modules/*" -exec rm -rf {} + 2>/dev/null || true

echo "Removing Node.js artifacts..."
rm -rf node_modules pnpm-debug.log*

echo "Clean complete."

cd - > /dev/null
