# PyInstaller spec for TweakMB Reborn.
#
# Build (from project root):
#     pyinstaller tweakmb.spec --noconfirm
#
# Output: dist/TweakMB/TweakMB.exe with tweaks_native_1174.json sitting
# next to it (and DearPyGui's native bits in the same folder). End-users
# can edit the JSON; the app reads it from beside the executable on
# startup (see src/ui/app.py).

from PyInstaller.utils.hooks import collect_submodules

block_cipher = None


a = Analysis(
    ['src/main.py'],
    pathex=['src'],
    binaries=[],
    datas=[('src/data/tweaks_native_1174.json', '.')],
    hiddenimports=collect_submodules('dearpygui'),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TweakMB',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='TweakMB',
    # Flatten dist/TweakMB/ so the JSON, exe, and DLLs share one folder
    # instead of being tucked under _internal/.
    contents_directory='.',
)
