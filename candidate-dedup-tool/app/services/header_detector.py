from typing import List, Dict, Any, Tuple
import difflib
import logging
import pandas as pd
import re

LOGGER = logging.getLogger(__name__)

HEADER_KEYWORDS = {
    'NAME': [
        'name', 'candidate name', 'applicant name', 'full name',
        'first name', 'person name'
    ],
    'PHONE': [
        'phone', 'phone number', 'phone no', 'contact', 'contact no',
        'contact number', 'mobile', 'mobile no', 'mobile number',
        'telephone', 'tel', 'contact mobile'
    ],
    'EMAIL': [
        'email', 'email address', 'email id', 'e-mail', 'e-mail address',
        'mailbox', 'electronic mail'
    ],
    'DESIGNATION': [
        'designation', 'role', 'position', 'job title', 'current role',
        'role applied', 'current designation', 'applied position'
    ],
    'DEPARTMENT': [
        'department', 'domain', 'function', 'dept', 'division',
        'functional area', 'business unit'
    ],
    'DATE': [
        'date', 'contact date', 'contacted date', 'contacted on',
        'application date', 'applied date', 'last contacted',
        'last contact date', 'updated date', 'dob', 'date of birth',
        'birth date', 'cv shared', 'shared date', 'cv date'
    ]
}


def _seq_ratio(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, a, b).ratio()


def _fuzzy_ratio(a: str, b: str) -> float:
    try:
        # fuzzywuzzy returns 0-100, convert to 0-1
        from fuzzywuzzy import fuzz
        return fuzz.token_set_ratio(a, b) / 100.0
    except Exception:
        return _seq_ratio(a, b)


def detect_by_content(df: pd.DataFrame, column: str) -> str:
    """Detect column type by analyzing content."""
    if df is None or df.empty or column not in df.columns:
        return 'OTHER'
    
    # Sample up to 100 rows
    sample = df[column].dropna().astype(str).head(100)
    if sample.empty:
        return 'OTHER'
    
    phone_count = 0
    email_count = 0
    date_count = 0
    
    for val in sample:
        val_str = str(val).strip()
        
        # Check for email: contains @ and .com/.net/.org etc
        if '@' in val_str and '.' in val_str.split('@')[-1]:
            email_count += 1
            continue  # Skip further checks if email found
        
        # Check for date patterns (YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY, etc)
        date_patterns = [
            r'\d{4}[-/]\d{1,2}[-/]\d{1,2}',  # YYYY-MM-DD or YYYY/MM/DD
            r'\d{1,2}[-/]\d{1,2}[-/]\d{4}',  # DD-MM-YYYY or DD/MM/YYYY
            r'\d{1,2}[-/]\d{1,2}[-/]\d{2}',   # DD-MM-YY or DD/MM/YY
        ]
        is_date = any(re.match(pattern, val_str) for pattern in date_patterns)
        if is_date:
            date_count += 1
            continue  # Skip phone check if it's a date
        
        # Check for phone: has 7-15 digits and mostly digits (not dates)
        digits = re.findall(r'\d', val_str)
        digit_count = len(digits)
        # Phone should have 7-15 digits and digits should be >60% of content length
        # Also ensure it's not just numbers (like IDs or years)
        if 7 <= digit_count <= 15 and digit_count / max(len(val_str), 1) > 0.6:
            # Additional check: avoid pure numbers without formatting
            has_formatting = any(char in val_str for char in ['-', '(', ')', ' ', '+'])
            if has_formatting or digit_count >= 10:  # 10+ digits likely a phone
                phone_count += 1
    
    # Determine type based on majority
    total = len(sample)
    if email_count > total * 0.5:  # More than 50% are emails
        return 'EMAIL'
    elif phone_count > total * 0.5:  # More than 50% are phones
        return 'PHONE'
    elif date_count > total * 0.5:  # More than 50% are dates
        return 'DATE'
    
    return 'OTHER'


def detect_headers(column_names: List[str], threshold: float = 0.75, use_fuzzy: bool = False, df: pd.DataFrame = None) -> Dict[str, Dict[str, Any]]:
    """Auto-detect header types for given column names.

    Returns mapping: original_column -> {'field': field_type, 'score': score}
    field_type is one of HEADER_KEYWORDS keys or 'OTHER'.
    score is a float between 0 and 1.
    """
    LOGGER.debug('Detecting headers for columns: %s (threshold=%s, use_fuzzy=%s)', column_names, threshold, use_fuzzy)
    results: Dict[str, Dict[str, Any]] = {}
    
    for col in column_names:
        col_norm = col.strip().lower()
        best_field = 'OTHER'
        best_score = 0.0
        
        # First, try content-based detection if DataFrame is provided
        if df is not None:
            content_type = detect_by_content(df, col)
            if content_type in ['PHONE', 'EMAIL']:
                results[col] = {'field': content_type, 'score': 1.0}
                LOGGER.debug('Column=%s detected by content=%s', col, content_type)
                continue
        
        # Fallback to name-based detection
        for field_type, keywords in HEADER_KEYWORDS.items():
            # find best match among keywords for this field type
            for kw in keywords:
                kw_norm = kw.lower()
                if use_fuzzy:
                    score = _fuzzy_ratio(col_norm, kw_norm)
                else:
                    score = _seq_ratio(col_norm, kw_norm)
                if score > best_score:
                    best_score = score
                    best_field = field_type
        
        if best_score < threshold:
            results[col] = {'field': 'OTHER', 'score': best_score}
        else:
            results[col] = {'field': best_field, 'score': best_score}
        LOGGER.debug('Column=%s detected=%s (score=%.3f)', col, results[col]['field'], results[col]['score'])
    
    LOGGER.info('Header detection complete for %d columns', len(column_names))
    return results


def detect_headers_simple_map(column_names: List[str], threshold: float = 0.75, use_fuzzy: bool = False) -> Dict[str, str]:
    """Convenience wrapper to return column -> field_type only."""
    r = detect_headers(column_names, threshold=threshold, use_fuzzy=use_fuzzy)
    return {k: v['field'] for k, v in r.items()}
