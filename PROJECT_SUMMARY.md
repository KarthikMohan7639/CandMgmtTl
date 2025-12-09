# ============================================================================
# CANDIDATE DEDUPLICATION TOOL - PROJECT SUMMARY & QUICK START
# ============================================================================

**Project Name:** Candidate Data Management & Deduplication Tool

**Version:** 1.0.0

**Purpose:** Consolidate and deduplicate candidate records from multiple 
Excel files (department-specific recruitment data) by identifying duplicates 
via phone/email and merging them interactively.

**Status:** Ready for GitHub Copilot Code Generation

---

## YOUR REQUIREMENTS (Summarized)

✓ **Problem:** Multiple Excel files (Piping Design, Quality Manager, 
  Electrical Engineering) with same candidates appearing multiple times due 
  to repeated recruiting contact

✓ **Solution:** Build a desktop tool that:
  1. Loads multiple Excel files with varying column headers
  2. Auto-detects and maps column types (Name, Phone, Email, Designation, etc.)
  3. Identifies duplicates based on phone number AND email address
  4. Allows interactive merging (iOS Photos-style interface)
  5. Exports clean "unique" and "duplicates" datasets

✓ **Expected Duplicate Scenario:**
  - Same person appears in Piping file with "Contact No" = "9876543210"
  - Same person appears in Quality file with "Mobile" = "9876543210"
  → System detects duplicate and suggests merge
  → User confirms merge, creating single consolidated record

✓ **Expected Outcome:**
  - `unique_candidates.xlsx` - All unique records + merged consolidated records
  - `duplicate_records.xlsx` - All original duplicate rows (before merge)

---

## KEY FEATURES IMPLEMENTED

### 1. Multi-File Excel Loading
- Load 1+ Excel files at once
- Support .xlsx and .xls formats
- Combine into single dataset with source tracking

### 2. Smart Header Detection
Uses fuzzy string matching to automatically detect:
- NAME fields: "Name", "Candidate Name", "Applicant Name", "Full Name"
- PHONE fields: "Phone", "Contact", "Contact No", "Mobile", "Mobile No"
- EMAIL fields: "Email", "Email ID", "Email Address"
- DESIGNATION fields: "Designation", "Role", "Position", "Job Title"
- DEPARTMENT fields: "Department", "Domain", "Function"
- DATE fields: "Date", "Contact Date", "Application Date"

User can manually override auto-detection via mapping dialog.

### 3. Intelligent Data Normalization
**Phone Normalization:**
- Remove all formatting: spaces, dashes, parentheses, dots, slashes
- Remove country codes: +91, 0091, 001
- Convert to 10-digit format (India standard)
- Handle empty values correctly

**Email Normalization:**
- Convert to lowercase
- Trim whitespace
- Handle empty values correctly

### 4. Duplicate Detection Engine
- Identifies records with matching phone OR matching email
- Transitive grouping: If A matches B, and B matches C, group all three
- Handles empty phone/email gracefully (no false matches)
- Creates unique group IDs for each duplicate set

### 5. Interactive Merge Interface
- Show all records in a duplicate group
- Highlight conflicting field values
- User chooses per-field merge strategy:
  * Use value from Row 1/2/3
  * Use most recent (by date)
  * Concatenate all values
  * Enter custom value
- Auto-merge option with sensible defaults

### 6. Clean Data Export
- **Unique Dataset:** Original unique records + merged consolidated records
- **Duplicate Dataset:** All original duplicate rows (before merging)
- Both exported to separate Excel files with proper formatting

---

## TECH STACK

**Language:** Python 3.10+

**Core Libraries:**
- `pandas` - Excel reading/writing, data manipulation
- `openpyxl` - Advanced Excel file handling
- `PyQt5` - Desktop GUI framework
- `fuzzywuzzy` - Fuzzy string matching for headers
- `difflib` - Built-in fuzzy matching (alternative)

**Packaging:**
- `PyInstaller` - Create standalone .exe for Windows

**Testing:**
- `pytest` - Unit tests

---

## PROJECT STRUCTURE

