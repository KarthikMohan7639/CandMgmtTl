from typing import Any, Dict, List

import pandas as pd

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QComboBox, QWidget, QHeaderView
)


class MergeDialog(QDialog):
    """Dialog to review and choose merge decisions for a single duplicate group.

    Inputs:
    - records: List[Dict[str, Any]] (source records)

    UI:
    - Table: rows = source records, columns = union of record fields
    - For each field, a `QComboBox` to pick which source row to keep (strategy 'row_index')
    - Preview panel showing the merged result using `merge_service.merge_duplicate_group`

    Outputs:
    - `get_merge_decisions()` returns a mapping field -> {'strategy':'row_index','row_index':n}
    - On accept, the dialog computes and stores the merged record in `self.merged_record`
    """

    def __init__(self, records: List[Dict[str, Any]], parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle('Merge Group')
        self.resize(900, 500)

        self.records = records or []
        self.fields = self._collect_fields(self.records)

        self._controls: Dict[str, QComboBox] = {}
        self._merge_decisions: Dict[str, Dict[str, Any]] = {}
        self.merged_record: Dict[str, Any] = {}

        self._build_ui()
        self._refresh_preview()

    def _collect_fields(self, records: List[Dict[str, Any]]) -> List[str]:
        keys = []
        for r in records:
            for k in r.keys():
                if k not in keys:
                    keys.append(k)
        return keys

    def _build_ui(self) -> None:
        layout = QVBoxLayout()

        # Table showing source records
        self.table = QTableWidget()
        self.table.setRowCount(max(1, len(self.records)))
        self.table.setColumnCount(len(self.fields))
        self.table.setHorizontalHeaderLabels(self.fields)
        for c_idx, f in enumerate(self.fields):
            for r_idx, rec in enumerate(self.records):
                val = rec.get(f, '')
                item = QTableWidgetItem(str(val))
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.table.setItem(r_idx, c_idx, item)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(QLabel('Source records'))
        layout.addWidget(self.table)

        # Controls: for each field, a combo to choose source row
        controls_widget = QWidget()
        controls_layout = QHBoxLayout()
        controls_widget.setLayout(controls_layout)

        for f in self.fields:
            combo = QComboBox()
            # entries: 'Row 0', 'Row 1', ... with display of short value
            for i in range(len(self.records)):
                display = str(self.records[i].get(f, ''))
                if len(display) > 40:
                    display = display[:37] + '...'
                combo.addItem(f'Row {i}: {display}', i)
            # default to first non-empty row or 0
            sel_index = 0
            for i, rec in enumerate(self.records):
                if rec.get(f) not in (None, ''):
                    sel_index = i
                    break
            combo.setCurrentIndex(sel_index)
            combo.currentIndexChanged.connect(self._on_control_changed)
            self._controls[f] = combo
            # label + combo as compact widget
            container = QWidget()
            c_layout = QVBoxLayout()
            c_layout.setContentsMargins(2, 2, 2, 2)
            c_layout.addWidget(QLabel(f))
            c_layout.addWidget(combo)
            container.setLayout(c_layout)
            controls_layout.addWidget(container)

        layout.addWidget(QLabel('Choose source row per field'))
        layout.addWidget(controls_widget)

        # Preview area
        layout.addWidget(QLabel('Preview (merged result)'))
        self.preview_table = QTableWidget()
        self.preview_table.setRowCount(1)
        self.preview_table.setColumnCount(len(self.fields))
        self.preview_table.setHorizontalHeaderLabels(self.fields)
        self.preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.preview_table)

        # Buttons
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton('OK')
        self.ok_btn.clicked.connect(self._on_accept)
        self.cancel_btn = QPushButton('Cancel')
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def _on_control_changed(self, *_args) -> None:
        self._refresh_preview()

    def _build_decisions(self) -> Dict[str, Dict[str, Any]]:
        dec: Dict[str, Dict[str, Any]] = {}
        for f, combo in self._controls.items():
            row_index = combo.currentData()
            dec[f] = {'strategy': 'row_index', 'row_index': int(row_index)}
        self._merge_decisions = dec
        return dec

    def _refresh_preview(self) -> None:
        # build decisions and compute merged record via merge_service
        decisions = self._build_decisions()
        try:
            from app.services.merge_service import merge_duplicate_group
            merged = merge_duplicate_group(self.records, decisions)
        except Exception:
            # Fallback: compute merged using simple rules (take chosen row value)
            merged = {}
            for f, d in decisions.items():
                idx = d.get('row_index', 0)
                try:
                    merged[f] = self.records[idx].get(f)
                except Exception:
                    merged[f] = None

        self.merged_record = merged

        # populate preview table
        for c_idx, f in enumerate(self.fields):
            val = merged.get(f, '')
            item = QTableWidgetItem(str(val))
            item.setFlags(item.flags() ^ Qt.ItemIsEditable)
            self.preview_table.setItem(0, c_idx, item)

    def _on_accept(self) -> None:
        # ensure preview/decisions up-to-date
        self._refresh_preview()
        self.accept()

    def get_merge_decisions(self) -> Dict[str, Dict[str, Any]]:
        """Return the merge decisions chosen by the user."""
        return self._merge_decisions
class MergeDialog:
    pass