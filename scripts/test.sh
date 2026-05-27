#!/bin/bash

. "$(dirname "$0")"/lib/get_dir.sh

set -e

cd "$DIR/.."

. scripts/lib/venv_bin.sh

echo "Running ruff lint check..."
"$VENV_BIN/ruff$EXE" check .

echo "Running pyright type check..."
"$VENV_BIN/pyright$EXE"

echo "Running jscpd copy-paste check..."
if ! command -v pnpm > /dev/null 2>&1; then
	echo "ERROR: pnpm not found. Run 'make check' to verify your environment." >&2
	exit 1
fi
pnpm exec jscpd

echo "Running vulture dead code check..."
"$VENV_BIN/vulture$EXE" src/ tests/ --min-confidence 80

echo "Running pytest..."
"$VENV_BIN/pytest$EXE"

cd - > /dev/null
