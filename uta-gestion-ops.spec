# -*- mode: python ; coding: utf-8 -*-
import tomllib
from pathlib import Path

from PyInstaller.utils.win32.versioninfo import (
    FixedFileInfo,
    StringFileInfo,
    StringStruct,
    StringTable,
    VarFileInfo,
    VarStruct,
    VSVersionInfo,
)

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

import nicegui
nicegui_path = Path(nicegui.__file__).parent

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries_list,
    datas=[
        (str(nicegui_path), 'nicegui'),
        ('templates', 'templates'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

with open('pyproject.toml', 'rb') as pyproject:
    project_version = tomllib.load(pyproject)['project']['version']

version_parts = [int(part) for part in project_version.split('.')]
while len(version_parts) < 4:
    version_parts.append(0)
filevers = tuple(version_parts[:4])

version_info = VSVersionInfo(
    ffi=FixedFileInfo(
        filevers=filevers,
        prodvers=filevers,
        mask=0x3F,
        flags=0,
        OS=0x40004,
        fileType=0x1,
        subtype=0x0,
        date=(0, 0),
    ),
    kids=[
        StringFileInfo(
            [
                StringTable(
                    '040904B0',
                    [
                        StringStruct('CompanyName', 'UTA'),
                        StringStruct('FileDescription', 'UTA Gestion de Ordenes de Pago'),
                        StringStruct('FileVersion', project_version),
                        StringStruct('InternalName', 'uta-gestion-ops'),
                        StringStruct('OriginalFilename', 'uta-gestion-ops.exe'),
                        StringStruct('ProductName', 'UTA Gestion de Ordenes de Pago'),
                        StringStruct('ProductVersion', project_version),
                    ],
                )
            ]
        ),
        VarFileInfo([VarStruct('Translation', [1033, 1200])]),
    ],
)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='uta-gestion-ops',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version=version_info,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='uta-gestion-ops',
)
