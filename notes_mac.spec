# -*- mode: python ; coding: utf-8 -*-
from kivymd.icon_definitions import md_icons

a = Analysis(
    ['notes_app/main.py'],
    pathex=[],
    binaries=[],
    datas=[("notes_app/view/notes_view.kv", "notes_app/view/")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='notes',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Notes',
)
app = BUNDLE(
    coll,
    name='notes.app',
    version='1.0.0',
    icon="notes_app/assets/notes_app_icon.ico",
    bundle_identifier='com.github.datahappy1.notes_app',
    info_plist={
        'NSHighResolutionCapable': 'False',
    },
)