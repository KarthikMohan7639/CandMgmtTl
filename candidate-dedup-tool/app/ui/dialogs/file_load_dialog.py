from typing import List, Optional
import os
import zipfile

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QListWidget, QHBoxLayout, QFileDialog, QLabel, QMessageBox
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
        self.choose_files_btn = QPushButton('Choose Files')
        self.choose_files_btn.clicked.connect(self._choose_files)
        btn_layout.addWidget(self.choose_files_btn)

        self.choose_folder_btn = QPushButton('Choose Folder')
        self.choose_folder_btn.clicked.connect(self._choose_folder)
        btn_layout.addWidget(self.choose_folder_btn)

        self.choose_zip_btn = QPushButton('Choose Zip')
        self.choose_zip_btn.clicked.connect(self._choose_zip)
        btn_layout.addWidget(self.choose_zip_btn)

        self.clear_btn = QPushButton('Clear')
        self.clear_btn.clicked.connect(self._clear_files)
        btn_layout.addWidget(self.clear_btn)

        layout.addLayout(btn_layout)

        btn_layout2 = QHBoxLayout()
        self.ok_btn = QPushButton('OK')
        self.ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton('Cancel')
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout2.addWidget(self.cancel_btn)

        layout.addLayout(btn_layout2)
        self.setLayout(layout)

    def _choose_files(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(self, 'Select Excel files', '', 'Excel Files (*.xlsx *.xls)')
        if not paths:
            return
        self._files.extend(paths)
        self._update_list()

    def _choose_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, 'Select Folder with Excel Files')
        if not folder:
            return
        excel_files = self._find_excel_files(folder)
        if not excel_files:
            QMessageBox.information(self, 'No Files', f'No Excel files found in {folder}')
            return
        self._files.extend(excel_files)
        self._update_list()

    def _choose_zip(self) -> None:
        zip_path, _ = QFileDialog.getOpenFileName(self, 'Select Zip File', '', 'Zip Files (*.zip)')
        if not zip_path:
            return
        try:
            excel_files = self._extract_excel_from_zip(zip_path)
            if not excel_files:
                QMessageBox.information(self, 'No Files', f'No Excel files found in {zip_path}')
                return
            self._files.extend(excel_files)
            self._update_list()
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to extract zip: {e}')

    def _clear_files(self) -> None:
        self._files.clear()
        self._update_list()

    def _update_list(self) -> None:
        # Remove duplicates
        self._files = list(dict.fromkeys(self._files))
        self.list_widget.clear()
        self.list_widget.addItems(self._files)
        self.info_label.setText(f'{len(self._files)} file(s) selected')

    def _find_excel_files(self, folder: str) -> List[str]:
        excel_files = []
        for root, _, files in os.walk(folder):
            for f in files:
                if f.lower().endswith(('.xlsx', '.xls')):
                    excel_files.append(os.path.join(root, f))
        return excel_files

    def _extract_excel_from_zip(self, zip_path: str) -> List[str]:
        import tempfile
        excel_files = []
        temp_dir = tempfile.mkdtemp(prefix='excel_zip_')
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for file_info in zip_ref.filelist:
                if file_info.filename.lower().endswith(('.xlsx', '.xls')):
                    extracted_path = zip_ref.extract(file_info, temp_dir)
                    excel_files.append(extracted_path)
        
        return excel_files

    def get_selected_files(self) -> List[str]:
        return list(self._files)