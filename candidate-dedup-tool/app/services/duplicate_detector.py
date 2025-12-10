from typing import Tuple, Dict, List, Callable, Any
import pandas as pd
import logging

LOGGER = logging.getLogger(__name__)


class _DSU:
    def __init__(self):
        self.parent = {}

    def find(self, x):
        if x not in self.parent:
            self.parent[x] = x
            return x
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, a, b):
        ra = self.find(a)
        rb = self.find(b)
        if ra == rb:
            return
        self.parent[rb] = ra


def detect_duplicates(
    df: pd.DataFrame,
    phone_col: str,
    email_col: str,
    normalizer_phone_func: Callable[[Any], str],
    normalizer_email_func: Callable[[Any], str]
) -> Tuple[pd.DataFrame, Dict[str, List[int]]]:
    """
    Detect duplicates by phone and/or email and return unique representatives and groups.
    Optimized for large datasets.
    """
    LOGGER.debug('Starting duplicate detection: phone_col=%s email_col=%s', phone_col, email_col)
    if df is None or df.empty:
        LOGGER.info('Empty dataframe provided to detect_duplicates')
        return pd.DataFrame(), {}

    df = df.copy()

    # Create normalized columns using vectorized operations for better performance
    LOGGER.debug('Normalizing phone and email columns...')
    df['normalized_phone'] = df[phone_col].fillna('').astype(str).apply(normalizer_phone_func)
    df['normalized_email'] = df[email_col].fillna('').astype(str).apply(normalizer_email_func)
    
    # Log sample data for debugging
    LOGGER.debug('Sample original data (first 2 rows):')
    for i, idx in enumerate(list(df.index)[:2]):
        LOGGER.debug('  Row %d: phone_orig="%s" email_orig="%s" phone_norm="%s" email_norm="%s"',
                    i, df.at[idx, phone_col], df.at[idx, email_col],
                    df.at[idx, 'normalized_phone'], df.at[idx, 'normalized_email'])

    # Build index list
    indices = list(df.index)

    dsu = _DSU()

    # Map normalized value to list of indices
    phone_map: Dict[str, List[int]] = {}
    email_map: Dict[str, List[int]] = {}

    for idx in indices:
        npn = df.at[idx, 'normalized_phone']
        nem = df.at[idx, 'normalized_email']
        # Only group if normalized value is non-empty and has actual content
        if npn and npn.strip():
            phone_map.setdefault(npn, []).append(idx)
        if nem and nem.strip():
            email_map.setdefault(nem, []).append(idx)

    LOGGER.debug('Phone groups: %d email groups: %d', len(phone_map), len(email_map))
    
    # Log sample groups for debugging
    if phone_map:
        sample_phone = list(phone_map.items())[0]
        LOGGER.debug('Sample phone group: normalized="%s" -> indices=%s', sample_phone[0], sample_phone[1])
    if email_map:
        sample_email = list(email_map.items())[0]
        LOGGER.debug('Sample email group: normalized="%s" -> indices=%s', sample_email[0], sample_email[1])

    # Union indices sharing same phone
    for group in phone_map.values():
        if len(group) < 2:
            continue
        for i in range(1, len(group)):
            dsu.union(group[0], group[i])

    # Union indices sharing same email
    for group in email_map.values():
        if len(group) < 2:
            continue
        for i in range(1, len(group)):
            dsu.union(group[0], group[i])

    # Prevent matching two completely empty records: ensure no unions where both phone and email empty
    # DSU unions above were only created for non-empty normalized values, so this is satisfied.

    # Build components
    comp: Dict[int, List[int]] = {}
    for idx in indices:
        root = dsu.find(idx)
        comp.setdefault(root, []).append(idx)

    # Create duplicate groups where size > 1
    duplicate_groups: Dict[str, List[int]] = {}
    group_id_seq = 1
    idx_to_group: Dict[int, str] = {}

    # Sort components by smallest index for determinism
    sorted_comps = sorted([members for members in comp.values() if len(members) > 1], key=lambda m: min(m))
    for members in sorted_comps:
        gid = f"DUP-{group_id_seq:03d}"
        duplicate_groups[gid] = sorted(members)
        for idx in members:
            idx_to_group[idx] = gid
        group_id_seq += 1

    LOGGER.info('Detected %d duplicate groups', len(duplicate_groups))

    # Assign duplicate_group column
    df['duplicate_group'] = df.index.map(lambda i: idx_to_group.get(i))

    # Build unique_df: representative for each group (first occurrence) + all non-duplicated rows
    representatives = []
    for gid, members in duplicate_groups.items():
        representatives.append(members[0])

    non_duplicate_indices = [i for i in indices if i not in idx_to_group]
    unique_indices = sorted(representatives + non_duplicate_indices)

    unique_df = df.loc[unique_indices].copy()
    unique_df.reset_index(drop=True, inplace=True)

    LOGGER.debug('Returning unique_df with %d rows', len(unique_df))
    return unique_df, duplicate_groups


def get_duplicate_group(group_id: str, duplicate_groups: Dict[str, List[int]], df: pd.DataFrame) -> List[Dict]:
    members = duplicate_groups.get(group_id, [])
    return [df.loc[idx].to_dict() for idx in members]
