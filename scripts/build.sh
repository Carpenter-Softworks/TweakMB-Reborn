#!/bin/bash

. "$(dirname "$0")"/lib/get_dir.sh

set -e

cd "$DIR/.."

# Only prompt for version if not already set (e.g., by release.sh)
if [[ -z "$VERSION" ]]; then
    . "$(dirname "$0")"/lib/get_version.sh
fi

echo "Running pyinstaller..."

pyinstaller tweakmb.spec --noconfirm

echo "Moving tweaks_native_1174.json..."

mv dist/TweakMB/_internal/tweaks_native_1174.json dist/TweakMB

echo "Renaming output directory..."

mv dist/TweakMB dist/TweakMB-Reborn

cd - > /dev/null
