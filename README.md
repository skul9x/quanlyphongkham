# Clinic Manager - Phần mềm Quản lý Phòng khám Nhi

![Version](https://img.shields.io/badge/Version-5.0-blue.svg) ![Python](https://img.shields.io/badge/Python-3.10+-yellow.svg) ![PySide6](https://img.shields.io/badge/GUI-PySide6-green.svg)

Hệ thống quản lý phòng khám tư nhân nhẹ, hiện đại, tối ưu cho quy trình khám chữa bệnh Nhi khoa.

## ✨ Tính năng nổi bật (v5.0)

### 🏥 Quản lý Bệnh nhân & Khám chữa bệnh
- **Hồ sơ điện tử:** Lưu trữ thông tin hành chính, tiền sử bệnh, dị ứng.
- **Tách biệt Chẩn đoán & Đơn thuốc (Mới v4.4):** 
    - Quản lý chẩn đoán riêng biệt với đơn thuốc. 
    - Dữ liệu cũ tự động được nâng cấp (migration).
- **Lịch sử khám:** Xem lại toàn bộ lịch sử khám, đơn thuốc cũ của bệnh nhân.

### 💊 Quản lý Kho thuốc & Kê đơn
- **Kho thuốc thông minh:** Quản lý nhập/xuất, cảnh báo sắp hết hàng.
- **Kê đơn nhanh:** 
    - Tìm thuốc theo tên/hoạt chất.
    - Gợi ý liều dùng.
    - Tự động tính tiền và in đơn.
- **Tính liều tự động:** Công cụ tính liều dựa trên cân nặng/tuổi của trẻ.

### 📊 Báo cáo & Thống kê
- **Dashboard trực quan:** Biểu đồ doanh thu, lượt khám theo ngày/tháng.
- **Phân tích:** Thống kê mặt bệnh, nhóm tuổi bệnh nhân.

### ☁️ Cloud & Mobile (Mới v5.0)
- **Supabase Cloud Sync:** Đồng bộ dữ liệu an toàn lên đám mây, bảo vệ dữ liệu 24/7.
- **Android App Integration:** 
    - Kết nối với ứng dụng **ClinicViewer** trên Android.
    - Theo dõi danh sách bệnh nhân và doanh thu từ xa.
- **Splash Screen Chuyên nghiệp:**
    - Màn hình khởi động hiện đại, hiển thị tiến trình đồng bộ dữ liệu.
    - Tối ưu trải nghiệm người dùng, giúp ứng dụng khởi động mượt mà hơn.

---

## 🚀 Cài đặt & Chạy ứng dụng

### Yêu cầu hệ thống
- Python 3.10 trở lên
- Windows 10/11 (Khuyến nghị)

### 1. Cài đặt thư viện
Chạy lệnh sau trong terminal để cài các thư viện cần thiết:
```bash
pip install PySide6 pytz matplotlib
```

### 2. Chạy ứng dụng
```bash
python main_pyside.py
```

### 3. Đóng gói ra file .exe (Optional)
Sử dụng PyInstaller (xem lệnh chi tiết trong `dong goi.txt`):
```bash
pyinstaller --name QuanLyPhongKhamv5.0 --windowed --icon=logo.ico --add-data "logo.ico;." --hidden-import pytz main_pyside.py
```

---

## 🛠️ Cấu trúc dữ liệu (Database v4.4)

Ứng dụng sử dụng **SQLite** (`clinic.db`). Schema chính:

1.  **`patients`**: Thông tin bệnh nhân + Chẩn đoán mới nhất.
2.  **`medicines`**: Danh mục thuốc.
3.  **`prescriptions_header`**: Lưu thông tin chung của đơn thuốc (Ngày, Chẩn đoán, Tổng tiền).
4.  **`prescription_details`**: Lưu chi tiết từng loại thuốc trong đơn (Tên, SL, Giá).
5.  **`visits`**: (Legacy) Lịch sử lần khám cũ.

---

## 📝 Changelog

### v5.0 (Latest)
- **Cloud Sync:** Tích hợp đồng bộ dữ liệu với Supabase.
- **Mobile App:** Hỗ trợ kết nối với ứng dụng Android ClinicViewer.
- **UI Update:** Cập nhật thông tin phiên bản và giới thiệu.

### v4.4
- **Tách Database:** Tách `medical_history` thành bảng `prescriptions` riêng.
- **Migration:** Tool tự động migrate dữ liệu cũ sang cấu trúc mới an toàn.
- **UI:** Cập nhật giao diện Kê đơn và Xem chi tiết bệnh nhân.

### v4.3.3
- Fix lỗi hiển thị lịch sử.
- Cải thiện hiệu năng search.

---

## 👤 Tác giả
**Nguyễn Duy Trường**
© 2026 All Rights Reserved.
