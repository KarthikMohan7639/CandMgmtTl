import pandas as pd
from app.services.duplicate_detector import detect_duplicates
from app.services.normalizer import normalize_phone, normalize_email


def test_same_phone():
    data = [
        {'id': 'A', 'phone': '9876543210', 'email': 'a@test.com'},
        {'id': 'B', 'phone': '9876543210', 'email': 'b@test.com'},
    ]
    df = pd.DataFrame(data)
    _, groups = detect_duplicates(df, 'phone', 'email', normalize_phone, normalize_email)
    assert len(groups) == 1
    assert any(len(m) == 2 for m in groups.values())


def test_same_email():
    data = [
        {'id': 'A', 'phone': '9876543210', 'email': 'test@mail.com'},
        {'id': 'B', 'phone': '9876554321', 'email': 'test@mail.com'},
    ]
    df = pd.DataFrame(data)
    _, groups = detect_duplicates(df, 'phone', 'email', normalize_phone, normalize_email)
    assert len(groups) == 1
    assert any(len(m) == 2 for m in groups.values())


def test_transitive_grouping():
    # A-B same phone, B-C same email -> all grouped
    data = [
        {'id': 'A', 'phone': '1111', 'email': 'a@test.com'},
        {'id': 'B', 'phone': '1111', 'email': 'b@test.com'},
        {'id': 'C', 'phone': '3333', 'email': 'b@test.com'},
    ]
    df = pd.DataFrame(data)
    _, groups = detect_duplicates(df, 'phone', 'email', normalize_phone, normalize_email)
    # one group of size 3
    assert any(len(m) == 3 for m in groups.values())


def test_empty_fields_do_not_match():
    data = [
        {'id': 'A', 'phone': '', 'email': ''},
        {'id': 'B', 'phone': '9999', 'email': 'b@test.com'},
    ]
    df = pd.DataFrame(data)
    _, groups = detect_duplicates(df, 'phone', 'email', normalize_phone, normalize_email)
    # no groups should include the empty record
    all_grouped_indices = [i for members in groups.values() for i in members]
    assert 0 not in all_grouped_indices


def test_multiple_unique_records():
    data = [
        {'id': '1', 'phone': '1000', 'email': 'a@x.com'},
        {'id': '2', 'phone': '2000', 'email': 'b@x.com'},
        {'id': '3', 'phone': '3000', 'email': 'c@x.com'},
        {'id': '4', 'phone': '4000', 'email': 'd@x.com'},
        {'id': '5', 'phone': '5000', 'email': 'e@x.com'},
    ]
    df = pd.DataFrame(data)
    _, groups = detect_duplicates(df, 'phone', 'email', normalize_phone, normalize_email)
    assert len(groups) == 0