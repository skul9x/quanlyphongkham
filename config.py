# config.py
# Lưu trữ các hằng số cấu hình
import os
import sys
import shutil

# APP_DIR: nơi chứa file thực thi + assets tĩnh (logo.ico) — READ ONLY khi đóng gói
if getattr(sys, 'frozen', False):
    _APP_DIR = os.path.dirname(sys.executable)
else:
    _APP_DIR = os.path.dirname(os.path.abspath(__file__))

# DATA_DIR: nơi chứa dữ liệu có thể ghi (clinic.db, settings.json)
# - Dev mode: cùng thư mục source code (không thay đổi behavior)
# - Frozen Linux (.deb): ~/.quanlyphongkham/ (vì /opt/ không cho ghi)
# - Frozen Windows (.exe): %APPDATA%/QuanLyPhongKham/
if getattr(sys, 'frozen', False):
    if sys.platform == 'win32':
        _DATA_DIR = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'QuanLyPhongKham')
    else:
        _DATA_DIR = os.path.join(os.path.expanduser('~'), '.quanlyphongkham')
    os.makedirs(_DATA_DIR, exist_ok=True)
else:
    _DATA_DIR = _APP_DIR  # Dev mode: cùng thư mục source

def _migrate_data_from_app_dir():
    """One-time migration: copy data files from old location (/opt/...) to new DATA_DIR."""
    if _DATA_DIR == _APP_DIR:
        return  # Dev mode or same dir, no migration needed
    
    files_to_migrate = ['clinic.db', 'settings.json']
    for filename in files_to_migrate:
        old_path = os.path.join(_APP_DIR, filename)
        new_path = os.path.join(_DATA_DIR, filename)
        if os.path.exists(old_path) and not os.path.exists(new_path):
            try:
                shutil.copy2(old_path, new_path)
                print(f"[MIGRATION] Copied {filename} from {_APP_DIR} to {_DATA_DIR}")
            except Exception as e:
                print(f"[MIGRATION] Failed to copy {filename}: {e}")

_migrate_data_from_app_dir()

DATABASE_NAME = os.path.join(_DATA_DIR, 'clinic.db')
_database_path_override = None

def set_database_path(path):
    """Set the database path before initializing the database."""
    global _database_path_override
    # Normalize: strip whitespace, convert empty/whitespace-only to None
    _database_path_override = path.strip() if path and path.strip() else None

def get_database_path_override():
    """Returns the raw override path, or empty string if using default.
    Used by save_settings() to distinguish 'custom path' vs 'default'.
    """
    return _database_path_override or ""

def get_database_path():
    """Returns the current database path (override or default)."""
    if _database_path_override:
        return _database_path_override
    return DATABASE_NAME

DEFAULT_PAGE_SIZE = 50
APP_VERSION = "5.2" # Database Path & Packaging Stabilization
DEFAULT_APP_TITLE = "CLINIC MANAGER"
APP_TITLE = f"Phần mềm Quản lý Phòng khám Nhi v{APP_VERSION}"
APP_ICON = os.path.join(_APP_DIR, "logo.ico")

# Phí khám mặc định - CÓ THỂ ĐIỀU CHỈNH TRONG RUNTIME
_consultation_fee_override = None

def set_consultation_fee(fee):
    """Set the consultation fee override."""
    global _consultation_fee_override
    _consultation_fee_override = float(fee) if fee is not None else None

def get_consultation_fee():
    """Returns the consultation fee (override or default 100)."""
    if _consultation_fee_override is not None:
        return _consultation_fee_override
    return 120.0 # Tiền công khám mặc định (VNĐ)

# Cấu hình múi giờ
TIMEZONE = 'Asia/Ho_Chi_Minh'

# Các nhóm tuổi cho thống kê
AGE_GROUPS_STATS = {
    "0 - 2 tháng tuổi": (0, 60),
    "2 - 6 tháng tuổi": (60, 180),
    "6 tháng - 2 tuổi": (180, 730),
    "2 - 6 tuổi": (730, 2190),
    "6 - 16 tuổi": (2190, 5840),
    "Người lớn": (5840, float('inf')),
    "Không xác định": None
}

# Cấu hình tìm kiếm bệnh nhân
SEARCH_PLACEHOLDER = "Nhấn Ctrl + F để tìm kiếm theo tên hoặc số điện thoại..."

# Cấu hình cửa sổ kê đơn
MEDICINE_SEARCH_DELAY = 300 # ms
MEDICINE_SEARCH_MIN_LEN = 2 # Số ký tự tối thiểu để bắt đầu tìm thuốc

# Thêm các biến cấu hình mới
DOCTOR_NAME = "BS. Nguyễn Duy Trường"
CLINIC_NAME = "Phòng khám Nhi khoa"
