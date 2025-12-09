# Running the Candidate Deduplication Tool GUI

## Prerequisites

- Python 3.10 or higher
- For GUI: PyQt5 (will be installed automatically)
- For Excel support: openpyxl (will be installed automatically)

## Quick Start

### On Linux/Mac:

```bash
cd candidate-dedup-tool
./start_gui.sh
```

### On Windows:

```cmd
cd candidate-dedup-tool
start_gui.bat
```

### Manual Start:

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Run the application
python -m app --debug
```

## GUI Features

The application provides a graphical interface with the following features:

### 1. **Load Files**
- Click "Load Files" button or use File → Load Files menu
- Select one or more Excel files (.xlsx, .xls)
- Files will be merged automatically

### 2. **Map Headers**
- Click "Map Headers" to define which columns contain:
  - Phone numbers
  - Email addresses
  - Other important fields
- Auto-detection suggests mappings based on column names
- Previous mappings are saved and reused

### 3. **Find Duplicates**
- Click "Find Duplicates" to analyze loaded data
- The tool will identify duplicate records based on:
  - Phone number matching (fuzzy matching)
  - Email address matching (fuzzy matching)
- Results appear in the "Duplicates" tab

### 4. **Review Duplicates**
- Switch to "Duplicates" tab to see groups of duplicate records
- Each group shows all records identified as duplicates

### 5. **Auto Merge**
- Click "Merge" to automatically merge duplicate groups
- The tool creates a single "best" record from each duplicate group
- Merged results appear in "Merge Review" tab

### 6. **Export**
- **Export Unique**: Save the deduplicated records
- **Export Duplicates**: Save only the duplicate records for review

## Tabs Overview

### Loaded Data Tab
- Shows all loaded records
- Displays a `duplicate_group` column after finding duplicates
- Records with the same group ID are duplicates

### Duplicates Tab
- Lists all duplicate groups
- Click on a group to see all member records
- Useful for manual review before merging

### Merge Review Tab
- Shows the final merged/unique records
- One record per duplicate group (the "best" record)
- Ready for export

## Troubleshooting

### GUI doesn't start

**Check Python version:**
```bash
python --version  # Should be 3.10 or higher
```

**Install PyQt5 manually:**
```bash
pip install PyQt5>=5.15.0
```

### Import errors

**Install all dependencies:**
```bash
pip install -r requirements.txt
```

### Can't open Excel files

**Install openpyxl:**
```bash
pip install openpyxl>=3.0.10
```

### Linux: Qt platform plugin error

If you see "Could not load Qt platform plugin", install:
```bash
sudo apt-get install -y libgl1 libxcb-xinerama0 libxkbcommon-x11-0
```

## Running in Headless Environments

For servers or containers without display:

```bash
export QT_QPA_PLATFORM=offscreen
xvfb-run -s "-screen 0 1280x720x24" python -m app --debug
```

Note: This allows the app to run but you won't be able to interact with it visually.

## Command Line Mode

If you prefer command-line operation without GUI:

```bash
# Run backend tests
pytest candidate-dedup-tool/tests/

# Or use the service modules directly from Python
python -c "
from app.services import detect_duplicates
import pandas as pd
# ... your code here
"
```

## Getting Help

- Check logs in the console when running with `--debug` flag
- Logs show detailed information about:
  - File loading
  - Header detection
  - Duplicate detection progress
  - Export operations

## System Requirements

- **RAM**: 2GB minimum, 4GB recommended for large files
- **Disk**: 100MB for application + space for data files
- **Display**: 1024x768 or higher resolution
