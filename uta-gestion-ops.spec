# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path

msys2_bin = Path('C:/msys64/mingw64/bin')

weasyprint_dlls = [
    'libgobject-2.0-0.dll',
    'libglib-2.0-0.dll',
    'libpango-1.0-0.dll',
    'libpangoft2-1.0-0.dll',
    'libpangowin32-1.0-0.dll',
    'libpangocairo-1.0-0.dll',
    'libharfbuzz-0.dll',
    'libfontconfig-1.dll',
    'libfreetype-6.dll',
    'libcairo-2.dll',
    'libcairo-gobject-2.dll',
    'libpixman-1-0.dll',
    'libpng16-16.dll',
    'zlib1.dll',
    'libintl-8.dll',
    'libiconv-2.dll',
    'libffi-8.dll',
    'libpcre2-8-0.dll',
    'libbz2-1.dll',
    'libbrotlicommon.dll',
    'libbrotlidec.dll',
    'libexpat-1.dll',
    'libgraphite2.dll',
    'libstdc++-6.dll',
    'libgcc_s_seh-1.dll',
    'libwinpthread-1.dll',
]

binaries_list = []
if msys2_bin.exists():
    for dll in weasyprint_dlls:
        dll_path = msys2_bin / dll
        if dll_path.exists():
            binaries_list.append((str(dll_path), '.'))

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries_list,
    datas=[('D:\\Proyectos\\uta-gestion-ops\\.venv\\Lib\\site-packages\\nicegui', 'nicegui')],
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
    name='uta-gestion-ops',
    debug=False,
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
    name='uta-gestion-ops',
)
