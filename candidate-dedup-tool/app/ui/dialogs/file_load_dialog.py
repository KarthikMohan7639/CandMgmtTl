from typing import List, Optional

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QListWidget, QHBoxLayout, QFileDialog, QLabel
)


class FileLoadDialog(QDialog):
    """Dialog to select multiple Excel files and confirm selection.

    Use `get_selected_files()` after `exec_()` returns accepted to retrieve the list.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Load Excel Files')
        self.resize(600, 400)

        self._files: List[str] = []

        layout = QVBoxLayout()

        self.info_label = QLabel('No files selected')
        layout.addWidget(self.info_label)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        self.choose_btn = QPushButton('Choose Files')
        self.choose_btn.clicked.connect(self._choose_files)
        btn_layout.addWidget(self.choose_btn)

        self.ok_btn = QPushButton('OK')
        self.ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton('Cancel')
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def _choose_files(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(self, 'Select Excel files', '', 'Excel Files (*.xlsx *.xls)')
        if not paths:
            return
        self._files = paths
        self.list_widget.clear()
        self.list_widget.addItems(self._files)
        self.info_label.setText(f'{len(self._files)} file(s) selected')

    def get_selected_files(self) -> List[str]:
        return list(self._files)
class FileLoadDialog:
    pass