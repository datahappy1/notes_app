# -*- mode: python ; coding: utf-8 -*-
from kivy_deps import sdl2, glew

block_cipher = None


a = Analysis(
    ["notes_app\\main.py"],
    pathex=[],
    binaries=[],
    datas=[("notes_app\\view\\notes_view.kv", "notes_app\\view\\")],
    hiddenimports=[],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
    name="notes",
    debug=False,
    bootloader_ignore_signals=False,
    upx=True,
    console=False,
    strip=False,
    upx_exclude=[],
)
