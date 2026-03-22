# Clinic Manager Desktop (v5.1.1+) 🏥

Phần mềm Quản lý Phòng khám Nhi chuyên nghiệp, được thiết kế để tối ưu hóa quy trình làm việc từ khâu đón tiếp bệnh nhân đến kê đơn và quản lý tồn kho. Ứng dụng tích hợp khả năng đồng bộ đám mây (Cloud Sync) giúp bảo vệ dữ liệu an toàn.

---

## ✨ Tính năng nổi bật

- **Quản lý bệnh nhân chuyên nghiệp**: Lưu trữ và truy xuất hồ sơ bệnh nhân nhanh chóng.
- **Kê đơn thuốc thông minh**: Tự động tính toán liều lượng, hỗ trợ luồng làm việc liền mạch từ lượt khám sang đơn thuốc.
- **Quản lý tồn kho thuốc (Local-Only)**: Theo dõi số lượng thuốc thực tế, cảnh báo ngay khi thuốc sắp hết hoặc hết kho để kịp thời nhập hàng.
- **Đồng bộ Cloud Supabase**: Cơ chế đẩy dữ liệu một chiều (One-Way Push) từ máy cục bộ lên đám mây để sao lưu và phục hồi dữ liệu khi cần.
- **Báo cáo & Thống kê**: Theo dõi doanh thu, số lượng bệnh nhân và các loại thuốc sử dụng nhiều nhất theo thời gian.
- **Giao diện hiện đại**: Sử dụng thư viện PySide6 (Qt for Python) mang lại trải nghiệm mượt mà, tối ưu cho cả Linux (Ubuntu 24).

---

## 🛠️ Hướng dẫn cài đặt

### 1. Yêu cầu hệ thống
- **Hệ điều hành**: Linux (Ubuntu 24 khuyến nghị), Windows.
- **Ngôn ngữ**: Python 3.12 trở lên.

### 2. Cài đặt môi trường
Clone repository và cài đặt các thư viện cần thiết:
```bash
git clone https://github.com/skul9x/quanlyphongkham.git -b Supabase-v2
cd quanlyphongkham

# Tạo môi trường ảo
python3 -m venv venv
source venv/bin/activate

# Cài đặt thư viện
pip install -r requirements.txt
```

### 3. Cấu hình Supabase
Cập nhật thông tin kết nối trong file `supabase_config.py` để sử dụng tính năng đồng bộ đám mây.

---

## 🚀 Cách sử dụng

### Chạy ứng dụng từ mã nguồn:
```bash
python main_pyside.py
```

### Đóng gói cho Linux (Ubuntu):
Nếu bạn muốn tạo file cài đặt `.deb`:
```bash
bash build_deb.sh
```
Sau đó cài đặt trực tiếp bằng lệnh:
```bash
sudo dpkg -i quanlyphongkham_5.1.1_amd64.deb
```

---

## 📂 Cấu trúc thư mục (Tóm tắt)

- `main_pyside.py`: Điểm khởi đầu của ứng dụng.
- `ui_*.py`: Các giao diện cửa sổ (Sử dụng PySide6).
- `database.py`: Quản lý các truy vấn SQLite cục bộ.
- `sync_manager.py`: Xử lý logic đồng bộ dữ liệu lên Supabase.
- `.brain/`: Thư mục lưu trữ kiến thức và lịch sử dự án.
- `docs/`: Chứa các tài liệu thiết kế và hướng dẫn chi tiết.

---

## 📝 Bản quyền

Copyright 2026 Nguyễn Duy Trường. 
Mọi quyền được bảo lưu. Liên hệ: [skul9x@gmail.com](mailto:skul9x@gmail.com)

---
*Dự án đang được phát triển tích cực bởi Nguyễn Duy Trường (Andru.ia Consultant).*
