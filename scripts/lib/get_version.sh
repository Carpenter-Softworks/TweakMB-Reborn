#!/bin/bash

# get_version.sh: Derive, prompt for, and apply a semantic version
#
# Exports:
#   VERSION: The selected version (set by caller or derived from pyproject.toml)
#
# Environment variables:
#   REVISION: If set, uses this as VERSION (for non-interactive mode)

get_version() {
    local new_version
    new_version=$(grep '^version = ' pyproject.toml 2>/dev/null | sed 's/version = "\(.*\)"/\1/')
    new_version="${new_version:-1.0.0-SNAPSHOT}"

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

    echo "Setting version ${VERSION} in pyproject.toml..."
    sed -i "s/^version = .*/version = \"${VERSION}\"/" pyproject.toml
}

get_version "$@"
