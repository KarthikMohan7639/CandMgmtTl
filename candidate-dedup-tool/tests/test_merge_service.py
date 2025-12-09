import pandas as pd
from app.services.merge_service import merge_duplicate_group, auto_merge_all_groups


def test_merge_most_recent():
    records = [
        {'id': '1', 'name': 'A', 'designation': 'Junior', 'contact_date': '2023-01-01'},
        {'id': '2', 'name': 'A', 'designation': 'Senior', 'contact_date': '2023-06-01'},
    ]
    decisions = {'designation': {'strategy': 'most_recent'}}
    merged = merge_duplicate_group(records, decisions)
    assert merged['designation'] == 'Senior'


def test_merge_concatenate_and_custom():
    records = [
        {'id': '1', 'notes': 'Worked on X'},
        {'id': '2', 'notes': 'Worked on Y'},
    ]
    decisions = {'notes': {'strategy': 'concatenate', 'sep': ' | '}, 'name': {'strategy': 'custom', 'value': 'Merged Name'}}
    merged = merge_duplicate_group(records, decisions)
    assert merged['notes'] == 'Worked on X | Worked on Y'
    assert merged['name'] == 'Merged Name'


def test_merge_row_index_and_first_non_empty():
    records = [
        {'id': '1', 'name': 'First', 'email': ''},
        {'id': '2', 'name': 'Second', 'email': 'second@example.com'},
    ]
    decisions = {'name': {'strategy': 'row_index', 'value': 1}, 'email': {'strategy': 'first_non_empty'}}
    merged = merge_duplicate_group(records, decisions)
    assert merged['name'] == 'Second'
    assert merged['email'] == 'second@example.com'


def test_auto_merge_all_groups():
    data = [
        {'id': '1', 'name': 'A', 'phone': '9876543210', 'email': 'a@example.com', 'contact_date': '2023-01-01'},
        {'id': '2', 'name': 'B', 'phone': '9876543210', 'email': 'b@example.com', 'contact_date': '2023-02-01'},
        {'id': '3', 'name': 'C', 'phone': '1111111111', 'email': 'c@example.com', 'contact_date': '2023-03-01'},
    ]
    df = pd.DataFrame(data)
    duplicate_groups = {'DUP-001': [0, 1]}
    merged_df, decisions = auto_merge_all_groups(duplicate_groups, df)
    # merged_df should have 2 rows now (one merged + the untouched record)
    assert len(merged_df) == 2
    # decisions should contain one group entry
    assert len(decisions) == 1