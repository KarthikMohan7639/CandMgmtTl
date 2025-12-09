import json
from typing import Dict
from pathlib import Path
import logging

LOGGER = logging.getLogger(__name__)

# Configurable path so tests can override if needed
CONFIG_PATH = Path(__file__).resolve().parents[2] / 'config' / 'header_mappings.json'


def load_mappings() -> Dict[str, Dict[str, str]]:
    """Load header mappings from JSON file.

    Returns a dict mapping source_file_pattern -> { column_name: field_type }
    If the file does not exist or is invalid, returns an empty dict.
    """
    try:
        if not CONFIG_PATH.exists():
            return {}
        with open(CONFIG_PATH, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
            if not isinstance(data, dict):
                LOGGER.warning('header_mappings.json does not contain a JSON object')
                return {}
            return data
    except json.JSONDecodeError:
        LOGGER.warning('Failed to parse header_mappings.json — returning empty mappings')
        return {}
    except Exception as ex:
        LOGGER.warning(f'Error loading header mappings: {ex}')
        return {}


def save_mappings(mappings: Dict[str, Dict[str, str]]) -> None:
    """Save mappings to the JSON config file.

    Raises an exception if saving fails.
    """
    try:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, 'w', encoding='utf-8') as fh:
            json.dump(mappings, fh, indent=2, ensure_ascii=False)
    except Exception as ex:
        raise RuntimeError(f'Failed to save header mappings: {ex}') from ex


def get_mapping_for_file(file_name: str, mappings: Dict[str, Dict[str, str]]) -> Dict[str, str]:
    """Return the mapping dict for a given file name using simple substring matching.

    If multiple patterns match, returns the first match (iteration order).
    Returns empty dict if no mapping found.
    """
    fname = file_name.lower()
    for pattern, mapping in mappings.items():
        try:
            if pattern.lower() in fname:
                return mapping
        except Exception:
            continue
    return {}
class MappingStorage:
    pass