# Candidate Deduplication Tool

A Python desktop tool for detecting and merging duplicate candidate records across multiple Excel files. Designed for recruitment/HR staff to consolidate, clean, and export candidate data efficiently.

## Running the application

Run the GUI with:

```bash
python -m app
```

Options:

- `--debug`: enable console logging (useful for development).
- `--demo`: set a flag so the UI may auto-load a demo dataset if provided.

Example:

```bash
python -m app --debug
```

Dependencies (install in a virtualenv):

```bash
pip install -r requirements.txt
```

Note: The GUI requires `PyQt5` and export functionality requires `openpyxl`.

## Building a standalone executable

You can build a distributable executable using PyInstaller. A helper script and a `.spec` template are included.

Install PyInstaller:

```bash
pip install pyinstaller
```

Build (one-folder):

```bash
python build_exe.py
```

Build (single-file):

```bash
python build_exe.py --onefile
```

The script will include the `config/` directory in the bundle. If you need to include PyQt5 Qt plugins, ensure `PyQt5` is installed in the build environment; the script will attempt to discover the Qt `plugins/` folder automatically.

Alternatively you can run the provided spec directly:

```bash
pyinstaller candidate-dedup-tool.spec
```

Troubleshooting: If the built app fails to start due to missing Qt platform plugins, try adding the plugins directory explicitly via `--add-binary` or use the spec file and include plugin folders into `datas`/`binaries`.