from typing import List, Dict, Any, Tuple
import pandas as pd
from datetime import datetime, timezone
import logging

LOGGER = logging.getLogger(__name__)


def _parse_date(d: Any):
    try:
        return pd.to_datetime(d, errors='coerce')
    except Exception:
        return pd.NaT


def merge_duplicate_group(records: List[Dict], merge_decisions: Dict[str, Dict]) -> Dict:
    """
    Merge a group of duplicate records into one consolidated record.
    """
    LOGGER.debug('Merging %d records with decisions for %d fields', len(records), len(merge_decisions))
    if not records:
        LOGGER.warning('merge_duplicate_group called with empty records')
        return {}

    # Build set of all fields (include any fields mentioned in merge_decisions)
    all_fields = set()
    for r in records:
        all_fields.update(r.keys())
    # include decision keys so custom strategies can add fields not present in records
    all_fields.update(merge_decisions.keys())

    merged: Dict[str, Any] = {}
    conflicts: Dict[str, List[Any]] = {}

    for field in all_fields:
        decision = merge_decisions.get(field, {'strategy': 'first_non_empty'})
        strategy = decision.get('strategy')

        values = [r.get(field) for r in records]
        non_empty = [v for v in values if v is not None and (not (isinstance(v, str) and v.strip() == ''))]

        if strategy == 'row_index':
            idx = decision.get('value', 0)
            try:
                merged[field] = records[idx].get(field)
            except Exception:
                merged[field] = non_empty[0] if non_empty else None

        elif strategy == 'keep_same':
            if not non_empty:
                merged[field] = None
            else:
                # if values differ, record conflict but pick first non-empty
                uniq = list({str(v).strip() for v in non_empty})
                if len(uniq) > 1:
                    conflicts[field] = uniq
                merged[field] = non_empty[0]

        elif strategy == 'most_recent':
            # identify record with latest contact_date (falls back to first non-empty)
            dates = [_parse_date(r.get('contact_date')) for r in records]
            best_idx = None
            best_date = pd.NaT
            for i, dt in enumerate(dates):
                if pd.isna(dt):
                    continue
                if pd.isna(best_date) or dt > best_date:
                    best_date = dt
                    best_idx = i
            if best_idx is not None:
                merged[field] = records[best_idx].get(field)
            else:
                merged[field] = non_empty[0] if non_empty else None

        elif strategy == 'first_non_empty':
            merged[field] = non_empty[0] if non_empty else None

        elif strategy == 'concatenate':
            sep = decision.get('sep', '; ')
            unique_vals = []
            for v in non_empty:
                sv = str(v).strip()
                if sv and sv not in unique_vals:
                    unique_vals.append(sv)
            merged[field] = sep.join(unique_vals) if unique_vals else None

        elif strategy == 'custom':
            merged[field] = decision.get('value')

        else:
            # default
            merged[field] = non_empty[0] if non_empty else None

    # Metadata
    merged['merge_id'] = f"MERGE-{int(datetime.now(timezone.utc).timestamp())}"
    merged['source_records'] = [r.get('id') or r.get('_index') or None for r in records]
    if conflicts:
        merged['merge_conflicts'] = conflicts
    if conflicts:
        LOGGER.info('Conflicts detected for fields: %s', list(conflicts.keys()))
    LOGGER.debug('Merged result merge_id=%s', merged.get('merge_id'))
    return merged


def auto_merge_all_groups(duplicate_groups: Dict[str, List[int]], df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict]]:
    """
    Auto-merge all duplicate groups using default strategies.

    Default strategies:
    - For date fields: use most recent
    - For phone/email: keep value (should be same)
    - For name: use first row
    - For other fields: use first non-empty value
    """
    LOGGER.info('Auto-merging %d groups', len(duplicate_groups) if duplicate_groups else 0)
    if not duplicate_groups:
        LOGGER.info('No duplicate groups provided to auto_merge_all_groups')
        return df.copy(), []

    df_copy = df.copy()
    merged_rows = []
    decisions_log = []

    # Gather default strategies based on columns present
    columns = list(df_copy.columns)

    for gid, indices in duplicate_groups.items():
        records = [df_copy.loc[i].to_dict() for i in indices]

        # default decisions
        merge_decisions: Dict[str, Dict] = {}
        for col in columns:
            if col.lower().find('date') != -1 or col == 'contact_date':
                merge_decisions[col] = {'strategy': 'most_recent'}
            elif col.lower() in ('phone', 'normalized_phone') or 'phone' in col.lower():
                merge_decisions[col] = {'strategy': 'keep_same'}
            elif col.lower() in ('email', 'normalized_email') or 'email' in col.lower():
                merge_decisions[col] = {'strategy': 'keep_same'}
            elif col.lower() in ('name', 'candidate name', 'full name'):
                merge_decisions[col] = {'strategy': 'row_index', 'value': 0}
            else:
                merge_decisions[col] = {'strategy': 'first_non_empty'}

        merged = merge_duplicate_group(records, merge_decisions)
        # Attach group metadata
        merged['duplicate_group'] = gid
        merged_rows.append((indices, merged, merge_decisions))
        decisions_log.append({'group_id': gid, 'decisions': merge_decisions})
        LOGGER.debug('Auto-merged group %s -> merged fields %d', gid, len(merged.keys()))

    # Remove all original rows that were part of groups
    all_indices = [i for members in duplicate_groups.values() for i in members]
    df_result = df_copy.drop(index=all_indices, errors='ignore')

    # Append merged rows
    merged_df = pd.DataFrame([m for _, m, _ in merged_rows])
    if not merged_df.empty:
        # ensure columns align
        df_result = pd.concat([df_result, merged_df], ignore_index=True, sort=False)

    df_result.reset_index(drop=True, inplace=True)
    LOGGER.info('Auto-merge completed, result rows=%d', len(df_result))
    return df_result, decisions_log
