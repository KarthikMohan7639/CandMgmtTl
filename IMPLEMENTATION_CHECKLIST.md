# CANDIDATE DEDUPLICATION TOOL - IMPLEMENTATION CHECKLIST

## UNDERSTANDING PHASE ✓
- [x] Read and understand requirements document
- [x] Reviewed 3 sample Excel files (Piping, Quality, Electrical)
- [x] Identified header variation patterns
- [x] Understood data flow and architecture
- [x] Reviewed key algorithms
- [x] Ready for code generation

---

## PHASE 1: PROJECT SETUP

### Git & Environment Setup
- [ ] Create GitHub repository: `candidate-dedup-tool`
- [ ] Clone repository locally
- [ ] Create Python 3.10+ virtual environment:
  ```bash
  python -m venv venv
  source venv/bin/activate  # Linux/Mac
  # or
  venv\Scripts\activate  # Windows
  ```
- [ ] Create `.gitignore` (Python template)
- [ ] Initialize requirements.txt

### Project Structure
- [ ] Create root directory structure (as in PROJECT_SUMMARY.md)
- [ ] Create all subdirectories: app/, app/ui/, app/services/, app/models/, etc.
- [ ] Create __init__.py files in all packages
- [ ] Create empty Python files for each module

### Configuration
- [ ] Create `config/app_settings.json` with default settings
- [ ] Create `config/header_mappings/` directory for storing mapping configs

---

## PHASE 2: CORE SERVICES (Business Logic)

Using copilot_prompts.txt, generate and implement:

### Data Models (app/models/)
- [ ] `candidate_record.py`
  - [ ] CandidateRecord dataclass
  - [ ] Type hints for all fields
  - [ ] from_dict() classmethod
  - [ ] to_dict() method
  - [ ] __eq__ method
  - [ ] Docstrings

- [ ] `duplicate_group.py`
  - [ ] DuplicateGroup dataclass
  - [ ] add_record() method
  - [ ] get_conflicting_fields() method
  - [ ] is_identical() method
  - [ ] Docstrings

- [ ] `merge_decision.py`
  - [ ] MergeDecision dataclass for storing merge rules

### Business Services (app/services/)

#### 1. Normalizer Service
- [ ] `normalizer.py`
  - [ ] normalize_phone(phone_str) → "9876543210"
    - [ ] Remove formatting characters
    - [ ] Remove country codes
    - [ ] Handle leading zeros
    - [ ] Unit tests (10+ test cases)
  
  - [ ] normalize_email(email_str) → "user@email.com"
    - [ ] Convert to lowercase
    - [ ] Trim whitespace
    - [ ] Unit tests (5+ test cases)
  
  - [ ] normalize_text(text_str) → "normalized text"
    - [ ] Trim whitespace

#### 2. Header Detection Service
- [ ] `header_detector.py`
  - [ ] HEADER_KEYWORDS dict with all field types
  - [ ] detect_headers(column_names) function
    - [ ] Fuzzy matching with difflib/fuzzywuzzy
    - [ ] 75% similarity threshold
    - [ ] Return column → field_type mapping
    - [ ] Case insensitivity
  - [ ] Unit tests with your 3 Excel file headers

#### 3. Excel Loading Service
- [ ] `excel_loader.py`
  - [ ] load_excel_file(filepath, sheet_name=0) → DataFrame
    - [ ] Use pandas.read_excel()
    - [ ] Error handling (FileNotFoundError, ValueError)
    - [ ] Return DataFrame
  
  - [ ] load_multiple_excel_files(filepaths) → DataFrame
    - [ ] Load each file
    - [ ] Add 'source_file' column
    - [ ] Concatenate all DataFrames
    - [ ] Reset index
  
  - [ ] load_folder_recursive(folder_path) → List[str]
    - [ ] Find all .xlsx and .xls files recursively

