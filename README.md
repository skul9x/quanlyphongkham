# 🏥 Clinic Manager v5.1.1
### Hệ thống Quản lý Phòng khám Nhi - Seamless Workflow Edition

![Version](https://img.shields.io/badge/Version-5.1.1-blue.svg?style=for-the-badge) ![Python](https://img.shields.io/badge/Python-3.12+-yellow.svg?style=for-the-badge) ![PySide6](https://img.shields.io/badge/UI-PySide6-green.svg?style=for-the-badge) ![License](https://img.shields.io/badge/License-Private-red.svg?style=for-the-badge)

**Clinic Manager** là giải pháp quản lý phòng khám hiện đại, được tối ưu cho các phòng khám Nhi khoa. Phiên bản **v5.1.1** mang đến trải nghiệm làm việc **mượt mà không gián đoạn** với luồng "Thêm lượt khám → Kê đơn" được tối ưu hoàn toàn.

---

## ✨ Tính năng mới: Seamless Visit-to-Prescription Flow (v5.1.1) 🚀

Bác sĩ giờ đây có thể làm việc liên tục mà không bị gián đoạn:

- **Nút "LƯU & KÊ ĐƠN NGAY 💊":** Sau khi lưu lượt khám, cửa sổ kê đơn tự động mở ngay lập tức cho bệnh nhân vừa thêm.
- **Không còn popup thừa:** Loại bỏ các thông báo "Lưu thành công" gây gián đoạn quy trình làm việc.
- **Tự động focus:** Hệ thống tự động chọn đúng lượt khám vừa tạo trong danh sách.
- **Xử lý thông minh:** Sử dụng QTimer delay 100ms để đảm bảo UI cập nhật hoàn tất trước khi mở cửa sổ kê đơn.
- **Validation chặt chẽ:** Tự động kiểm tra chẩn đoán trước khi cho phép kê đơn.

---

## 🏥 Các tính năng cốt lõi

### 📋 Quản lý Chuyên môn
- **Hồ sơ điện tử:** Quản lý lịch sử khám, chẩn đoán (đa nguồn: DB field & Legacy text) và đơn thuốc chi tiết.
- **Kê đơn thông minh:** Tự động tính liều lượng thuốc dựa trên cân nặng của trẻ.
- **In đơn thuốc:** Hỗ trợ in đơn mẫu A4/A5 chuyên nghiệp, trình bày rõ ràng.
- **Luồng làm việc mượt mà:** Chuyển đổi liền mạch giữa các bước khám - chẩn đoán - kê đơn.

### 💊 Quản lý Kho thuốc Real-time (v5.1.0)
- **Cập nhật số lượng tức thời:** Số lượng tồn kho thay đổi ngay lập tức sau khi hoàn tất lưu đơn thuốc.
- **Cảnh báo tồn kho thấp:** Tự động hiển thị biểu tượng cảnh báo ⚠️ và đổi màu đỏ nếu thuốc sắp hết.
- **Kê đơn thông minh:** Hiển thị số dư tồn thực tế ngay trong bảng chọn thuốc.
- **Báo cáo Thống kê:** Theo dõi danh sách thuốc dùng nhiều nhất và doanh thu thuốc theo thời gian thực.
- **Bảo mật dữ liệu:** Hệ thống kho được duy trì local để đảm bảo tốc độ và riêng tư tuyệt đối.

### ☁️ Công nghệ Đám mây (Cloud Sync)
- **Đồng bộ Real-time:** Dữ liệu tự động sao lưu lên Supabase Cloud (ngoại trừ dữ liệu kho nội bộ).
- **ClinicViewer App:** Theo dõi doanh thu và danh sách bệnh nhân từ xa qua ứng dụng Android/Mobile.
- **An toàn Tuyệt đối:** Cơ chế **Local Master** đảm bảo dữ liệu máy tính luôn là nguồn chuẩn.

### 🎨 Giao diện Hiện đại
- **Modern UI:** Thiết kế giao diện đẹp mắt với PySide6, hỗ trợ Light/Dark mode.
- **Sidebar thu gọn:** Tối ưu không gian làm việc với sidebar có thể thu gọn.
- **Lazy Loading:** Tải các tab chỉ khi cần thiết, tăng tốc độ khởi động ứng dụng.
- **Splash Screen:** Màn hình chờ chuyên nghiệp với thanh tiến trình đồng bộ.

---

## 🚀 Hướng dẫn Cài đặt & Chạy

### 🛠️ Yêu cầu Hệ thống
- **HĐH:** Linux (Ubuntu/Debian) / Windows 10/11
- **Python:** 3.12+ (Khuyến khích dùng môi trường ảo `venv`)

### 📦 Chạy từ Mã nguồn
```bash
# Clone repository
git clone https://github.com/skul9x/quanlyphongkham.git
cd quanlyphongkham
git checkout Supabase-v2

# Tạo môi trường ảo và kích hoạt
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# Cài đặt thư viện
pip install -r requirements.txt

# Khởi chạy ứng dụng
python3 main_pyside.py
```

### 🔧 Cấu hình Supabase (Tùy chọn)
Nếu muốn sử dụng tính năng đồng bộ Cloud, tạo file `supabase_config.py`:
```python
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-key"
```

---

## 📁 Cấu trúc Dự án

```
quanlyphongkham-Supabase-v2/
├── main_pyside.py              # Entry point chính
├── config.py                   # Cấu hình ứng dụng
├── database.py                 # Logic database SQLite
├── sync_manager.py             # Quản lý đồng bộ Supabase
├── theme_manager_pyside.py     # Quản lý giao diện Light/Dark
├── ui_*.py                     # Các module giao diện
├── requirements.txt            # Dependencies Python
├── .brain/                     # Knowledge base & session state
├── plans/                      # Kế hoạch phát triển tính năng
└── scripts/                    # Utility scripts
```

---

## 📝 Nhật ký Cập nhật (Changelog)

### v5.1.1 (Hiện tại) - 2026-03-22
- **Feature:** Luồng "Thêm lượt khám → Kê đơn" mượt mà không gián đoạn (Seamless Flow).
- **Feature:** Nút "LƯU & KÊ ĐƠN NGAY 💊" tự động mở cửa sổ kê đơn sau khi lưu.
- **UX:** Loại bỏ popup thông báo thừa, tối ưu trải nghiệm làm việc liên tục.
- **Fix:** Sử dụng QTimer delay để đảm bảo UI cập nhật hoàn tất trước khi chuyển màn hình.

### v5.1.0 - 2026-03-11
- **Feature:** Hệ thống quản lý kho thuốc tích hợp (Real-time Inventory Tracking).
- **Feature:** Thống kê thuốc và doanh thu theo thời gian thực.
- **Fix:** Khắc phục lỗi kiểm tra chẩn đoán đa nguồn.
- **Fix:** Xử lý triệt để lỗi crash `AttributeError` khi đọc dữ liệu từ SQLite Row.

### v5.0.6 - 2026-02-28
- **Fix:** Sửa lỗi hiển thị chân chữ (g, y, p, q) trên môi trường Linux Ubuntu.
- **Update:** Tách biệt cửa sổ "Sửa Chẩn Đoán" để tối ưu quy trình nhập liệu nhanh.

### v5.0.3 - 2026-02-15
- **Feature:** Sync Delete đồng bộ - Xóa bệnh nhân chờ Cloud xóa xong.
- **Fix:** Dữ liệu đã xóa không còn tự động hồi sinh từ Cloud (Zombie Data).

### v5.0.0 - 2026-02-01
- **Feature:** Kết nối Cloud System (Supabase) với đồng bộ an toàn.
- **Feature:** Đồng bộ App Android (ClinicViewer).
- **Feature:** Splash Screen mới với trải nghiệm khởi động mượt mà.

---

## 🛠️ Công nghệ Sử dụng

- **Frontend:** PySide6 (Qt for Python)
- **Database:** SQLite (Local Master)
- **Cloud Sync:** Supabase (PostgreSQL)
- **Language:** Python 3.12+
- **Packaging:** PyInstaller (cho bản build standalone)

---

## 📚 Tài liệu Bổ sung

- [CHANGELOG.md](CHANGELOG.md) - Lịch sử cập nhật chi tiết
- [STRUCTURE.md](STRUCTURE.md) - Kiến trúc hệ thống
- [GUIDE_PACKAGING_GITHUB.md](GUIDE_PACKAGING_GITHUB.md) - Hướng dẫn đóng gói
- [.brain/](/.brain/) - Knowledge base & patterns

---

## 👤 Thông tin Liên hệ

- **Tác giả:** Nguyễn Duy Trường
- **Email:** skul9x@gmail.com
- **Hotline:** 0388.634.123
- **GitHub:** [@skul9x](https://github.com/skul9x)

---

## 📄 Bản quyền

Copyright © 2026 Nguyễn Duy Trường. All Rights Reserved.

Phần mềm này được phát triển cho mục đích sử dụng nội bộ tại các phòng khám Nhi khoa. Mọi hành vi sao chép, phân phối hoặc sử dụng cho mục đích thương mại mà không có sự cho phép bằng văn bản đều bị nghiêm cấm.
