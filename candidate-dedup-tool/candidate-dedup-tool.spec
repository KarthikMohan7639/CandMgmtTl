# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller .spec template for candidate-dedup-tool.

This spec collects the `config/` directory and attempts to include Qt plugins.
You can customize and run: `pyinstaller candidate-dedup-tool.spec`
"""
import os
from PyInstaller.utils.hooks import collect_submodules, collect_data_files
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

project_root = os.path.abspath(os.path.dirname(__file__))
datas = []
config_dir = os.path.join(project_root, 'config')
if os.path.exists(config_dir):
    datas.append((config_dir, 'config'))

# Collect PyQt5 submodules if present
hiddenimports = []
try:
    hiddenimports = collect_submodules('PyQt5')
except Exception:
    hiddenimports = []

a = Analysis(
    ['app/main.py'],
    pathex=[project_root],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(pyz, a.scripts, [], name='candidate-dedup-tool', debug=False, bootloader_ignore_signals=False, strip=False, upx=True, console=False)

coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, strip=False, upx=True, name='candidate-dedup-tool')