#### 4. Duplicate Detection Service
- [ ] `duplicate_detector.py`
  - [ ] detect_duplicates(df, phone_col, email_col, ...) → (unique_df, duplicate_groups)
    - [ ] Normalize phone/email columns
    - [ ] Group by normalized_phone
    - [ ] Group by normalized_email
    - [ ] Implement transitive closure
    - [ ] Handle empty phone/email correctly
    - [ ] Return unique records + duplicate groups dict
  
  - [ ] get_duplicate_group(group_id, duplicate_groups, df) → List[Dict]
    - [ ] Get all records in a specific group
  
  - [ ] Comprehensive unit tests
    - [ ] Same phone → grouped
    - [ ] Same email → grouped
    - [ ] Transitive closure (A-B-C)
    - [ ] Empty fields handled
    - [ ] Multiple unique records

#### 5. Merge Service
- [ ] `merge_service.py`
  - [ ] merge_duplicate_group(records, merge_decisions) → Dict
    - [ ] Apply merge strategies per field:
      - [ ] 'row_index' - use specific row's value
      - [ ] 'keep_same' - keep value (should be same)
      - [ ] 'most_recent' - use most recent by date
      - [ ] 'first_non_empty' - use first non-empty
      - [ ] 'concatenate' - combine all values
      - [ ] 'custom' - use user-provided value
    - [ ] Create merged record with merge_id
    - [ ] Track source_files and original_rows
  
  - [ ] auto_merge_all_groups(duplicate_groups, df) → (updated_df, merge_log)
    - [ ] Apply default merge strategies
    - [ ] Return updated DataFrame + merge decisions made
  
  - [ ] Unit tests for all merge strategies

#### 6. Export Service
- [ ] `export_service.py`
  - [ ] export_unique_records(df, output_filepath, sheet_name) → bool
    - [ ] Write to Excel using openpyxl
    - [ ] Format headers (bold, background)
    - [ ] Auto-fit column widths
    - [ ] Freeze header row
    - [ ] Error handling
  
  - [ ] export_duplicate_records(duplicate_groups, df, output_filepath) → bool
    - [ ] Include all original duplicate rows
    - [ ] Add duplicate group ID column
    - [ ] Format for easy review
    - [ ] Group related records visually

#### 7. Mapping Storage Service
- [ ] `mapping_storage.py`
  - [ ] save_mapping(mapping_config, filename) → bool
    - [ ] Save as JSON config file
  
  - [ ] load_mapping(filename) → Dict
    - [ ] Load saved mapping config
  
  - [ ] detect_mapping_from_filename(filename) → Optional[Dict]
    - [ ] Suggest mapping based on filename pattern

### Utilities
- [ ] `utils/constants.py`
  - [ ] APP_NAME, VERSION, etc.
  - [ ] PHONE_NORMALIZATION_RULES
  - [ ] EMAIL_REGEX, PHONE_REGEX
  - [ ] FIELD_TYPES enum

- [ ] `utils/validators.py`
  - [ ] is_valid_phone(phone) → bool
  - [ ] is_valid_email(email) → bool
  - [ ] validate_dataframe(df) → List[str] (warnings)

---

## PHASE 3: GUI COMPONENTS (PyQt5)

### Dialogs & Widgets
- [ ] `ui/dialogs/file_load_dialog.py`
  - [ ] File selection (single/multiple/folder)
  - [ ] Preview of first few rows
  - [ ] Column detection display

- [ ] `ui/dialogs/mapping_dialog.py`
  - [ ] Show all columns with detected types
  - [ ] Dropdowns to override detection
  - [ ] Preview of mapped data
  - [ ] Save/load mapping profiles
  - [ ] OK/Cancel buttons

- [ ] `ui/dialogs/export_dialog.py`
  - [ ] Choose save location
  - [ ] Choose filename
  - [ ] Confirm record counts
  - [ ] Include/exclude options

- [ ] `ui/widgets/data_table.py`
  - [ ] QTableWidget for displaying records
  - [ ] Search/filter functionality
  - [ ] Sort columns
  - [ ] Show record count

- [ ] `ui/widgets/duplicate_view.py`
  - [ ] List of duplicate groups
  - [ ] Expand group to see detail
  - [ ] Highlight matching values
  - [ ] Highlight conflicting values

- [ ] `ui/widgets/merge_dialog.py`
  - [ ] Show duplicate group details
  - [ ] Field-by-field merge strategy selection
  - [ ] Preview merged result
  - [ ] Confirm/Cancel