```
candidate-dedup-tool/
│
├── README.md                          ← User guide
├── requirements.txt                   ← Python dependencies
├── setup.py                          ← Package setup
│
├── app/
│   ├── main.py                       ← Entry point (python -m app.main)
│   │
│   ├── ui/                           ← GUI Components
│   │   ├── main_window.py            ← Main application window
│   │   ├── widgets/
│   │   │   ├── data_table.py         ← Reusable table widget
│   │   │   ├── duplicate_view.py     ← Duplicate group display
│   │   │   └── merge_dialog.py       ← Interactive merge UI
│   │   └── dialogs/
│   │       ├── file_load_dialog.py   ← File selection
│   │       ├── mapping_dialog.py     ← Header mapping
│   │       └── export_dialog.py      ← Export options
│   │
│   ├── services/                     ← Business Logic
│   │   ├── excel_loader.py           ← Load Excel files
│   │   ├── header_detector.py        ← Fuzzy match headers
│   │   ├── normalizer.py             ← Phone/email normalization
│   │   ├── duplicate_detector.py     ← Find duplicate groups
│   │   ├── merge_service.py          ← Merge conflict resolution
│   │   ├── export_service.py         ← Export to Excel
│   │   └── mapping_storage.py        ← Save/load mapping configs
│   │
│   ├── models/                       ← Data Models
│   │   ├── candidate_record.py       ← Single candidate record
│   │   ├── duplicate_group.py        ← Group of duplicates
│   │   └── merge_decision.py         ← Merge rules
│   │
│   └── utils/                        ← Utilities
│       ├── constants.py              ← App constants
│       └── validators.py             ← Input validation
│
├── tests/                            ← Unit Tests
│   ├── test_normalizer.py
│   ├── test_duplicate_detector.py
│   ├── test_merge_service.py
│   └── fixtures/
│       └── sample_data.xlsx
│
└── config/                           ← Configuration
    ├── app_settings.json
    └── header_mappings/              ← Saved mapping profiles
        ├── piping_designer.json
        ├── quality_manager.json
        └── electrical_eng.json
```

---

## WORKFLOW (User Perspective)

```
START
  ↓
[1] Click "Load Files" button
  ├─ Select Piping-Designer-ONG.xlsx
  ├─ Select Quality-Project-Manager_GMO_QAN-OR-QAG.xlsx
  ├─ Select Elec-Eng-ONG.xlsx
  ↓
[2] For each file, auto-detect headers
  ├─ Piping: "Contact No" → PHONE ✓, "Candidate Name" → NAME ✓, ...
  ├─ Quality: "Mobile" → PHONE ✓, "Email ID" → EMAIL ✓, ...
  ├─ Elec: "Phone" → PHONE ✓, "Email Address" → EMAIL ✓, ...
  ↓
[3] User reviews mappings (can override if needed)
  ↓
[4] Click "Find Duplicates"
  ├─ System normalizes phone/email
  ├─ Detects: "Rajesh Kumar" appears in Piping AND Quality
  ├─ Groups: DUP-001 (2 records, same phone + email)
  ↓
[5] User clicks "Merge" on duplicate group
  ├─ Merge dialog shows conflicting fields
  ├─ For each field:
  │   - Name: (same in both) use "Rajesh Kumar"
  │   - Phone: (same in both) use "9876543210"
  │   - Email: (same in both) use "rajesh@email.com"
  │   - Role: CONFLICT: "Senior Piping Engineer" vs "Quality Manager"
  │     → User chooses "Quality Manager" (more recent date)
  │   - Contact Date: Range from 2024-11-15 to 2024-12-05
  │     → Auto-select most recent: 2024-12-05
  ↓
[6] User clicks "Confirm Merge"
  ├─ Consolidated record created: MERGED-0001
  ├─ Status updated to "merged"
  ↓
[7] User clicks "Export Unique"
  ├─ Saves: unique_candidates_2024-12-09.xlsx
  │   Contains: All original unique records + merged MERGED-0001
  ↓
[8] User clicks "Export Duplicates"
  ├─ Saves: duplicate_records_2024-12-09.xlsx
  │   Contains: Original rows from Piping and Quality files
  │   (marked as "merged" with reference to MERGED-0001)
  ↓
END - Ready to import clean data to HR system
```

---

## DOCUMENTS PROVIDED

You now have 3 comprehensive documents:

### 1. requirements.txt (Specifications Document)
**What it is:** Detailed project requirements in standard format
**Where to use:** 
- Reference when building the application
- Share with team for clarity
- Use as spec for GitHub Copilot
- Basis for testing/acceptance criteria

**Key sections:**
- Functional requirements (FR-1 through FR-8)
- Non-functional requirements (NR-1 through NR-5)
- Example scenarios from your actual use case
- Acceptance criteria

### 2. copilot_prompts.txt (GitHub Copilot Instructions)
**What it is:** 14 ready-to-use prompts for Copilot code generation
**How to use:**
1. Open GitHub Copilot in VS Code
2. Copy one prompt at a time
3. Paste into Copilot chat
4. Wait for code generation
5. Review and commit to repo

**Covers:** Structure, models, services, UI, tests, deployment

### 3. This Summary Document
**What it is:** Quick reference guide
**Includes:**
- Your requirements summary
- Tech stack overview
- Project structure diagram
- Example workflow
- Quick start instructions

---

## NEXT STEPS - IMPLEMENTATION ROADMAP

### Phase 1: Core Services (No UI yet)
✓ Create project structure
✓ Implement normalizer.py (phone/email normalization)
✓ Implement header_detector.py (fuzzy matching)
✓ Implement excel_loader.py (load Excel files)
✓ Implement duplicate_detector.py (find groups)
✓ Implement merge_service.py (merge logic)
✓ Unit test each service

