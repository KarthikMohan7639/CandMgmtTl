import os
import tempfile

import pandas as pd
import pytest

pytest.importorskip('openpyxl')

from app.services import export_service


def test_export_unique_writes_file(tmp_path):
    df = pd.DataFrame({'name': ['Alice', 'Bob'], 'phone': ['123', '456']})
    out = tmp_path / 'unique.xlsx'
    # ensure file does not exist
    assert not out.exists()
    export_service.export_unique_records(df, str(out))
    assert out.exists()
    # read back
    read = pd.read_excel(str(out))
    assert list(read['name']) == ['Alice', 'Bob']


def test_export_unique_raises_if_exists(tmp_path):
    df = pd.DataFrame({'name': ['Alice']})
    out = tmp_path / 'exists.xlsx'
    out.write_text('placeholder')
    try:
        try:
            export_service.export_unique_records(df, str(out))
            raised = False
        except FileExistsError:
            raised = True
        assert raised
    finally:
        pass


def test_export_duplicate_writes_file(tmp_path):
    df = pd.DataFrame({
        'name': ['A', 'A_dup', 'B', 'B_dup'],
        'phone': ['111', '111', '222', '222']
    })
    dup_groups = {'DUP-001': [0, 1], 'DUP-002': [2, 3]}
    out = tmp_path / 'dups.xlsx'
    export_service.export_duplicate_records(dup_groups, df, str(out))
    assert out.exists()
    read = pd.read_excel(str(out))
    assert 'duplicate_group' in read.columns
    assert set(read['duplicate_group'].dropna().unique()) == set(['DUP-001', 'DUP-002'])


def test_export_duplicate_raises_if_exists(tmp_path):
    df = pd.DataFrame({'name': ['A']})
    dup_groups = {}
    out = tmp_path / 'dups_exists.xlsx'
    out.write_text('x')
    try:
        try:
            export_service.export_duplicate_records(dup_groups, df, str(out))
            raised = False
        except FileExistsError:
            raised = True
        assert raised
    finally:
        pass
