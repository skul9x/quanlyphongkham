# config.py
# Lưu trữ các hằng số cấu hình

DATABASE_NAME = 'clinic.db'
DEFAULT_PAGE_SIZE = 50
APP_VERSION = "5.0.1" # Cập nhật phiên bản
DEFAULT_APP_TITLE = "CLINIC MANAGER"
APP_TITLE = f"Phần mềm Quản lý Phòng khám Nhi v{APP_VERSION}"
APP_ICON = "logo.ico"

# Phí khám mặc định - ĐÃ SỬA THÀNH 100 THEO YÊU CẦU
CONSULTATION_FEE = 100 # Tiền công khám (VNĐ)

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
