# 🏥 Clinic Manager v5.0.5
### Hệ thống Quản lý Phòng khám Nhi - Cloud Sync Edition

![Version](https://img.shields.io/badge/Version-5.0.5-blue.svg?style=for-the-badge) ![Python](https://img.shields.io/badge/Python-3.12+-yellow.svg?style=for-the-badge) ![PySide6](https://img.shields.io/badge/UI-PySide6-green.svg?style=for-the-badge) ![License](https://img.shields.io/badge/License-Private-red.svg?style=for-the-badge)

**Clinic Manager** là giải pháp quản lý phòng khám hiện đại, được tối ưu cho các phòng khám Nhi khoa. Phiên bản **v5.0.5** mang đến sự ổn định tuyệt đối với cơ chế đồng bộ đám mây và khả năng quản lý dữ liệu linh hoạt.

---

## ✨ Tính năng nổi bật

### 🏥 Quản lý Chuyên môn
- **Hồ sơ điện tử:** Quản lý lịch sử khám, chẩn đoán và đơn thuốc chi tiết.
- **Kê đơn thông minh:** Tự động tính liều lượng thuốc dựa trên cân nặng của trẻ.
- **In đơn thuốc:** Hỗ trợ in đơn mẫu A4/A5 chuyên nghiệp.
- **Kho thuốc:** Theo dõi nhập/xuất/tồn kho và cảnh báo hạn sử dụng.

### ☁️ Công nghệ Đám mây (Cloud Sync)
- **Đồng bộ Real-time:** Dữ liệu tự động sao lưu lên Supabase Cloud.
- **ClinicViewer App:** Theo dõi doanh thu và danh sách bệnh nhân từ xa qua ứng dụng Android.
- **An toàn Tuyệt đối:** Cơ chế **Local Master** đảm bảo dữ liệu máy tính luôn là nguồn chuẩn. Mất máy tính không mất dữ liệu.
- **Xóa đồng bộ:** Xóa hồ sơ tại máy tính sẽ lập tức xóa trên Cloud và App Mobile, loại bỏ hoàn toàn "dữ liệu rác".

### 🛡️ Ổn định & Hiệu năng (Mới trong v5.0.5)
- **Fix Path Portability:** Tự động xử lý đường dẫn tuyệt đối cho Database và Cài đặt, đảm bảo app hoạt động ổn định bất kể vị trí chạy (Desktop, Shortcut hay thư mục cài đặt).
- **Settings Persistence:** Khắc phục triệt để lỗi không lưu được cài đặt khi chạy file thực thi duy nhất (One-file).
- **High-DPI Support:** Giao diện sắc nét trên mọi loại màn hình.
- **Dark/Light Mode:** Chế độ bảo vệ mắt hiện đại.

---

## 🚀 Hướng dẫn Cài đặt

### 🛠️ Yêu cầu Hệ thống
- **HĐH:** Ubuntu 22.04+ / Windows 10/11
- **Python:** 3.12+ (nếu chạy từ mã nguồn)

### 1. Chạy từ Mã nguồn
```bash
# Tạo môi trường ảo
python3 -m venv venv
source venv/bin/activate

# Cài đặt thư viện
pip install -r requirements.txt # Hoặc cài lẻ: PySide6 pytz supabase openpyxl matplotlib
```

Chạy ứng dụng:
```bash
python3 main_pyside.py
```

### 2. Đóng gói ứng dụng (Build Executable)

Sử dụng PyInstaller để tạo file thực thi duy nhất (`.exe` trên Windows hoặc binary trên Linux):

#### 🐧 Trên Linux (Ubuntu/Debian)
```bash
venv/bin/pyinstaller --noconfirm --name QuanLyPhongKhamv5.0.5 \
    --onefile --windowed --icon=logo.ico \
    --add-data "logo.ico:." \
    --hidden-import pytz --hidden-import supabase --hidden-import postgrest \
    --hidden-import httpx --hidden-import openpyxl main_pyside.py
```

#### 🪟 Trên Windows
```powershell
# Lưu ý: Dấu phân cách trong --add-data là dấu chấm phẩy (;)
venv\Scripts\pyinstaller --noconfirm --name QuanLyPhongKhamv5.0.5 `
    --onefile --windowed --icon=logo.ico `
    --add-data "logo.ico;." `
    --hidden-import pytz --hidden-import supabase --hidden-import postgrest `
    --hidden-import httpx --hidden-import openpyxl main_pyside.py
```

---

## 🛠️ Cấu trúc Dữ liệu
Dự án sử dụng mô hình **Hybrid Database**:
1. **Local (SQLite):** `clinic.db` - Tốc độ cao, hoạt động Offline.
2. **Cloud (Supabase/PostgreSQL):** Sao lưu động và cung cấp API cho App Mobile.

---

## 📝 Nhật ký Cập nhật (Changelog)

### v5.0.5 (Hiện tại) - 2026-02-24
- **Fix:** Xử lý triệt để lỗi đường dẫn `settings.json` khi chạy từ Shortcut hoặc Desktop.
- **Fix:** Đảm bảo lưu cài đặt thành công trong môi trường PyInstaller Single Executable.
- **Update:** Cấu hình tiền công khám mặc định mới: **120.000 VNĐ**.
- **Optimization:** Cải thiện tốc độ khởi động và đồng bộ ban đầu.

### v5.0.3 - 2026-02-07
- **Feature:** Sync Delete Đồng Bộ - Xóa dữ liệu an toàn tuyệt đối.
- **Fix:** Ngăn chặn Zombie Data (dữ liệu đã xóa tự hồi sinh).

---

## 👤 Thông tin Liên hệ
- **Tác giả:** Nguyễn Duy Trường
- **Email:** skul9x@gmail.com
- **Hotline:** 0388.634.123

© 2026 Clinic Manager System. All Rights Reserved.
