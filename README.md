# Clinic Manager - Phần mềm Quản lý Phòng khám Nhi

![Version](https://img.shields.io/badge/Version-5.0.3-blue.svg) ![Python](https://img.shields.io/badge/Python-3.10+-yellow.svg) ![PySide6](https://img.shields.io/badge/GUI-PySide6-green.svg)

Hệ thống quản lý phòng khám tư nhân hiện đại, ổn định, hỗ trợ đồng bộ Cloud và ứng dụng di động.

## ✨ Tính năng nổi bật (v5.0.3)

### 🏥 Quản lý Phòng khám Toàn diện
- **Hồ sơ bệnh nhân:** Lưu trữ lịch sử khám, đơn thuốc, tiền sử bệnh trọn đời.
- **Kê đơn thông minh:**
    - Gợi ý thuốc theo tên/hoạt chất.
    - Tính liều tự động theo cân nặng trẻ em.
    - In đơn thuốc chuyên nghiệp (A4/A5).
- **Kho thuốc:** Quản lý nhập/xuất/tồn, cảnh báo hết hạn.

### ☁️ Cloud Sync & Mobile (Đột phá)
- **Supabase Cloud:** Đồng bộ dữ liệu real-time lên đám mây, an toàn tuyệt đối.
- **ClinicViewer App:** Theo dõi phòng khám từ xa qua điện thoại Android.
- **One-Way Push Sync (New):**
    - Cơ chế **Local Master** đảm bảo dữ liệu tại máy tính là nguồn chuẩn duy nhất.
    - **Synchronous Delete:** Xóa dữ liệu trên máy tính → Xóa ngay lập tức trên Cloud & Mobile.
- **Auto Restore:** Tự động khôi phục dữ liệu về máy khi cài đặt lại phần mềm.

### 🛡️ Ổn định & Hiệu năng
- **Chống mất dữ liệu:** Cơ chế Queue thông minh, đảm bảo dữ liệu luôn được gửi đi ngay cả khi mạng chập chờn.
- **Fix Zombie Data:** Ngăn chặn triệt để tình trạng dữ liệu đã xóa tự động hồi sinh.
- **Auto-Update:** Tự động cập nhật cấu trúc dữ liệu cũ (Legacy Migration) mà không làm mất thông tin.

---

## 🚀 Cài đặt & Sử dụng

### Yêu cầu hệ thống
- **OS:** Windows 10/11 (64-bit)
- **RAM:** 4GB trở lên
- **Python:** 3.10+ (nếu chạy source code)

### 1. Chạy từ Source Code
Cài đặt thư viện:
```bash
pip install PySide6 pytz matplotlib supabase postgrest httpx openpyxl
```

Chạy ứng dụng:
```bash
python main_pyside.py
```

### 2. Đóng gói ra file .exe
Sử dụng PyInstaller (với đầy đủ hidden imports):
```bash
pyinstaller --noconfirm --name QuanLyPhongKhamv5.0.3 --windowed --icon=logo.ico --add-data "logo.ico;." --hidden-import pytz --hidden-import supabase --hidden-import postgrest --hidden-import httpx --hidden-import openpyxl main_pyside.py
```

---

## 🛠️ Cấu trúc dữ liệu

Ứng dụng sử dụng mô hình **Hybrid Database**:

1.  **Local (SQLite):** `clinic.db` - Lưu trữ chính, tốc độ cao, hoạt động Offline.
2.  **Cloud (Supabase/PostgreSQL):** Bản sao lưu & API cho Mobile App.

**Bảng chính:**
- `patients`: Thông tin hành chính & chẩn đoán.
- `medicines`: Danh mục thuốc & tồn kho.
- `prescriptions_header`: Đơn thuốc (Ngày, Bác sĩ, Tổng tiền).
- `prescription_details`: Chi tiết thuốc trong đơn.

---

## 📝 Changelog

### v5.0.3 (Stable) - 2026-02-07
- **Feature:** Sync Delete Đồng Bộ - Xóa dữ liệu an toàn tuyệt đối.
- **Fix:** Ngăn chặn Zombie Data (dữ liệu đã xóa tự hồi sinh).
- **Fix:** Sửa lỗi ID Conflict khi cài lại máy.

### v5.0.0 - 2026-02-06
- **Release:** Ra mắt phiên bản Cloud Sync & Mobile App Integration.

---

## 👤 Tác giả
**Nguyễn Duy Trường**
© 2026 Clinic Manager System. All Rights Reserved.
