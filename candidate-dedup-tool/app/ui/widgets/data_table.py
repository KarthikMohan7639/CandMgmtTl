import pandas as pd
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from typing import Optional


class DataTable(QTableWidget):
    """A QTableWidget wrapper for displaying pandas DataFrames."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlternatingRowColors(True)
    
    def set_dataframe(self, df: Optional[pd.DataFrame]) -> None:
        """Display a pandas DataFrame in the table."""
        if df is None or df.empty:
            self.clear()
            self.setRowCount(0)
            self.setColumnCount(0)
            return
        
        # Set dimensions
        self.setRowCount(len(df))
        self.setColumnCount(len(df.columns))
        self.setHorizontalHeaderLabels([str(col) for col in df.columns])
        
        # Populate cells
        for row_idx, (_, row) in enumerate(df.iterrows()):
            for col_idx, col_name in enumerate(df.columns):
                value = row[col_name]
                item = QTableWidgetItem(str(value) if pd.notna(value) else '')
                self.setItem(row_idx, col_idx, item)
        
        # Auto-resize columns to content
        self.resizeColumnsToContents()
    
    def clear(self) -> None:
        """Clear the table."""
        super().clear()
        self.setRowCount(0)
        self.setColumnCount(0)