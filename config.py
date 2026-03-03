# config.py
# Lưu trữ các hằng số cấu hình
import os
import sys

# PyInstaller --onefile: __file__ points to temp dir, sys.executable points to real app location
if getattr(sys, 'frozen', False):
    _APP_DIR = os.path.dirname(sys.executable)
else:
    _APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_NAME = '/home/skul9x/Desktop/Onedrive/Music/QuanLyPhongKhamv5.0.4/clinic.db'
_database_path_override = None

def set_database_path(path):
    """Set the database path before initializing the database."""
    global _database_path_override
    _database_path_override = path

def get_database_path():
    """Returns the current database path (override or default)."""
    if _database_path_override:
        return _database_path_override
    return DATABASE_NAME

DEFAULT_PAGE_SIZE = 50
APP_VERSION = "5.0.6" # Sync Delete: ensure Cloud updated on delete
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
