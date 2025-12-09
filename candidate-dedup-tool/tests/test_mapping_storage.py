import json
import tempfile
from pathlib import Path

from app.services import mapping_storage


def test_save_and_load_mappings(tmp_path):
    # Override CONFIG_PATH to a temp file
    temp_file = tmp_path / 'header_mappings.json'
    mapping_storage.CONFIG_PATH = temp_file

    mappings = {
        'piping': {'Candidate Name': 'NAME', 'Contact No': 'PHONE'},
        'quality': {'Full Name': 'NAME', 'Mobile': 'PHONE'}
    }

    mapping_storage.save_mappings(mappings)
    loaded = mapping_storage.load_mappings()
    assert isinstance(loaded, dict)
    assert loaded.get('piping', {}).get('Candidate Name') == 'NAME'


def test_get_mapping_for_file(tmp_path):
    mappings = {
        'piping': {'Candidate Name': 'NAME'},
        'electrical': {'First Name': 'NAME'}
    }
    # matching should be case-insensitive substring
    res = mapping_storage.get_mapping_for_file('2023_PIPING_candidates.xlsx', mappings)
    assert res.get('Candidate Name') == 'NAME'

    res2 = mapping_storage.get_mapping_for_file('electrical-list.xls', mappings)
    assert res2.get('First Name') == 'NAME'

    # no match returns empty dict
    res3 = mapping_storage.get_mapping_for_file('other.xlsx', mappings)
    assert res3 == {}
