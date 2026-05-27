#!/bin/bash

. "$(dirname "$0")"/lib/get_dir.sh

set -e

cd "$DIR/.."

# Only prompt for version if not already set (e.g., by release.sh)
if [[ -z "$VERSION" ]]; then
    . "$(dirname "$0")"/lib/get_version.sh
fi

echo "Cleaning up..."

rm -rf dist/TweakMB-Reborn

echo "Running pyinstaller..."

pyinstaller tweakmb.spec --noconfirm

echo "Moving tweaks_native_1174.json..."

mv dist/TweakMB/_internal/tweaks_native_1174.json dist/TweakMB

echo "Renaming output directory..."

mv dist/TweakMB dist/TweakMB-Reborn

echo "Zipping dist/TweakMB-Reborn..."

cd dist
if command -v zip &>/dev/null; then
    zip -r TweakMB-Reborn.zip TweakMB-Reborn
else
    python -c "
import zipfile, pathlib
with zipfile.ZipFile('TweakMB-Reborn.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
    for p in pathlib.Path('TweakMB-Reborn').rglob('*'):
        zf.write(p)
"
fi
cd - > /dev/null

echo "Cleaning up..."

rm -rf dist/TweakMB-Reborn

cd - > /dev/null
