#!/bin/bash

# Sets VENV_BIN and EXE for the platform-appropriate venv executable layout:
#   Windows (Git Bash / MSYS / Cygwin): VENV_BIN=.venv/Scripts  EXE=.exe
#   POSIX   (Linux / macOS):            VENV_BIN=.venv/bin      EXE=
# Bash auto-appends .exe only for PATH lookups, not explicit paths,
# so call sites must use "$VENV_BIN/python$EXE" etc.
# Prefer existence-based detection so a .venv created by a different toolchain
# is still respected. Fall back to $OSTYPE when neither directory exists yet
# (first-time install). Must be sourced after cd-ing to the project root.

if [[ -d ".venv/Scripts" ]]; then
    VENV_BIN=".venv/Scripts"
    EXE=".exe"
elif [[ -d ".venv/bin" ]]; then
    VENV_BIN=".venv/bin"
    EXE=""
else
    case "$OSTYPE" in
        msys*|cygwin*|win32*) VENV_BIN=".venv/Scripts"; EXE=".exe" ;;
        *)                    VENV_BIN=".venv/bin";     EXE=""     ;;
    esac
fi
