from typing import Optional, Dict, List
import importlib

import pandas as pd

from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QAction, QToolBar, QTabWidget,
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel,
    QStatusBar, QProgressBar, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import logging

LOGGER = logging.getLogger(__name__)


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

        self.exit_action = QAction('Exit', self)
        self.exit_action.triggered.connect(self.close)

        self.map_headers_action = QAction('Map Headers', self)
        self.map_headers_action.triggered.connect(self.on_detect_headers)

        self.find_duplicates_action = QAction('Find Duplicates', self)
        self.find_duplicates_action.triggered.connect(self.on_find_duplicates)

        self.export_action = QAction('Export', self)
        self.export_action.triggered.connect(self.export)

        self.merge_action = QAction('Merge', self)
        self.merge_action.triggered.connect(self.on_auto_merge)

        self.export_unique_action = QAction('Export Unique', self)
        self.export_unique_action.triggered.connect(self.on_export_unique)

        self.export_duplicates_action = QAction('Export Duplicates', self)
        self.export_duplicates_action.triggered.connect(self.on_export_duplicates)

    def _create_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        file_menu.addAction(self.load_action)
        file_menu.addAction(self.exit_action)

        tools_menu = menubar.addMenu('Tools')
        tools_menu.addAction(self.map_headers_action)
        tools_menu.addAction(self.find_duplicates_action)
        tools_menu.addAction(self.export_action)

    def _create_toolbar(self):
        toolbar = QToolBar('Main')
        self.addToolBar(toolbar)
        toolbar.addAction(self.load_action)
        toolbar.addAction(self.map_headers_action)
        toolbar.addAction(self.find_duplicates_action)
        toolbar.addAction(self.merge_action)
        toolbar.addAction(self.export_unique_action)
        toolbar.addAction(self.export_duplicates_action)

    def _create_tabs(self):
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Tab: Loaded Data
        self.loaded_widget = QWidget()
        self.loaded_layout = QVBoxLayout()
        self.data_table = QTableWidget()
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
            self.df_all = combined
            self.loaded_files = paths
            self.populate_table(df=self.df_all)
            self.status_label.setText(f'Loaded {len(self.df_all)} records from {len(paths)} file(s)')
            LOGGER.info('Loaded %d records from %d files', len(self.df_all), len(paths))
        except Exception as ex:
            QMessageBox.critical(self, 'Error', f'Failed to load files: {ex}')

    def populate_table(self):
        if self.df_all is None or self.df_all.empty:
            self.data_table.clear()
            self.data_table.setRowCount(0)
            self.data_table.setColumnCount(0)
            return
        df = self.df_all
        cols = list(df.columns)
        self.data_table.setColumnCount(len(cols))
        self.data_table.setHorizontalHeaderLabels(cols)
        self.data_table.setRowCount(len(df))
        for r_idx, (_, row) in enumerate(df.iterrows()):
            for c_idx, col in enumerate(cols):
                item = QTableWidgetItem(str(row.get(col, '')))
                self.data_table.setItem(r_idx, c_idx, item)

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
            detected = detect_headers(columns)

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

        # Determine phone/email columns from current_header_mapping or auto-detect
        phone_col = None
        email_col = None
        for col, f in self.current_header_mapping.items():
            if f == 'PHONE':
                phone_col = col
            if f == 'EMAIL':
                email_col = col

        # fallback naive defaults
        cols = list(self.df_all.columns)
        if phone_col is None:
            phone_col = 'phone' if 'phone' in cols else cols[0]
        if email_col is None:
            email_col = 'email' if 'email' in cols else (cols[1] if len(cols) > 1 else cols[0])

        LOGGER.info('Starting duplicate detection (phone=%s email=%s)', phone_col, email_col)
        self.status_label.setText('Finding duplicates...')
        self.progress_bar.setValue(10)
        # run worker
        self.worker = DuplicateDetectWorker(self.df_all, phone_col, email_col)
        self.worker.finished.connect(self.on_duplicates_found)
        self.worker.start()

    def on_duplicates_found(self, unique_df, groups):
        if unique_df is None and isinstance(groups, dict) and groups.get('error'):
            QMessageBox.critical(self, 'Error', f"Duplicate detection failed: {groups.get('error')}")
            self.status_label.setText('Error')
            return
        self.status_label.setText('Duplicate detection complete')
        self.progress_bar.setValue(100)
        LOGGER.info('Duplicate detection complete: %d groups', len(groups))
        self.duplicate_groups = groups
        # update df_unique and show in merge review
        self.df_unique = unique_df
        self.populate_merge_table()

        # add duplicate_group id to df_all for display purposes
        try:
            if self.df_all is not None:
                # map index to group id
                idx_to_gid = {}
                for gid, members in groups.items():
                    for idx in members:
                        idx_to_gid[idx] = gid
                self.df_all['duplicate_group'] = self.df_all.index.map(lambda i: idx_to_gid.get(i))
                self.populate_table()
        except Exception:
            pass

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

    def export(self):
        QMessageBox.information(self, 'Export', 'Choose Export Unique or Export Duplicates')

    def export_unique(self):
        # Deprecated wrapper
        self.on_export_unique()

    def on_export_unique(self):
        if self.df_unique is None:
            QMessageBox.information(self, 'Export Unique', 'No unique data to export')
            return
        LOGGER.info('User requested export unique to %s', unique_path)
        try:
            ed = importlib.import_module('app.ui.dialogs.export_dialog')
            ExportDialog = getattr(ed, 'ExportDialog')
            dlg = ExportDialog(self)
            if dlg.exec_() != dlg.Accepted:
                return
            unique_path, dup_path = dlg.get_paths()
            if not unique_path:
                QMessageBox.information(self, 'Export', 'No path selected for unique export')
                return
            es = importlib.import_module('app.services.export_service')
            # export_unique_records raises on failure or existing file
            es.export_unique_records(self.df_unique, unique_path)
            QMessageBox.information(self, 'Export', f'Exported unique records to {unique_path}')
            LOGGER.info('Exported unique records to %s', unique_path)
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

    def run(self):
        app = QApplication.instance() or QApplication([])
        self.show()
        app.exec_()