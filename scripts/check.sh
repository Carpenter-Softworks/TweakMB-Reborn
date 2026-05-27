#!/bin/bash

. "$(dirname "$0")"/lib/get_dir.sh

REQUIRED_PYTHON_MAJOR="3"
REQUIRED_PYTHON_MINOR="13"

set -e

cd "$DIR/.."

echo "Checking version of $(which python3)..."

if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH. Exiting."
    echo "Please install Python ${REQUIRED_PYTHON_MAJOR}.${REQUIRED_PYTHON_MINOR} or higher and add it to PATH."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
if [[ -z "$PYTHON_VERSION" ]]; then
    echo "ERROR: Could not determine Python version. Exiting."
    exit 2
fi
echo "Detected Python version: ${PYTHON_VERSION}"

IFS='.' read -r -a ver_parts <<< "$PYTHON_VERSION"
PYTHON_MAJOR="${ver_parts[0]}"
PYTHON_MINOR="${ver_parts[1]}"

if [[ "$PYTHON_MAJOR" -lt "$REQUIRED_PYTHON_MAJOR" ]] || \
   [[ "$PYTHON_MAJOR" -eq "$REQUIRED_PYTHON_MAJOR" && "$PYTHON_MINOR" -lt "$REQUIRED_PYTHON_MINOR" ]]; then
    echo "ERROR: Python version ${PYTHON_VERSION} is below the required ${REQUIRED_PYTHON_MAJOR}.${REQUIRED_PYTHON_MINOR}. Exiting."
    echo "Please upgrade to Python ${REQUIRED_PYTHON_MAJOR}.${REQUIRED_PYTHON_MINOR} or higher."
    exit 3
fi
echo "Python version check passed. (>= ${REQUIRED_PYTHON_MAJOR}.${REQUIRED_PYTHON_MINOR})"

if [[ ! -d "$DIR/../.venv" ]]; then
    echo "WARNING: No .venv found in project root. Run 'make install' to set up the virtual environment."
else
    echo "Virtual environment (.venv) found."
fi

echo "Checking for pnpm..."
if ! command -v pnpm &> /dev/null; then
    echo "ERROR: pnpm is not installed or not in PATH. Exiting."
    echo "Please install pnpm (see https://pnpm.io/installation) to manage Node.js dependencies."
    exit 4
fi
echo "pnpm version $(pnpm --version) found."

cd - > /dev/null
