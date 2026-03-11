# 🏥 Clinic Manager v5.1.0
### Hệ thống Quản lý Phòng khám Nhi - Inventory & Cloud Sync Edition

![Version](https://img.shields.io/badge/Version-5.1.0-blue.svg?style=for-the-badge) ![Python](https://img.shields.io/badge/Python-3.12+-yellow.svg?style=for-the-badge) ![PySide6](https://img.shields.io/badge/UI-PySide6-green.svg?style=for-the-badge) ![License](https://img.shields.io/badge/License-Private-red.svg?style=for-the-badge)

**Clinic Manager** là giải pháp quản lý phòng khám hiện đại, được tối ưu cho các phòng khám Nhi khoa. Phiên bản **v5.1.0** đánh dấu bước tiến lớn với hệ thống **Quản lý kho thuốc Real-time**, giúp bác sĩ kiểm soát hoàn hảo lượng thuốc tồn kho ngay trong lúc kê đơn.

---

## ✨ Tính năng mới: Quản lý Kho thuốc Real-time (v5.1.0) 💊

Hệ thống kho được tích hợp sâu vào quy trình khám chữa bệnh hàng ngày:

- **Cập nhật số lượng tức thời:** Số lượng tồn kho thay đổi ngay lập tức sau khi hoàn tất lưu đơn thuốc.
- **Cảnh báo tồn kho thấp (Low Stock Alert):** Tự động hiển thị biểu tượng cảnh báo ⚠️ và đổi màu đỏ nếu thuốc sắp hết hoặc đã hết hàng.
- **Kê đơn thông minh:** Hiển thị số dư tồn thực tế ngay trong bảng chọn thuốc để bác sĩ đưa ra quyết định kê đơn chính xác nhất.
- **Báo cáo Thống kê:** Theo dõi danh sách thuốc dùng nhiều nhất và doanh thu thuốc theo thời gian thực.
- **Bảo mật dữ liệu:** Hệ thống kho được duy trì local để đảm bảo tốc độ phản hồi nhanh nhất và sự riêng tư tuyệt đối (Local-Only Inventory Tracking).

---

## 🏥 Các tính năng cốt lõi

### 📋 Quản lý Chuyên môn
- **Hồ sơ điện tử:** Quản lý lịch sử khám, chẩn đoán (đa nguồn: DB field & Legacy text) và đơn thuốc chi tiết.
- **Kê đơn thông minh:** Tự động tính liều lượng thuốc dựa trên cân nặng của trẻ.
- **In đơn thuốc:** Hỗ trợ in đơn mẫu A4/A5 chuyên nghiệp, trình bày rõ ràng.

### ☁️ Công nghệ Đám mây (Cloud Sync)
- **Đồng bộ Real-time:** Dữ liệu tự động sao lưu lên Supabase Cloud (ngoại trừ dữ liệu kho nội bộ).
- **ClinicViewer App:** Theo dõi doanh thu và danh sách bệnh nhân từ xa qua ứng dụng Android/Mobile.
- **An toàn Tuyệt đối:** Cơ chế **Local Master** đảm bảo dữ liệu máy tính luôn là nguồn chuẩn. Mất máy tính có thể khôi phục lại từ Cloud.

---

## 🚀 Hướng dẫn Cài đặt & Chạy

### 🛠️ Yêu cầu Hệ thống
- **HĐH:** Linux (Ubuntu/Debian) / Windows 10/11
- **Python:** 3.12+ (Khuyến khích dùng môi trường ảo `venv`)

### 📦 Chạy từ Mã nguồn
```bash
# Tạo môi trường ảo và kích hoạt
python3 -m venv venv
source venv/bin/activate  # Linux
# venv\Scripts\activate  # Windows

# Cài đặt thư viện
pip install -r requirements.txt

# Khởi chạy ứng dụng
python3 main_pyside.py
```

---

## 📝 Nhật ký Cập nhật (Changelog)

### v5.1.0 (Hiện tại) - 2026-03-11
- **Feature:** Hệ thống quản lý kho thuốc tích hợp (Real-time Inventory Tracking).
- **Feature:** Thống kê thuốc và doanh thu theo thời gian thực.
- **Fix:** Khắc phục lỗi kiểm tra chẩn đoán đa nguồn (hỗ trợ cả cột `diagnosis` mới và `medical_history` cũ).
- **Fix:** Xử lý triệt để lỗi crash `AttributeError` khi đọc dữ liệu từ SQLite Row.
- **Update:** Tối ưu hóa UI bảng chọn thuốc với các chỉ báo màu sắc cho tồn kho.

### v5.0.6 - 2026-02-28
- **Fix:** Sửa lỗi hiển thị chân chữ (g, y, p, q) trên môi trường Linux Ubuntu.
- **Update:** Tách biệt cửa sổ "Sửa Chẩn Đoán" để tối ưu quy trình nhập liệu nhanh.

---

## 👤 Thông tin Liên hệ
- **Tác giả:** Nguyễn Duy Trường
- **Email:** skul9x@gmail.com
- **Hotline:** 0388.634.123

© 2026 Clinic Manager System. All Rights Reserved.
