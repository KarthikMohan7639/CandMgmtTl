from typing import List, Dict
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QGroupBox, QCheckBox, QScrollArea, QWidget
)


class SearchDialog(QDialog):
    """Dialog for multi-keyword search with up to 6 keywords."""
    
    def __init__(self, columns: List[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle('Search Records - Multi-Keyword')
        self.resize(600, 500)
        self.columns = columns
        self.keyword_inputs = []
        self._build_ui()
    
    def _build_ui(self):
        layout = QVBoxLayout()
        
        # Info label
        info_label = QLabel(
            'Enter up to 6 keywords to search. Results will show records matching ANY keyword.\n'
            'Keywords will be searched across all selected columns.'
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Keyword inputs group
        keyword_group = QGroupBox('Keywords')
        keyword_layout = QVBoxLayout()
        
        for i in range(6):
            row_layout = QHBoxLayout()
            label = QLabel(f'Keyword {i+1}:')
            label.setMinimumWidth(80)
            input_field = QLineEdit()
            input_field.setPlaceholderText(f'e.g., name, phone, email, company, designation...')
            row_layout.addWidget(label)
            row_layout.addWidget(input_field)
            keyword_layout.addLayout(row_layout)
            self.keyword_inputs.append(input_field)
        
        keyword_group.setLayout(keyword_layout)
        layout.addWidget(keyword_group)
        
        # Column selection group
        column_group = QGroupBox('Search In Columns (select one or more)')
        column_layout = QVBoxLayout()
        
        # Select/Deselect all buttons
        select_btn_layout = QHBoxLayout()
        self.select_all_btn = QPushButton('Select All')
        self.select_all_btn.clicked.connect(self._select_all_columns)
        self.deselect_all_btn = QPushButton('Deselect All')
        self.deselect_all_btn.clicked.connect(self._deselect_all_columns)
        select_btn_layout.addWidget(self.select_all_btn)
        select_btn_layout.addWidget(self.deselect_all_btn)
        select_btn_layout.addStretch()
        column_layout.addLayout(select_btn_layout)
        
        # Scrollable column checkboxes
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        self.column_checkboxes = []
        for col in self.columns:
            checkbox = QCheckBox(col)
            checkbox.setChecked(True)  # All selected by default
            scroll_layout.addWidget(checkbox)
            self.column_checkboxes.append(checkbox)
        
        scroll.setWidget(scroll_widget)
        column_layout.addWidget(scroll)
        column_group.setLayout(column_layout)
        layout.addWidget(column_group)
        
        # Search options
        options_layout = QHBoxLayout()
        self.case_sensitive_checkbox = QCheckBox('Case Sensitive')
        options_layout.addWidget(self.case_sensitive_checkbox)
        options_layout.addStretch()
        layout.addLayout(options_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.search_btn = QPushButton('Search')
        self.search_btn.clicked.connect(self.accept)
        self.search_btn.setDefault(True)
        
        self.cancel_btn = QPushButton('Cancel')
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.search_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def _select_all_columns(self):
        for checkbox in self.column_checkboxes:
            checkbox.setChecked(True)
    
    def _deselect_all_columns(self):
        for checkbox in self.column_checkboxes:
            checkbox.setChecked(False)
    
    def get_search_params(self) -> Dict:
        """Return search parameters."""
        keywords = [inp.text().strip() for inp in self.keyword_inputs if inp.text().strip()]
        selected_columns = [
            checkbox.text() for checkbox in self.column_checkboxes if checkbox.isChecked()
        ]
        
        return {
            'keywords': keywords,
            'columns': selected_columns,
            'case_sensitive': self.case_sensitive_checkbox.isChecked()
        }
