from typing import List
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QListWidget, QListWidgetItem, 
    QPushButton, QHBoxLayout, QLabel
)
from PyQt5.QtCore import Qt


class ColumnSelectionDialog(QDialog):
    """Dialog to select which columns to export."""
    
    def __init__(self, columns: List[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle('Select Columns to Export')
        self.resize(500, 400)
        self.columns = columns
        self.selected_columns = []
        self._build_ui()
    
    def _build_ui(self):
        layout = QVBoxLayout()
        
        info_label = QLabel('Select the columns you want to export:')
        layout.addWidget(info_label)
        
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.MultiSelection)
        
        for col in self.columns:
            item = QListWidgetItem(col)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)  # All selected by default
            self.list_widget.addItem(item)
        
        layout.addWidget(self.list_widget)
        
        # Buttons for select/deselect all
        select_btn_layout = QHBoxLayout()
        self.select_all_btn = QPushButton('Select All')
        self.select_all_btn.clicked.connect(self._select_all)
        select_btn_layout.addWidget(self.select_all_btn)
        
        self.deselect_all_btn = QPushButton('Deselect All')
        self.deselect_all_btn.clicked.connect(self._deselect_all)
        select_btn_layout.addWidget(self.deselect_all_btn)
        
        layout.addLayout(select_btn_layout)
        
        # OK/Cancel buttons
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton('OK')
        self.ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.ok_btn)
        
        self.cancel_btn = QPushButton('Cancel')
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def _select_all(self):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setCheckState(Qt.Checked)
    
    def _deselect_all(self):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setCheckState(Qt.Unchecked)
    
    def get_selected_columns(self) -> List[str]:
        """Return list of selected column names."""
        selected = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.checkState() == Qt.Checked:
                selected.append(item.text())
        return selected