### Main Window
- [ ] `ui/main_window.py`
  - [ ] QMainWindow subclass
  - [ ] Menu bar (File, Tools, Help)
  - [ ] Toolbar with action buttons
  - [ ] Tabbed interface (QTabWidget)
    - [ ] Tab 1: "Loaded Data"
    - [ ] Tab 2: "Duplicates"
    - [ ] Tab 3: "Merge Review"
  - [ ] Status bar with counts
  - [ ] Wire all signals/slots
  - [ ] Use threading for long operations

---

## PHASE 4: APPLICATION ENTRY POINT

- [ ] `app/main.py`
  - [ ] QApplication initialization
  - [ ] MainWindow creation and display
  - [ ] Event loop execution
  - [ ] Make runnable: `python -m app.main`

---

## PHASE 5: TESTING

### Unit Tests
- [ ] `tests/test_normalizer.py`
  - [ ] 15+ test cases for phone normalization
  - [ ] 5+ test cases for email normalization
  - [ ] Edge cases (empty, null, whitespace)

- [ ] `tests/test_duplicate_detector.py`
  - [ ] Same phone detected
  - [ ] Same email detected
  - [ ] Transitive closure working
  - [ ] Empty fields handled
  - [ ] Multiple unique records

- [ ] `tests/test_merge_service.py`
  - [ ] Each merge strategy tested
  - [ ] Conflict resolution working
  - [ ] Merged record created correctly

### Integration Tests
- [ ] Load your 3 sample Excel files
- [ ] Verify headers auto-detected correctly
- [ ] Run duplicate detection
- [ ] Create a few merged records
- [ ] Export both datasets
- [ ] Verify output Excel files are valid

### Performance Tests
- [ ] Test with 10,000+ records
- [ ] Verify duplicate detection completes in <5 seconds
- [ ] Verify UI remains responsive
- [ ] Memory usage <500MB

---

## PHASE 6: DEPLOYMENT PREPARATION

- [ ] Create `requirements.txt`
  ```
  pandas>=2.0.0
  openpyxl>=3.10.0
  xlrd>=2.0.0
  PyQt5>=5.15.0
  fuzzywuzzy>=0.18.0
  python-Levenshtein>=0.21.0
  pytest>=7.0.0
  ```

- [ ] Create `setup.py` for package installation
- [ ] Create `README.md` with:
  - [ ] Project description
  - [ ] Installation instructions
  - [ ] Usage guide with screenshots (if possible)
  - [ ] Supported Excel file types
  - [ ] Example workflow

- [ ] Create `CHANGELOG.md`
- [ ] Add license (MIT recommended)
- [ ] Create `.gitignore` (Python template)

### PyInstaller Build
- [ ] Install PyInstaller: `pip install pyinstaller`
- [ ] Create executable:
  ```bash
  pyinstaller --onefile --windowed \
    --name CandidateDedupTool \
    --icon icon.ico \
    app/main.py
  ```
- [ ] Test standalone .exe on Windows
- [ ] Create distribution package

---

## QUALITY ASSURANCE

### Code Quality
- [ ] Type hints on all functions
- [ ] Docstrings on all public methods
- [ ] No hardcoded values (use constants.py)
- [ ] Error handling for all I/O operations
- [ ] Logging throughout app

### Functionality
- [ ] All FR-* requirements met
- [ ] All AC-* acceptance criteria pass
- [ ] No data loss scenarios
- [ ] Original files never overwritten
- [ ] Undo/revert functionality working

### User Experience
- [ ] Clear error messages
- [ ] Progress indicators for long operations
- [ ] Helpful tooltips
- [ ] Keyboard shortcuts (Ctrl+O, Ctrl+S, etc.)
- [ ] Responsive UI (no freezing)

### Documentation
- [ ] README.md complete
- [ ] API documentation (docstrings)
- [ ] User guide with examples
- [ ] Architecture diagram in repo
- [ ] Configuration guide

---

## FINAL VERIFICATION WITH YOUR DATA

Test with actual files:

### Test Case 1: Piping + Quality
- [ ] Load both files
- [ ] Headers detected correctly:
  - [ ] "Candidate Name" → NAME
  - [ ] "Contact No" vs "Mobile" → both PHONE
  - [ ] "Email Address" vs "Email ID" → both EMAIL
