import os
from typing import List
import pandas as pd
import warnings
import logging

LOGGER = logging.getLogger(__name__)


def load_excel_file(filepath: str, sheet_name: int = 0) -> pd.DataFrame:
    """
    Load a single Excel file and return as DataFrame.
    """
    LOGGER.debug('Loading Excel file: %s', filepath)
    if not os.path.exists(filepath):
        LOGGER.error('File not found: %s', filepath)
        raise FileNotFoundError(f"File not found: {filepath}")
    try:
        # prefer openpyxl for .xlsx
        df = pd.read_excel(filepath, sheet_name=sheet_name, engine='openpyxl')
    except ValueError:
        # invalid file/format
        LOGGER.exception('ValueError when reading Excel file: %s', filepath)
        raise
    except Exception:
        LOGGER.warning('openpyxl read failed for %s, trying default engine', filepath)
        # try with pandas default engine fallback
        df = pd.read_excel(filepath, sheet_name=sheet_name)

    if df is None or df.empty:
        LOGGER.warning('Loaded file is empty: %s', filepath)
        warnings.warn(f"Loaded file is empty: {filepath}")
        return pd.DataFrame()

    return df


def load_multiple_excel_files(filepaths: List[str]) -> pd.DataFrame:
    """
    Load multiple Excel files and combine into single DataFrame.
    """
    LOGGER.info('Loading multiple Excel files: %s', filepaths)
    frames = []
    for fp in filepaths:
        try:
            df = load_excel_file(fp)
        except FileNotFoundError:
            LOGGER.warning('File not found, skipping: %s', fp)
            warnings.warn(f"File not found, skipping: {fp}")
            continue
        except Exception as ex:
            LOGGER.exception('Error loading %s: %s', fp, ex)
            warnings.warn(f"Error loading {fp}: {ex}")
            continue

        if df is None:
            continue
        df = df.copy()
        df['source_file'] = fp
        frames.append(df)

    if not frames:
        LOGGER.info('No frames loaded from provided files')
        return pd.DataFrame()

    combined = pd.concat(frames, ignore_index=True, sort=False)
    combined.reset_index(drop=True, inplace=True)
    LOGGER.info('Combined DataFrame rows: %d', len(combined))
    return combined


def load_folder_recursive(folder_path: str) -> List[str]:
    """
    Find all Excel files (.xlsx, .xls) in folder recursively.
    """
    LOGGER = logging.getLogger(__name__)
    matches = []
    for root, _, files in os.walk(folder_path):
        for f in files:
            if f.lower().endswith(('.xlsx', '.xls')):
                matches.append(os.path.join(root, f))
    LOGGER.debug('Found %d Excel files under %s', len(matches), folder_path)
    return matches
