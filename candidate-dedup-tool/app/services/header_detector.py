from typing import List, Dict, Any, Tuple
import difflib
import logging

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
        'last contact date', 'updated date'
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


def detect_headers(column_names: List[str], threshold: float = 0.75, use_fuzzy: bool = False) -> Dict[str, Dict[str, Any]]:
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
