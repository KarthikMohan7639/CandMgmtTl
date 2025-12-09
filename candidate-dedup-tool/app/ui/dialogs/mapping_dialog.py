from typing import List, Dict, Any
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QComboBox,
    QCheckBox, QPushButton, QHBoxLayout, QLabel, QWidget
)


FIELD_TYPES = ['NAME', 'PHONE', 'EMAIL', 'DESIGNATION', 'DEPARTMENT', 'DATE', 'OTHER']


class MappingDialog(QDialog):
    def __init__(self, columns: List[str], detected: Dict[str, Dict[str, Any]], sample_rows: List[Dict[str, Any]], parent=None):
        super().__init__(parent)
        self.setWindowTitle('Header Mapping')
        self.columns = columns
        self.detected = detected
        self.sample_rows = sample_rows
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setRowCount(len(self.columns))
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['Column', 'Detected', 'Ignore', 'Preview'])

        for r, col in enumerate(self.columns):
            self.table.setItem(r, 0, QTableWidgetItem(col))

            detected_field = self.detected.get(col, {}).get('field', 'OTHER')
            combo = QComboBox()
            combo.addItems(FIELD_TYPES)
            if detected_field in FIELD_TYPES:
                combo.setCurrentText(detected_field)
            self.table.setCellWidget(r, 1, combo)

            chk = QCheckBox()
            self.table.setCellWidget(r, 2, chk)

            # preview
            preview_vals = []
            for row in self.sample_rows:
                preview_vals.append(str(row.get(col, '')))
            self.table.setItem(r, 3, QTableWidgetItem(' | '.join(preview_vals)))

        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton('OK')
        cancel_btn = QPushButton('Cancel')
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def get_mapping(self) -> Dict[str, Dict[str, Any]]:
        mapping: Dict[str, Dict[str, Any]] = {}
        for r, col in enumerate(self.columns):
            combo: QComboBox = self.table.cellWidget(r, 1)
            chk: QCheckBox = self.table.cellWidget(r, 2)
            mapping[col] = {'field': combo.currentText(), 'ignore': chk.isChecked()}
        return mapping

    def get_final_mapping(self) -> Dict[str, str]:
        """Return a simplified mapping of column -> field type for consumption by services.

        Columns marked as ignored will not appear in the returned mapping.
        """
        final: Dict[str, str] = {}
        for col, info in self.get_mapping().items():
            if info.get('ignore'):
                continue
            final[col] = info.get('field', 'OTHER')
        return final