#!/bin/bash

# get_version.sh: Derive and prompt for a semantic version
#
# Exports:
#   VERSION: The selected version (set by caller or derived from git tags)
#
# Environment variables:
#   REVISION: If set, uses this as VERSION (for non-interactive mode)

get_version() {
    local new_version="1.0.0-SNAPSHOT"

    if [[ -n "$REVISION" ]]; then
        VERSION="$REVISION"
    else
        read -p "Enter the new version [${new_version}]: " VERSION
        VERSION=${VERSION:-$new_version}
        if [[ -z "$VERSION" ]]; then
            echo "Version is required. Exiting."
            exit 1
        fi
    fi

    export VERSION
}

get_version "$@"