- [ ] Find common candidates
- [ ] Merge one duplicate group
- [ ] Export both datasets
- [ ] Verify exports contain correct data

### Test Case 2: All Three Files
- [ ] Load Piping + Quality + Electrical
- [ ] Auto-detect headers for all three
- [ ] Run duplicate detection
- [ ] Identify candidates appearing in multiple departments
- [ ] Merge several groups
- [ ] Export results
- [ ] Verify no data loss

### Test Case 3: Edge Cases
- [ ] Test with phone numbers having different formats
- [ ] Test with emails having different cases
- [ ] Test with missing/empty phone or email
- [ ] Test with large dataset (if you have one)
- [ ] Test with special characters in names

---

## DEPLOYMENT CHECKLIST

Before release:

- [ ] All tests passing (pytest)
- [ ] No linting errors (flake8/pylint optional)
- [ ] Performance verified (10k+ records in <5 seconds)
- [ ] Standalone executable tested
- [ ] README complete and accurate
- [ ] No hardcoded paths or credentials
- [ ] Git repository clean and well-organized
- [ ] Version number set (1.0.0)
- [ ] Changelog updated
- [ ] License included (MIT)

---

## POST-LAUNCH

### Future Enhancements (Phase 2)
- [ ] Partial name matching (advanced duplicate detection)
- [ ] Confidence scoring for merge suggestions
- [ ] Batch processing / scheduled runs
- [ ] Database backend for large-scale use
- [ ] Web UI alternative
- [ ] Email/phone validation and fixing
- [ ] Phone number geocoding
- [ ] Email domain typo detection

### Maintenance
- [ ] Monitor for bugs in production
- [ ] Collect user feedback
- [ ] Plan next version features
- [ ] Keep dependencies updated
- [ ] Add more keyboard shortcuts if needed
- [ ] Improve performance if bottlenecks found

---

## QUICK REFERENCE: COPILOT PROMPTS

When stuck, use copilot_prompts.txt in this order:

1. **Project Structure** - Create directory layout
2. **Data Models** - Create candidate_record.py, duplicate_group.py
3. **Normalizer** - Create phone/email normalization
4. **Header Detector** - Create fuzzy matching for headers
5. **Excel Loader** - Create file loading logic
6. **Duplicate Detector** - Create duplicate finding logic
7. **Merge Service** - Create merge conflict resolution
8. **Export Service** - Create Excel export
9. **Main GUI Window** - Create PyQt5 main window
10. **Unit Tests** - Generate tests for each service

Each prompt builds on previous ones, so follow order.

---

## ESTIMATED TIMELINE

| Phase | Task | Days | Status |
|-------|------|------|--------|
| 0 | Understanding & Planning | 0.5 | ✓ Complete |
| 1 | Project Setup & Structure | 1 | ⏳ To Do |
| 2 | Core Services (Business Logic) | 3-4 | ⏳ To Do |
| 3 | GUI Components (PyQt5) | 3-5 | ⏳ To Do |
| 4 | Entry Point & Integration | 0.5 | ⏳ To Do |
| 5 | Testing & QA | 2-3 | ⏳ To Do |
| 6 | Deployment & Packaging | 1 | ⏳ To Do |
| **TOTAL** | | **~10-14 days** | |

---

## SUCCESS CRITERIA

When complete, you should have:

✓ Desktop application that launches without terminal
✓ Load 3+ Excel files with different header formats
✓ Auto-detect and map headers (>80% accuracy)
✓ Find all duplicate candidates by phone/email
✓ Merge duplicates interactively (iOS-style)
✓ Export clean unique dataset + duplicate audit trail
✓ Handle 10k+ records without freezing
✓ Never overwrite original Excel files
✓ Fully type-hinted, documented code
✓ Deployable as standalone Windows executable

---

## SUPPORT RESOURCES

- requirements.txt - Complete specifications
- copilot_prompts.txt - Ready-to-use Copilot prompts
- PROJECT_SUMMARY.md - Quick start guide
- This checklist - Implementation tracking

Good luck! 🚀

Last Updated: December 09, 2024
Status: Ready for Implementation

