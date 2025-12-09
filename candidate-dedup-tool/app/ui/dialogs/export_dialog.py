from typing import Optional, Tuple

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QFileDialog
)


class ExportDialog(QDialog):
    """Minimal dialog to pick output paths for unique and duplicate Excel exports."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Export Paths')
        self.resize(600, 150)

        self.unique_path: Optional[str] = None
        self.duplicates_path: Optional[str] = None

        layout = QVBoxLayout()

        # Unique
        u_layout = QHBoxLayout()
        self.u_label = QLabel('Unique: (not set)')
        u_layout.addWidget(self.u_label)
        u_btn = QPushButton('Choose Unique Path')
        u_btn.clicked.connect(self._choose_unique)
        u_layout.addWidget(u_btn)
        layout.addLayout(u_layout)

        # Duplicates
        d_layout = QHBoxLayout()
        self.d_label = QLabel('Duplicates: (not set)')
        d_layout.addWidget(self.d_label)
        d_btn = QPushButton('Choose Duplicates Path')
        d_btn.clicked.connect(self._choose_duplicates)
        d_layout.addWidget(d_btn)
        layout.addLayout(d_layout)

        # OK / Cancel
        btn_layout = QHBoxLayout()
        ok = QPushButton('OK')
        ok.clicked.connect(self.accept)
        cancel = QPushButton('Cancel')
        cancel.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(ok)
        btn_layout.addWidget(cancel)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def _choose_unique(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, 'Save unique records', '', 'Excel Files (*.xlsx)')
        if path:
            self.unique_path = path
            self.u_label.setText(f'Unique: {path}')

    def _choose_duplicates(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, 'Save duplicates', '', 'Excel Files (*.xlsx)')
        if path:
            self.duplicates_path = path
            self.d_label.setText(f'Duplicates: {path}')

    def get_paths(self) -> Tuple[Optional[str], Optional[str]]:
        return self.unique_path, self.duplicates_path
