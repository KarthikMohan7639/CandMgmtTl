#!/usr/bin/env python3
"""Helper script to run PyInstaller for the application.

Usage:
  python build_exe.py [--onefile] [--clean]

This script will run PyInstaller to build the app, including the `config/` folder as data.
It will try to detect PyQt5 plugins and include them if available.
"""
import argparse
import os
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--onefile', action='store_true', help='Build a single-file executable')
    parser.add_argument('--clean', action='store_true', help='Pass --clean to PyInstaller')
    parser.add_argument('--debug', action='store_true', help='Show the full PyInstaller command and exit')
    args = parser.parse_args()

    project_root = os.path.dirname(__file__)
    entry_script = os.path.join(project_root, 'app', 'main.py')
    name = 'candidate-dedup-tool'

    sep = ';' if os.name == 'nt' else ':'

    datas = []
    # include config folder
    config_src = os.path.join(project_root, 'config')
    if os.path.exists(config_src):
        datas.append(f"{config_src}{sep}config")

    cmd = ['pyinstaller', '--name', name]
    if args.onefile:
        cmd.append('--onefile')
    else:
        cmd.append('--onedir')
    cmd.extend(['--noconfirm'])
    if args.clean:
        cmd.append('--clean')

    # add datas
    for d in datas:
        cmd.extend(['--add-data', d])

    # attempt to include PyQt5 plugins
    try:
        import PyQt5
        pyqt_dir = os.path.dirname(PyQt5.__file__)
        plugins_dir = os.path.join(pyqt_dir, 'Qt', 'plugins')
        if os.path.exists(plugins_dir):
            # include entire plugins folder
            cmd.extend(['--add-binary', f"{plugins_dir}{sep}PyQt5/Qt/plugins"])
    except Exception:
        # not fatal; user can add plugins manually
        pass

    # entry
    cmd.append(entry_script)

    if args.debug:
        print('PyInstaller command:')
        print(' '.join(cmd))
        return

    print('Running PyInstaller...')
    try:
        subprocess.run(cmd, check=True)
        print('PyInstaller finished successfully')
    except subprocess.CalledProcessError as e:
        print('PyInstaller failed:', e)
        sys.exit(e.returncode)


if __name__ == '__main__':
    main()
