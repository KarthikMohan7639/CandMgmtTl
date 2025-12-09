
from app.services.normalizer import normalize_phone, normalize_email, normalize_text


def test_normalize_phone():
    assert normalize_phone('+91-9876543210') == '9876543210'
    assert normalize_phone('09876543210') == '9876543210'
    assert normalize_phone('(987) 654-3210') == '9876543210'
    assert normalize_phone('9876543210') == '9876543210'
    # preserve short numeric strings
    assert normalize_phone('98765') == '98765'
    assert normalize_phone('') == ''
    assert normalize_phone(None) == ''
    assert normalize_phone('  ') == ''
    assert normalize_phone('abcdefgh') == ''


def test_normalize_email():
    assert normalize_email('John@GMAIL.COM') == 'john@gmail.com'
    assert normalize_email('test@example.com') == 'test@example.com'
    assert normalize_email('  Test@Email.Com  ') == 'test@email.com'
    assert normalize_email('') == ''
    assert normalize_email(None) == ''


def test_normalize_text():
    assert normalize_text('  Hello World  ') == 'Hello World'
    assert normalize_text('') == ''
    assert normalize_text(None) == ''
    assert normalize_text('    ') == ''