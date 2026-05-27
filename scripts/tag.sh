#!/bin/bash

. "$(dirname "$0")"/lib/get_dir.sh

set -e

cd "$DIR/.."

# Only prompt for version if not already set (e.g., by release.sh)
if [[ -z "$VERSION" ]]; then
    . "$(dirname "$0")"/lib/get_version.sh
fi

echo "Creating and pushing tag ${VERSION}..."

git tag -a -s "${VERSION}" -m "Release ${VERSION}"
if [ $? -ne 0 ]; then
    echo "Git tag creation failed. Exiting."
    exit 2
fi

git push origin "${VERSION}"
if [ $? -ne 0 ]; then
    echo "Failed to push tag. Exiting."
    exit 3
fi

cd - > /dev/null
