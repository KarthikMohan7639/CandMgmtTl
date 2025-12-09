from typing import Dict, List, Optional

import pandas as pd

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import (
    QWidget, QListWidget, QHBoxLayout, QVBoxLayout, QLabel
)

from app.ui.widgets.data_table import DataTable


class DuplicateView(QWidget):
    """Widget to display duplicate groups and records in the selected group.

    Left: `QListWidget` showing group entries like "DUP-001 (3 records, phone: 9876543210)".
    Right: `DataTable` showing the records for the currently selected group.

    Public API:
    - set_groups(duplicate_groups: Dict[str, List[int]], df: pd.DataFrame) -> None
    - get_selected_group_id() -> Optional[str]

    Emits:
    - groupSelected(str) when a group is selected by the user.
    """

    groupSelected = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._groups: Dict[str, List[int]] = {}
        self._df: Optional[pd.DataFrame] = None

        self.group_list = QListWidget()
        self.group_list.setSelectionMode(self.group_list.SingleSelection)
        self.group_list.itemSelectionChanged.connect(self._on_group_selected)

        self.summary_label = QLabel('Select a group to view records')

        self.data_table = DataTable()

        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel('Duplicate Groups'))
        left_layout.addWidget(self.group_list)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.summary_label)
        right_layout.addWidget(self.data_table)

        main_layout = QHBoxLayout()
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        main_layout.addWidget(left_widget, 2)
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        main_layout.addWidget(right_widget, 5)

        self.setLayout(main_layout)

    def set_groups(self, duplicate_groups: Dict[str, List[int]], df: pd.DataFrame) -> None:
        """Set the groups mapping and the backing DataFrame.

        duplicate_groups: mapping from group id (e.g. 'DUP-001') to list of row indices (ints)
        df: the full DataFrame containing the records; indices are interpreted as integer positions
        """
        self._groups = duplicate_groups or {}
        self._df = df

        self.group_list.clear()

        for gid, indices in self._groups.items():
            summary = self._group_summary(indices)
            label = f"{gid} ({len(indices)} records{summary})"
            self.group_list.addItem(label)

        # clear table / summary
        self.summary_label.setText('Select a group to view records')
        self.data_table.clear()

    def get_selected_group_id(self) -> Optional[str]:
        sel = self.group_list.currentItem()
        if not sel:
            return None
        # item text format: "DUP-001 (3 records, phone: 9876543210)"
        text = sel.text()
        gid = text.split(' ')[0]
        return gid

    def _on_group_selected(self) -> None:
        gid = self.get_selected_group_id()
        if not gid:
            return
        # emit signal
        self.groupSelected.emit(gid)

        # display records
        indices = self._groups.get(gid, [])
        if self._df is None or not indices:
            self.summary_label.setText('No data for selected group')
            self.data_table.clear()
            return

        # Interpret indices as integer positions; use iloc to fetch rows
        try:
            rows = self._df.iloc[indices]
        except Exception:
            # fallback: try using loc on index values
            rows = self._df.loc[indices]

        # update summary with some matching key hints
        hint = self._group_hint(rows)
        self.summary_label.setText(f"Group: {gid} — {len(rows)} records{hint}")

        # populate the DataTable with these rows
        try:
            self.data_table.set_dataframe(rows.reset_index(drop=True))
        except Exception:
            # best-effort: convert to simple list of dicts and let DataTable handle it
            self.data_table.set_dataframe(pd.DataFrame(rows))

    def _group_summary(self, indices: List[int]) -> str:
        """Return a short summary string like ', phone: 9876543210' if available."""
        if self._df is None or not indices:
            return ''
        try:
            rows = self._df.iloc[indices]
        except Exception:
            rows = self._df.loc[indices]

        # prefer phone, then email, then first non-empty cell from first column
        cols = list(rows.columns)
        def first_non_empty(col):
            vals = rows[col].dropna().astype(str)
            return vals.iloc[0] if not vals.empty else None

        # search for phone-like column
        phone_col = None
        for c in cols:
            if 'phone' in c.lower():
                phone_col = c
                break
        if phone_col:
            val = first_non_empty(phone_col)
            if val:
                return f", phone: {val}"

        # search for email-like column
        email_col = None
        for c in cols:
            if 'email' in c.lower():
                email_col = c
                break
        if email_col:
            val = first_non_empty(email_col)
            if val:
                return f", email: {val}"

        # fallback to first column's first value
        if cols:
            val = first_non_empty(cols[0])
            if val:
                return f", {cols[0]}: {val}"

        return ''

    def _group_hint(self, rows: pd.DataFrame) -> str:
        """Return a hint string summarizing the matching key(s)."""
        summary = self._group_summary(list(range(len(rows))))
        return summary
class DuplicateView:
    pass