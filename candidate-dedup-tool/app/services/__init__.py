from .header_detector import detect_headers, detect_headers_simple_map
from .excel_loader import load_excel_file, load_multiple_excel_files, load_folder_recursive
from .duplicate_detector import detect_duplicates, get_duplicate_group
from .normalizer import normalize_phone, normalize_email, normalize_text
# mapping storage helpers
from .mapping_storage import load_mappings, save_mappings, get_mapping_for_file
from .merge_service import merge_duplicate_group, auto_merge_all_groups