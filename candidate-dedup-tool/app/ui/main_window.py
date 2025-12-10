from typing import Optional, Dict, List
import importlib
import logging
import pandas as pd

LOGGER = logging.getLogger(__name__)

# Defer PyQt5 imports so module can be imported in non-GUI test environments
PYQT_AVAILABLE = True
try:
    from PyQt5.QtWidgets import (
        QMainWindow, QApplication, QAction, QToolBar, QTabWidget,
        QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel,
        QStatusBar, QProgressBar, QMessageBox
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal
except Exception:
    PYQT_AVAILABLE = False
    # Provide placeholders so importing this module doesn't crash
    QMainWindow = object
    QApplication = object
    QAction = object
    QToolBar = object
    QTabWidget = object
    QWidget = object
    QVBoxLayout = object
    QTableWidget = object
    QTableWidgetItem = object
    QLabel = object
    QStatusBar = object
    QProgressBar = object
    QMessageBox = object
    Qt = object
    QThread = object
    def pyqtSignal(*args, **kwargs):
        return None


if PYQT_AVAILABLE:
    class DuplicateDetectWorker(QThread):
        finished = pyqtSignal(object, object)

        def __init__(self, df, phone_col, email_col):
            super().__init__()
            self.df = df
            self.phone_col = phone_col
            self.email_col = email_col

        def run(self):
            try:
                from app.services import detect_duplicates, normalize_phone, normalize_email
                unique_df, groups = detect_duplicates(self.df, self.phone_col, self.email_col, normalize_phone, normalize_email)
                self.finished.emit(unique_df, groups)
            except Exception as ex:
                self.finished.emit(None, {'error': str(ex)})
else:
    class DuplicateDetectWorker:
        def __init__(self, *args, **kwargs):
            raise RuntimeError('PyQt5 is required to run the GUI worker')


if PYQT_AVAILABLE:
    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle('Candidate Deduplication Tool')
            self.resize(1000, 700)

            # Application state
            self.df_all: Optional[pd.DataFrame] = None
            self.df_unique: Optional[pd.DataFrame] = None
            self.duplicate_groups: Dict[str, List[int]] = {}
            self.current_header_mapping: Dict[str, str] = {}
            self.loaded_files: List[str] = []

            self._create_actions()
            self._create_menu()
            self._create_toolbar()
            self._create_tabs()
            self._create_statusbar()
        def _create_actions(self):
            self.load_action = QAction('Load Files', self)
            self.load_action.triggered.connect(self.on_load_files)

            self.clear_data_action = QAction('Clear Data', self)
            self.clear_data_action.triggered.connect(self.on_clear_data)
    
            self.exit_action = QAction('Exit', self)
            self.exit_action.triggered.connect(self.close)
    
            self.map_headers_action = QAction('Map Headers', self)
            self.map_headers_action.triggered.connect(self.on_detect_headers)
    
            self.find_duplicates_action = QAction('Find Duplicates', self)
            self.find_duplicates_action.triggered.connect(self.on_find_duplicates)
    
            self.export_action = QAction('Export', self)
            self.export_action.triggered.connect(self.export)

            self.export_all_action = QAction('Export All Data', self)
            self.export_all_action.triggered.connect(self.on_export_all)
    
            self.merge_action = QAction('Merge', self)
            self.merge_action.triggered.connect(self.on_auto_merge)
    
            self.export_unique_action = QAction('Export Unique', self)
            self.export_unique_action.triggered.connect(self.on_export_unique)
    
            self.export_duplicates_action = QAction('Export Duplicates', self)
            self.export_duplicates_action.triggered.connect(self.on_export_duplicates)

            self.delete_duplicates_action = QAction('Delete Duplicates from Source', self)
            self.delete_duplicates_action.triggered.connect(self.on_delete_duplicates_from_source)

            self.search_action = QAction('Search Records', self)
            self.search_action.triggered.connect(self.on_search_records)
    

        def _create_menu(self):
            menubar = self.menuBar()
            file_menu = menubar.addMenu('File')
            file_menu.addAction(self.load_action)
            file_menu.addAction(self.clear_data_action)
            file_menu.addAction(self.export_all_action)
            file_menu.addAction(self.exit_action)
    
            tools_menu = menubar.addMenu('Tools')
            tools_menu.addAction(self.search_action)
            tools_menu.addAction(self.map_headers_action)
            tools_menu.addAction(self.find_duplicates_action)
            tools_menu.addAction(self.delete_duplicates_action)
            tools_menu.addAction(self.export_action)
    

        def _create_toolbar(self):
            toolbar = QToolBar('Main')
            self.addToolBar(toolbar)
            toolbar.addAction(self.load_action)
            toolbar.addAction(self.clear_data_action)
            toolbar.addAction(self.search_action)
            toolbar.addAction(self.export_all_action)
            toolbar.addAction(self.map_headers_action)
            toolbar.addAction(self.find_duplicates_action)
            toolbar.addAction(self.merge_action)
            toolbar.addAction(self.delete_duplicates_action)
            toolbar.addAction(self.export_unique_action)
            toolbar.addAction(self.export_duplicates_action)
    

        def _create_tabs(self):
            self.tabs = QTabWidget()
            self.setCentralWidget(self.tabs)
    
            # Tab: Loaded Data
            self.loaded_widget = QWidget()
            self.loaded_layout = QVBoxLayout()
            self.data_table = QTableWidget()
            # Optimize table for large datasets
            self.data_table.setAlternatingRowColors(True)
            self.data_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Read-only for performance
            self.loaded_layout.addWidget(self.data_table)
            self.loaded_widget.setLayout(self.loaded_layout)
            self.tabs.addTab(self.loaded_widget, 'Loaded Data')
    
            # Tab: Duplicates
            self.duplicates_widget = QWidget()
            self.duplicates_layout = QVBoxLayout()
            # Use DuplicateView widget for listing groups and showing records
            try:
                mod = importlib.import_module('app.ui.widgets.duplicate_view')
                DuplicateView = getattr(mod, 'DuplicateView')
                self.duplicate_view = DuplicateView()
                self.duplicates_layout.addWidget(self.duplicate_view)
            except Exception:
                # Fallback to a simple label if widget import fails
                self.duplicates_layout.addWidget(QLabel('Duplicate groups view unavailable'))
            self.duplicates_widget.setLayout(self.duplicates_layout)
            self.tabs.addTab(self.duplicates_widget, 'Duplicates')

            # Tab: Unique Records (Non-Duplicates)
            self.unique_widget = QWidget()
            self.unique_layout = QVBoxLayout()
            self.unique_table = QTableWidget()
            self.unique_table.setAlternatingRowColors(True)
            self.unique_table.setEditTriggers(QTableWidget.NoEditTriggers)
            self.unique_layout.addWidget(self.unique_table)
            self.unique_widget.setLayout(self.unique_layout)
            self.tabs.addTab(self.unique_widget, 'Unique Records')

            # Tab: Search Results
            self.search_widget = QWidget()
            self.search_layout = QVBoxLayout()
            self.search_info_label = QLabel('No search performed yet')
            self.search_table = QTableWidget()
            self.search_table.setAlternatingRowColors(True)
            self.search_table.setEditTriggers(QTableWidget.NoEditTriggers)
            self.search_layout.addWidget(self.search_info_label)
            self.search_layout.addWidget(self.search_table)
            self.search_widget.setLayout(self.search_layout)
            self.tabs.addTab(self.search_widget, 'Search Results')
    
            # Tab: Merge Review
            self.merge_widget = QWidget()
            self.merge_layout = QVBoxLayout()
            self.merge_table = QTableWidget()
            self.merge_layout.addWidget(self.merge_table)
            self.merge_widget.setLayout(self.merge_layout)
            self.tabs.addTab(self.merge_widget, 'Merge Review')
    

        def _create_statusbar(self):
            sb = QStatusBar()
            self.status_label = QLabel('Ready')
            self.progress_bar = QProgressBar()
            self.progress_bar.setMaximum(100)
            self.progress_bar.setValue(0)
            sb.addWidget(self.status_label)
            sb.addPermanentWidget(self.progress_bar)
            self.setStatusBar(sb)
    

        def load_files(self):
            # Deprecated; kept for compatibility
            self.on_load_files()
    

        def on_load_files(self):
            # Open file load dialog
            LOGGER.info('User initiated file load')
            try:
                fld_mod = importlib.import_module('app.ui.dialogs.file_load_dialog')
                FileLoadDialog = getattr(fld_mod, 'FileLoadDialog')
            except Exception:
                QMessageBox.critical(self, 'Error', 'FileLoadDialog not available')
                return
    
            dlg = FileLoadDialog(self)
            if dlg.exec_() != dlg.Accepted:
                return
            paths = dlg.get_selected_files()
            if not paths:
                QMessageBox.information(self, 'Load', 'No files selected')
                return
    
            try:
                loader = importlib.import_module('app.services.excel_loader')
                combined = loader.load_multiple_excel_files(paths)
                if combined is None or combined.empty:
                    LOGGER.warning('No data loaded from selected files')
                    QMessageBox.warning(self, 'Load', 'No data loaded from selected files')
                    return
                
                # Convert all column names to lowercase for consistent comparison
                combined.columns = [str(col).lower().strip() for col in combined.columns]
                LOGGER.info('Converted column names to lowercase: %s', list(combined.columns))
                
                self.df_all = combined
                self.loaded_files = paths
                
                # Auto-detect and map columns based on content
                self._auto_detect_and_map()
                
                self.populate_table()
                self.status_label.setText(f'Loaded {len(self.df_all)} records from {len(paths)} file(s)')
                LOGGER.info('Loaded %d records from %d files', len(self.df_all), len(paths))
            except Exception as ex:
                QMessageBox.critical(self, 'Error', f'Failed to load files: {ex}')
    
        def _auto_detect_and_map(self):
            """Auto-detect phone and email columns based on content."""
            if self.df_all is None or self.df_all.empty:
                return
            
            try:
                hd_mod = importlib.import_module('app.services.header_detector')
                detect_headers = getattr(hd_mod, 'detect_headers')
                columns = list(self.df_all.columns)
                detected = detect_headers(columns, df=self.df_all)
                
                # Build mapping from detected fields
                self.current_header_mapping = {}
                for col, info in detected.items():
                    self.current_header_mapping[col] = info.get('field', 'OTHER')
                
                LOGGER.info('Auto-detected column mappings: %s', self.current_header_mapping)
            except Exception as ex:
                LOGGER.warning('Auto-detection failed: %s', ex)

        def populate_table(self, max_rows=10000):
            """Populate table with optimization for large datasets."""
            if self.df_all is None or self.df_all.empty:
                self.data_table.clear()
                self.data_table.setRowCount(0)
                self.data_table.setColumnCount(0)
                return
            
            df = self.df_all
            total_rows = len(df)
            
            # Limit display for performance
            if total_rows > max_rows:
                QMessageBox.information(
                    self,
                    'Large Dataset',
                    f'Dataset has {total_rows} rows. Displaying first {max_rows} rows for performance.\n\n'
                    f'All data is loaded and will be used for duplicate detection and export.'
                )
                df = df.head(max_rows)
            
            cols = list(df.columns)
            self.data_table.setColumnCount(len(cols))
            self.data_table.setHorizontalHeaderLabels(cols)
            self.data_table.setRowCount(len(df))
            
            # Disable updates during population for better performance
            self.data_table.setUpdatesEnabled(False)
            
            try:
                # Use itertuples which is much faster than iterrows
                for r_idx, row in enumerate(df.itertuples(index=False)):
                    for c_idx, value in enumerate(row):
                        item = QTableWidgetItem(str(value) if pd.notna(value) else '')
                        self.data_table.setItem(r_idx, c_idx, item)
            finally:
                self.data_table.setUpdatesEnabled(True)
            
            LOGGER.info('Populated table with %d rows (total: %d)', len(df), total_rows)

        def populate_unique_table(self, max_rows=10000):
            """Populate the unique records table with non-duplicate records."""
            if self.df_unique is None or self.df_unique.empty:
                self.unique_table.clear()
                self.unique_table.setRowCount(0)
                self.unique_table.setColumnCount(0)
                return
            
            df = self.df_unique
            total_rows = len(df)
            
            # Limit display for performance
            if total_rows > max_rows:
                df = df.head(max_rows)
            
            cols = list(df.columns)
            self.unique_table.setColumnCount(len(cols))
            self.unique_table.setHorizontalHeaderLabels(cols)
            self.unique_table.setRowCount(len(df))
            
            # Disable updates during population
            self.unique_table.setUpdatesEnabled(False)
            
            try:
                for r_idx, row in enumerate(df.itertuples(index=False)):
                    for c_idx, value in enumerate(row):
                        item = QTableWidgetItem(str(value) if pd.notna(value) else '')
                        self.unique_table.setItem(r_idx, c_idx, item)
            finally:
                self.unique_table.setUpdatesEnabled(True)
            
            LOGGER.info('Populated unique table with %d records (total: %d)', len(df), total_rows)
    

        def map_headers(self):
            # Deprecated wrapper
            self.on_detect_headers()
    

        def on_detect_headers(self):
            if self.df_all is None or self.df_all.empty:
                QMessageBox.information(self, 'Detect Headers', 'Load data first')
                return
            LOGGER.info('User requested header detection')
            try:
                hd_mod = importlib.import_module('app.services.header_detector')
                detect_headers = getattr(hd_mod, 'detect_headers')
                columns = list(self.df_all.columns)
                # Pass DataFrame for content-based detection
                detected = detect_headers(columns, df=self.df_all)
    
                # load saved mappings
                ms = importlib.import_module('app.services.mapping_storage')
                saved = ms.load_mappings()
    
                # show mapping dialog
                from app.ui.dialogs.mapping_dialog import MappingDialog
                sample_rows = [self.df_all.iloc[i].to_dict() for i in range(min(3, len(self.df_all)))]
                dlg = MappingDialog(columns, detected, sample_rows, parent=self)
                if dlg.exec_():
                    final_map = dlg.get_final_mapping()
                    # persist mapping under first loaded filename key
                    key = ''
                    if self.loaded_files:
                        import os
                        key = os.path.basename(self.loaded_files[0])
                    if key:
                        saved[key] = final_map
                        try:
                            ms.save_mappings(saved)
                        except Exception as ex:
                            QMessageBox.warning(self, 'Mapping', f'Saved mapping failed: {ex}')
                    self.current_header_mapping = final_map
                    LOGGER.info('Header mapping saved for key=%s: %s', key, final_map)
                    QMessageBox.information(self, 'Mapping', 'Header mapping saved')
            except Exception as ex:
                QMessageBox.critical(self, 'Error', f'Header mapping failed: {ex}')
    

        def find_duplicates(self):
            # Deprecated wrapper
            self.on_find_duplicates()
    

        def on_find_duplicates(self):
            if self.df_all is None or self.df_all.empty:
                QMessageBox.information(self, 'Find Duplicates', 'Load data first')
                return
    
            # Determine phone/email columns from current_header_mapping
            phone_col = None
            email_col = None
            
            for col, f in self.current_header_mapping.items():
                if f == 'PHONE' and phone_col is None:
                    phone_col = col
                if f == 'EMAIL' and email_col is None:
                    email_col = col
    
            # If not found in mapping, try to auto-detect
            if phone_col is None or email_col is None:
                cols = list(self.df_all.columns)
                if phone_col is None:
                    phone_candidates = [c for c in cols if 'phone' in c.lower() or 'mobile' in c.lower() or 'contact' in c.lower()]
                    phone_col = phone_candidates[0] if phone_candidates else cols[0]
                if email_col is None:
                    email_candidates = [c for c in cols if 'email' in c.lower() or 'mail' in c.lower()]
                    email_col = email_candidates[0] if email_candidates else (cols[1] if len(cols) > 1 else cols[0])
            
            # Show detected columns to user
            msg = f"Duplicate detection will use:\n\nPhone Column: {phone_col}\nEmail Column: {email_col}\n\nContinue?"
            reply = QMessageBox.question(
                self, 
                'Confirm Columns', 
                msg,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.No:
                # Let user select manually
                from PyQt5.QtWidgets import QInputDialog
                items = list(self.df_all.columns)
                phone_col, ok1 = QInputDialog.getItem(
                    self, 'Select Phone Column', 
                    'Choose the column containing phone numbers:', 
                    items, items.index(phone_col) if phone_col in items else 0, False
                )
                if not ok1:
                    return
                
                email_col, ok2 = QInputDialog.getItem(
                    self, 'Select Email Column', 
                    'Choose the column containing email addresses:', 
                    items, items.index(email_col) if email_col in items else 0, False
                )
                if not ok2:
                    return
    
            LOGGER.info('Starting duplicate detection (phone=%s email=%s)', phone_col, email_col)
            self.status_label.setText(f'Finding duplicates by {phone_col} and {email_col}...')
            self.progress_bar.setValue(10)
            # run worker
            self.worker = DuplicateDetectWorker(self.df_all, phone_col, email_col)
            self.worker.finished.connect(self.on_duplicates_found)
            self.worker.start()
    

        def on_duplicates_found(self, unique_df, groups):
            # Check if there was an error
            if unique_df is None and isinstance(groups, dict) and 'error' in groups:
                QMessageBox.critical(self, 'Error', f"Duplicate detection failed: {groups.get('error')}")
                self.status_label.setText('Error')
                return
            
            # Validate that we received proper data
            if not isinstance(groups, dict):
                QMessageBox.critical(self, 'Error', 'Invalid duplicate detection result')
                self.status_label.setText('Error')
                return
                
            self.status_label.setText('Duplicate detection complete')
            self.progress_bar.setValue(100)
            LOGGER.info('Duplicate detection complete: %d groups', len(groups))
            
            # Log detailed information about duplicate groups
            total_duplicates = sum(len(members) for members in groups.values())
            LOGGER.info('Total duplicate records: %d in %d groups', total_duplicates, len(groups))
            for gid, members in list(groups.items())[:3]:  # Log first 3 groups
                LOGGER.info('Group %s has %d members: %s', gid, len(members), members)
            
            self.duplicate_groups = groups
            # update df_unique and show in merge review
            self.df_unique = unique_df
            self.populate_merge_table()
            self.populate_unique_table()
    
            # add duplicate_group id to df_all for display purposes
            try:
                if self.df_all is not None and not self.df_all.empty:
                    # map index to group id
                    idx_to_gid = {}
                    for gid, members in groups.items():
                        for idx in members:
                            idx_to_gid[idx] = gid
                    
                    # Safely add duplicate_group column
                    self.df_all = self.df_all.copy()
                    self.df_all['duplicate_group'] = None
                    for idx, gid in idx_to_gid.items():
                        if idx in self.df_all.index:
                            self.df_all.at[idx, 'duplicate_group'] = gid
                    
                    self.populate_table()
            except Exception as ex:
                LOGGER.warning('Failed to add duplicate_group column: %s', ex)
    
            # populate DuplicateView if available
            try:
                if hasattr(self, 'duplicate_view'):
                    self.duplicate_view.set_groups(self.duplicate_groups, self.df_all)
            except Exception:
                pass
    

        def populate_merge_table(self):
            if not hasattr(self, 'df_unique') or self.df_unique is None:
                return
            df = self.df_unique
            cols = list(df.columns)
            self.merge_table.setColumnCount(len(cols))
            self.merge_table.setHorizontalHeaderLabels(cols)
            self.merge_table.setRowCount(len(df))
            for r_idx, (_, row) in enumerate(df.iterrows()):
                for c_idx, col in enumerate(cols):
                    item = QTableWidgetItem(str(row.get(col, '')))
                    self.merge_table.setItem(r_idx, c_idx, item)
    

        def merge_selected(self):
            QMessageBox.information(self, 'Merge', 'Use Merge dialog from Duplicates tab')
    

        def on_auto_merge(self):
            if not self.duplicate_groups or self.df_all is None:
                QMessageBox.information(self, 'Auto Merge', 'No duplicate groups to merge')
                return
            LOGGER.info('User requested auto-merge of %d groups', len(self.duplicate_groups))
            try:
                ms = importlib.import_module('app.services.merge_service')
                merged_df, decisions_log = ms.auto_merge_all_groups(self.duplicate_groups, self.df_all)
                # merged_df is expected to be the dataframe of merged unique rows
                self.df_unique = merged_df
                self.populate_merge_table()
                QMessageBox.information(self, 'Auto Merge', f'Auto-merged {len(self.duplicate_groups)} groups')
                LOGGER.info('Auto-merge completed, new unique rows=%d', len(self.df_unique))
            except Exception as ex:
                QMessageBox.critical(self, 'Auto Merge Error', str(ex))
    

        def on_clear_data(self):
            """Clear all loaded data and reset the application state."""
            reply = QMessageBox.question(
                self,
                'Clear Data',
                'Are you sure you want to clear all loaded data?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                LOGGER.info('User cleared all data')
                self.df_all = None
                self.df_unique = None
                self.duplicate_groups = []
                self.loaded_files = []
                self.phone_col = None
                self.email_col = None
                
                # Clear the data table
                self.data_table.clear()
                self.data_table.setRowCount(0)
                self.data_table.setColumnCount(0)
                
                # Clear duplicate view
                try:
                    if hasattr(self, 'duplicate_view'):
                        self.duplicate_view.clear()
                except Exception:
                    pass
                
                self.status_label.setText('Ready')
                self.progress_bar.setValue(0)
                QMessageBox.information(self, 'Clear Data', 'All data has been cleared')

        def on_export_all(self):
            """Export all loaded data to Excel file."""
            if self.df_all is None or self.df_all.empty:
                QMessageBox.information(self, 'Export All', 'No data loaded to export')
                return
            
            LOGGER.info('User requested export all data')
            try:
                # Column selection dialog
                col_mod = importlib.import_module('app.ui.dialogs.column_selection_dialog')
                ColumnSelectionDialog = getattr(col_mod, 'ColumnSelectionDialog')
                col_dlg = ColumnSelectionDialog(list(self.df_all.columns), self)
                
                if col_dlg.exec_() != col_dlg.Accepted:
                    return
                
                selected_cols = col_dlg.get_selected_columns()
                if not selected_cols:
                    QMessageBox.warning(self, 'Export', 'No columns selected')
                    return
                
                from PyQt5.QtWidgets import QFileDialog
                file_path, _ = QFileDialog.getSaveFileName(
                    self, 
                    'Export All Loaded Data', 
                    '', 
                    'Excel Files (*.xlsx)'
                )
                
                if not file_path:
                    return
                
                if not file_path.endswith('.xlsx'):
                    file_path += '.xlsx'
                
                # Show progress for large datasets
                total_rows = len(self.df_all)
                self.status_label.setText(f'Exporting {total_rows} records...')
                self.progress_bar.setValue(10)
                
                # Export only selected columns with optimizations for large files
                try:
                    # Use openpyxl engine with optimization
                    self.df_all[selected_cols].to_excel(
                        file_path, 
                        index=False, 
                        engine='openpyxl'
                    )
                    self.progress_bar.setValue(100)
                except Exception as write_ex:
                    # Fallback: try xlsxwriter which can be faster for large datasets
                    try:
                        self.df_all[selected_cols].to_excel(
                            file_path, 
                            index=False, 
                            engine='xlsxwriter'
                        )
                        self.progress_bar.setValue(100)
                    except Exception:
                        raise write_ex
                QMessageBox.information(
                    self, 
                    'Export Complete', 
                    f'Exported {len(self.df_all)} records with {len(selected_cols)} columns to {file_path}'
                )
                LOGGER.info('Exported all data (%d records, %d columns) to %s', len(self.df_all), len(selected_cols), file_path)
            except Exception as ex:
                LOGGER.exception('Export all failed: %s', ex)
                QMessageBox.critical(self, 'Export Error', str(ex))

        def export(self):
            QMessageBox.information(self, 'Export', 'Choose Export Unique or Export Duplicates')
    

        def export_unique(self):
            # Deprecated wrapper
            self.on_export_unique()
    

        def on_export_unique(self):
            if self.df_unique is None:
                QMessageBox.information(self, 'Export Unique', 'No unique data to export')
                return
            LOGGER.info('User requested export unique')
            try:
                # Column selection dialog
                col_mod = importlib.import_module('app.ui.dialogs.column_selection_dialog')
                ColumnSelectionDialog = getattr(col_mod, 'ColumnSelectionDialog')
                col_dlg = ColumnSelectionDialog(list(self.df_unique.columns), self)
                
                if col_dlg.exec_() != col_dlg.Accepted:
                    return
                
                selected_cols = col_dlg.get_selected_columns()
                if not selected_cols:
                    QMessageBox.warning(self, 'Export', 'No columns selected')
                    return
                
                ed = importlib.import_module('app.ui.dialogs.export_dialog')
                ExportDialog = getattr(ed, 'ExportDialog')
                dlg = ExportDialog(self)
                if dlg.exec_() != dlg.Accepted:
                    return
                unique_path, dup_path = dlg.get_paths()
                if not unique_path:
                    QMessageBox.information(self, 'Export', 'No path selected for unique export')
                    return
                
                # Export only selected columns
                self.df_unique[selected_cols].to_excel(unique_path, index=False, engine='openpyxl')
                QMessageBox.information(
                    self, 
                    'Export', 
                    f'Exported {len(self.df_unique)} unique records with {len(selected_cols)} columns to {unique_path}'
                )
                LOGGER.info('Exported unique records (%d rows, %d columns) to %s', len(self.df_unique), len(selected_cols), unique_path)
            except Exception as ex:
                LOGGER.exception('Export unique failed: %s', ex)
                QMessageBox.critical(self, 'Export Error', str(ex))
    

        def export_duplicates(self):
            # Deprecated wrapper
            self.on_export_duplicates()
    

        def on_export_duplicates(self):
            if not self.duplicate_groups or self.df_all is None:
                QMessageBox.information(self, 'Export Duplicates', 'No duplicate groups to export')
                return
            LOGGER.info('User requested export duplicates')
            try:
                ed = importlib.import_module('app.ui.dialogs.export_dialog')
                ExportDialog = getattr(ed, 'ExportDialog')
                dlg = ExportDialog(self)
                if dlg.exec_() != dlg.Accepted:
                    return
                unique_path, dup_path = dlg.get_paths()
                # prefer dup_path
                path = dup_path or unique_path
                if not path:
                    QMessageBox.information(self, 'Export', 'No path selected for export')
                    return
                es = importlib.import_module('app.services.export_service')
                es.export_duplicate_records(self.duplicate_groups, self.df_all, path)
                QMessageBox.information(self, 'Export', f'Exported duplicate records to {path}')
                LOGGER.info('Exported duplicate records to %s', path)
            except Exception as ex:
                LOGGER.exception('Export duplicates failed: %s', ex)
                QMessageBox.critical(self, 'Export Error', str(ex))
    

        def on_delete_duplicates_from_source(self):
            """Delete duplicate rows permanently from the source Excel files."""
            if not self.duplicate_groups or self.df_all is None:
                QMessageBox.information(self, 'Delete Duplicates', 'No duplicate groups found. Please run duplicate detection first.')
                return
            
            if not self.loaded_files:
                QMessageBox.warning(self, 'Delete Duplicates', 'No source files loaded')
                return
            
            # Count duplicates to be deleted
            duplicate_count = sum(len(members) - 1 for members in self.duplicate_groups.values())
            
            # Show warning dialog
            warning_msg = (
                f"⚠️ WARNING: PERMANENT DELETE OPERATION ⚠️\n\n"
                f"This will PERMANENTLY DELETE {duplicate_count} duplicate rows from the source Excel files:\n\n"
            )
            
            for file_path in self.loaded_files[:5]:  # Show first 5 files
                import os
                warning_msg += f"  • {os.path.basename(file_path)}\n"
            
            if len(self.loaded_files) > 5:
                warning_msg += f"  ... and {len(self.loaded_files) - 5} more files\n"
            
            warning_msg += (
                f"\n{len(self.duplicate_groups)} duplicate groups will be reduced to 1 record each.\n"
                f"Original files will be OVERWRITTEN!\n\n"
                f"This action CANNOT be undone!\n\n"
                f"Are you sure you want to proceed?"
            )
            
            reply = QMessageBox.critical(
                self,
                'DELETE DUPLICATES FROM SOURCE - PERMANENT ACTION',
                warning_msg,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                LOGGER.info('User cancelled delete duplicates operation')
                return
            
            # Second confirmation
            confirm_msg = (
                f"FINAL CONFIRMATION\n\n"
                f"You are about to PERMANENTLY DELETE {duplicate_count} rows from {len(self.loaded_files)} file(s).\n\n"
                f"Type 'DELETE' to confirm:"
            )
            
            from PyQt5.QtWidgets import QInputDialog
            text, ok = QInputDialog.getText(
                self,
                'Final Confirmation',
                confirm_msg
            )
            
            if not ok or text.strip().upper() != 'DELETE':
                QMessageBox.information(self, 'Cancelled', 'Delete operation cancelled')
                LOGGER.info('User did not confirm DELETE text')
                return
            
            # Proceed with deletion
            try:
                self.status_label.setText('Deleting duplicates from source files...')
                self.progress_bar.setValue(10)
                
                # Get indices of rows to keep (representatives from each group + non-duplicates)
                all_duplicate_indices = set()
                for members in self.duplicate_groups.values():
                    # Keep first, delete rest
                    for idx in members[1:]:
                        all_duplicate_indices.add(idx)
                
                # Group indices by source file
                if 'source_file' not in self.df_all.columns:
                    QMessageBox.critical(self, 'Error', 'Cannot determine source files for rows')
                    return
                
                files_to_update = {}
                for idx in all_duplicate_indices:
                    source_file = self.df_all.loc[idx, 'source_file']
                    if source_file not in files_to_update:
                        files_to_update[source_file] = []
                    files_to_update[source_file].append(idx)
                
                # Update each file
                updated_count = 0
                for file_path, indices_to_delete in files_to_update.items():
                    try:
                        # Read the original file
                        df_file = pd.read_excel(file_path, engine='openpyxl')
                        original_count = len(df_file)
                        
                        # Get rows from this file in df_all
                        file_mask = self.df_all['source_file'] == file_path
                        file_indices = self.df_all[file_mask].index.tolist()
                        
                        # Map df_all indices to original file row numbers
                        rows_to_delete = []
                        for df_all_idx in indices_to_delete:
                            if df_all_idx in file_indices:
                                original_row = file_indices.index(df_all_idx)
                                rows_to_delete.append(original_row)
                        
                        # Delete rows
                        df_file_cleaned = df_file.drop(rows_to_delete).reset_index(drop=True)
                        
                        # Save back to file
                        df_file_cleaned.to_excel(file_path, index=False, engine='openpyxl')
                        
                        deleted = original_count - len(df_file_cleaned)
                        updated_count += deleted
                        LOGGER.info('Deleted %d rows from %s', deleted, file_path)
                        
                    except Exception as ex:
                        LOGGER.exception('Failed to update file %s: %s', file_path, ex)
                        QMessageBox.warning(self, 'File Update Error', f'Failed to update {file_path}: {ex}')
                
                self.progress_bar.setValue(100)
                
                # Reload data
                QMessageBox.information(
                    self,
                    'Delete Complete',
                    f'Successfully deleted {updated_count} duplicate rows from {len(files_to_update)} file(s).\n\n'
                    f'Files have been updated. Please reload to see changes.'
                )
                
                LOGGER.info('Deleted %d duplicates from %d files', updated_count, len(files_to_update))
                
                # Clear current data
                self.on_clear_data()
                
            except Exception as ex:
                LOGGER.exception('Delete duplicates failed: %s', ex)
                QMessageBox.critical(self, 'Delete Error', f'Failed to delete duplicates: {ex}')
                self.status_label.setText('Delete failed')
    

        def on_search_records(self):
            """Search for records using multiple keywords across selected columns."""
            if self.df_all is None or self.df_all.empty:
                QMessageBox.information(self, 'Search', 'No data loaded. Please load files first.')
                return
            
            try:
                # Show search dialog
                from app.ui.dialogs.search_dialog import SearchDialog
                dlg = SearchDialog(list(self.df_all.columns), self)
                
                if dlg.exec_() != dlg.Accepted:
                    return
                
                search_params = dlg.get_search_params()
                keywords = search_params['keywords']
                columns = search_params['columns']
                case_sensitive = search_params['case_sensitive']
                
                if not keywords:
                    QMessageBox.warning(self, 'Search', 'Please enter at least one keyword')
                    return
                
                if not columns:
                    QMessageBox.warning(self, 'Search', 'Please select at least one column to search')
                    return
                
                LOGGER.info('Searching for keywords: %s in columns: %s', keywords, columns)
                self.status_label.setText('Searching...')
                self.progress_bar.setValue(50)
                
                # Perform optimized search using vectorized operations
                mask = pd.Series([False] * len(self.df_all), index=self.df_all.index)
                
                # Build regex pattern for faster searching
                import re
                if case_sensitive:
                    pattern = '|'.join(re.escape(kw) for kw in keywords)
                    flags = 0
                else:
                    pattern = '|'.join(re.escape(kw) for kw in keywords)
                    flags = re.IGNORECASE
                
                for column in columns:
                    if column not in self.df_all.columns:
                        continue
                    
                    try:
                        # Use vectorized string operations for better performance
                        mask |= self.df_all[column].astype(str).str.contains(
                            pattern, 
                            case=case_sensitive, 
                            na=False, 
                            regex=True,
                            flags=flags
                        )
                    except Exception as ex:
                        LOGGER.warning('Search failed for column %s: %s', column, ex)
                        continue
                
                # Get matching rows
                results = self.df_all[mask].copy()
                
                # Display results
                self.populate_search_results(results, keywords, columns)
                
                self.progress_bar.setValue(100)
                self.status_label.setText(f'Search complete: {len(results)} records found')
                
                # Switch to Search Results tab
                self.tabs.setCurrentWidget(self.search_widget)
                
                LOGGER.info('Search found %d records', len(results))
                
            except Exception as ex:
                LOGGER.exception('Search failed: %s', ex)
                QMessageBox.critical(self, 'Search Error', f'Search failed: {ex}')
                self.status_label.setText('Search failed')
    

        def populate_search_results(self, df: pd.DataFrame, keywords: List[str], columns: List[str], max_rows=10000):
            """Populate the search results table."""
            if df is None or df.empty:
                self.search_info_label.setText('No records found matching your search criteria')
                self.search_table.clear()
                self.search_table.setRowCount(0)
                self.search_table.setColumnCount(0)
                return
            
            total_rows = len(df)
            display_df = df.head(max_rows) if total_rows > max_rows else df
            
            keyword_str = ', '.join(f'"{k}"' for k in keywords)
            column_str = ', '.join(columns)
            display_msg = f'Found {total_rows} records matching keywords: {keyword_str}\nSearched in columns: {column_str}'
            if total_rows > max_rows:
                display_msg += f'\n(Displaying first {max_rows} results for performance)'
            self.search_info_label.setText(display_msg)
            
            cols = list(display_df.columns)
            self.search_table.setColumnCount(len(cols))
            self.search_table.setHorizontalHeaderLabels(cols)
            self.search_table.setRowCount(len(display_df))
            
            # Disable updates during population
            self.search_table.setUpdatesEnabled(False)
            
            try:
                for r_idx, row in enumerate(display_df.itertuples(index=False)):
                    for c_idx, value in enumerate(row):
                        item = QTableWidgetItem(str(value) if pd.notna(value) else '')
                        self.search_table.setItem(r_idx, c_idx, item)
            finally:
                self.search_table.setUpdatesEnabled(True)
            
            LOGGER.info('Populated search results table with %d records (total: %d)', len(display_df), total_rows)
    

        def run(self):
            app = QApplication.instance() or QApplication([])
            self.show()
            app.exec_()
else:
    class MainWindow:
        def __init__(self, *args, **kwargs):
            raise RuntimeError('PyQt5 is required to create the MainWindow')
