#!/bin/bash

. "$(dirname "$0")"/lib/get_dir.sh

set -e

cd "$DIR/.."

. scripts/lib/venv_bin.sh

if command -v python3 > /dev/null 2>&1; then
    PYTHON=python3
elif command -v python > /dev/null 2>&1; then
    PYTHON=python
else
    echo "ERROR: Neither python3 nor python found in PATH." >&2
    exit 1
fi

if [[ ! -d ".venv" ]]; then
    echo "Creating virtual environment..."
    "$PYTHON" -m venv .venv
    . scripts/lib/venv_bin.sh
fi

echo "Installing dev dependencies (Python)..."
"$VENV_BIN/pip$EXE" install -e ".[dev]"

echo "Installing dev dependencies (Node.js) via pnpm..."
if ! command -v pnpm > /dev/null 2>&1; then
    case "$OSTYPE" in
        msys*|cygwin*|win32*)
            if command -v npm > /dev/null 2>&1; then
                echo "pnpm not found. Installing via 'npm install -g pnpm'..."
                npm install -g pnpm
            else
                echo "ERROR: pnpm not found and npm is unavailable." >&2
                echo "Install pnpm on Windows via one of:" >&2
                echo "  - npm install -g pnpm" >&2
                echo "  - winget install pnpm.pnpm" >&2
                echo "  - iwr https://get.pnpm.io/install.ps1 -useb | iex   (PowerShell)" >&2
                exit 1
            fi
            ;;
        *)
            echo "pnpm not found. Attempting to install pnpm via standalone script..."
            if command -v curl > /dev/null 2>&1; then
                curl -fsSL https://get.pnpm.io/install.sh | sh -
            elif command -v wget > /dev/null 2>&1; then
                wget -qO- https://get.pnpm.io/install.sh | sh -
            else
                echo "ERROR: pnpm not found and neither curl nor wget is available." >&2
                echo "Please install pnpm manually: https://pnpm.io/installation" >&2
                exit 1
            fi
            # Add to PATH for the current session
            export PNPM_HOME="$HOME/.local/share/pnpm"
            case ":$PATH:" in
                *":$PNPM_HOME:"*) ;;
                *) export PATH="$PNPM_HOME:$PATH" ;;
            esac
            ;;
    esac
fi

if ! command -v pnpm > /dev/null 2>&1; then
    echo "ERROR: pnpm installation failed or not in PATH." >&2
    exit 1
fi

pnpm install --silent

echo "Regenerating requirements.txt..."
"$VENV_BIN/python$EXE" -m piptools compile --strip-extras --output-file=requirements.txt pyproject.toml

cd - > /dev/null
