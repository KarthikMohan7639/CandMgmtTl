
import re
from typing import Optional

def normalize_phone(phone_str: Optional[str]) -> str:
    """
    Normalize a phone number for duplicate detection.
    """
    if not phone_str or not str(phone_str).strip():
        return ''
    phone = str(phone_str)
    phone = re.sub(r'[\s\-()./]', '', phone)
    phone = re.sub(r'^(\+91|0091|001)', '', phone)
    phone = phone.lstrip('0')
    # For India numbers: if longer than 10, keep last 10 digits
    if len(phone) > 10:
        phone = phone[-10:]
    # If digits only, return as-is (preserve shorter numbers)
    if phone.isdigit():
        return phone
    return ''

def normalize_email(email_str: Optional[str]) -> str:
    """
    Normalize email for duplicate detection.
    """
    if not email_str or not str(email_str).strip():
        return ''
    return str(email_str).strip().lower()

def normalize_text(text_str: Optional[str]) -> str:
    """
    General text normalization for other fields.
    """
    if not text_str or not str(text_str).strip():
        return ''
    return str(text_str).strip()