**Estimated time:** 2-3 days

### Phase 2: GUI
✓ Create main_window.py (PyQt5)
✓ Create data_table.py widget
✓ Create file_load_dialog.py
✓ Create mapping_dialog.py
✓ Create duplicate_view.py
✓ Create merge_dialog.py
✓ Create export_dialog.py
✓ Wire all components together

**Estimated time:** 3-5 days

### Phase 3: Testing & Polish
✓ Test with your 3 sample files (Piping, Quality, Electrical)
✓ Test with 10k+ records
✓ Add export_service.py (Excel export)
✓ Polish UI, add tooltips
✓ Create user documentation

**Estimated time:** 2-3 days

### Phase 4: Deployment
✓ Create requirements.txt
✓ Create setup.py
✓ Package with PyInstaller
✓ Create standalone .exe for Windows
✓ Create distribution package

**Estimated time:** 1 day

**Total Estimated Time:** ~8-12 days for complete implementation

---

## QUICK START COMMAND

After generating code with Copilot:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python -m app.main

# Or create standalone Windows executable
pyinstaller --onefile --windowed app/main.py -n CandidateDedupTool
```

---

## TESTING YOUR THREE FILES

When complete, test with:
1. `Piping-Desinger-ONG.xlsx` - Verify "Contact No" → PHONE mapping
2. `Quality-Project-Manager_GMO_QAN-OR-QAG.xlsx` - Verify "Mobile" → PHONE mapping
3. `Elec-Eng-ONG.xlsx` - Verify "Email Address" → EMAIL mapping

Expected output:
- System detects all headers automatically
- Finds duplicates (if any) across files
- Successfully merges and exports results
- No data corruption in output files

---

## IMPORTANT NOTES

### For GitHub Copilot Effectiveness:
1. **Be specific** - Use prompts from copilot_prompts.txt
2. **Provide examples** - The 3 Excel files show real header variations
3. **Ask for tests** - Request unit tests for each service
4. **Review generated code** - Check for edge cases and error handling
5. **Iterate** - Ask Copilot to improve/refactor if needed

### For Your Requirements:
1. **Header mapping** - Most critical feature (handles variation across files)
2. **Phone normalization** - Must strip country codes, formatting
3. **Email normalization** - Case-insensitive matching
4. **Transitive grouping** - A→B→C must group together
5. **Never overwrite** - Original Excel files must be untouched

### Known Complexities:
- Phone numbers may have country codes (+91) that need stripping
- Email addresses might have typos (but tool doesn't fix them)
- Some candidates may have incomplete phone or email (handle gracefully)
- Merge decisions are user-driven (not auto, except auto-merge option)
- Large datasets (10k+ records) need background threading

---

## SUPPORT & TROUBLESHOOTING

**If headers not detected:**
- Check HEADER_KEYWORDS dict in header_detector.py
- Verify fuzzy matching threshold (75% recommended)
- Ask Copilot to add more keyword variations

**If duplicates missed:**
- Verify normalizer.py removes all formatting
- Check if phone has country code (+91) - ensure it's stripped
- Verify transitive grouping logic in duplicate_detector.py

**If merge fails:**
- Check field types in merge_decisions dict
- Verify date format handling (YYYY-MM-DD)
- Ensure no None/null values breaking logic

**If export corrupted:**
- Use openpyxl for Excel writing (more reliable)
- Verify column names are preserved
- Check file isn't open in Excel during export

---

## GITHUB SETUP RECOMMENDATIONS

```
Repository: candidate-dedup-tool
License: MIT
Structure:
├── main branch - production code
├── develop branch - development
├── feature/header-detection
├── feature/duplicate-detection
├── feature/merge-ui
└── feature/export-service

Branches can be merged in order after testing.
```

---

## FINAL CHECKLIST BEFORE CODING

- [ ] Read entire requirements.txt document
- [ ] Understand the 3 Excel file variations
- [ ] Identify your 3 sample files as test data
- [ ] Set up Git repository
- [ ] Create virtual environment for Python
- [ ] Review copilot_prompts.txt order
- [ ] Have GitHub Copilot ready in VS Code
- [ ] Plan for ~10 days of implementation
- [ ] Identify backup phone/email fields (if any)
- [ ] Decide on "most recent" logic (how to detect newest record)

---

## YOU'RE READY!

All the information, specifications, and code generation prompts are ready.

**Next:** Open GitHub Copilot and start with Prompt 1 (Project Structure Setup) 
from copilot_prompts.txt

**Result:** A production-ready candidate deduplication tool tailored to your 
recruitment data management needs.

Good luck! 🚀

---

Generated: December 09, 2024
For: Candidate Data Management & Deduplication Tool
Based on: 3 actual Excel files (Piping Design, Quality Manager, Electrical Engineering)

