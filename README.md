# Phần mềm Quản lý Phòng khám Nhi v5.1.2 🏥

Dự án phần mềm Quản lý Phòng khám Nhi chuyên biệt, được thiết kế để tối ưu hóa quy trình làm việc từ đón tiếp bệnh nhân, chẩn đoán, kê đơn thuốc và quản lý tồn kho. Ứng dụng tích hợp công nghệ đồng bộ đám mây (Cloud Sync) thông qua Supabase giúp bảo vệ an toàn cho dữ liệu.

---

## ✨ Tính năng nổi bật

- **Quản lý bệnh nhân chuyên nghiệp**: Lưu trữ và truy xuất hồ sơ bệnh nhân, lịch sử khám bệnh nhanh chóng bằng công nghệ tìm kiếm Indexed tự động.
- **Kê đơn thuốc thông minh**: Tự động tính toán liều lượng, hỗ trợ luồng làm việc liền mạch từ lúc khám chữa đến lúc in đơn thuốc.
- **Quản lý tồn kho thuốc**: Theo dõi số lượng thuốc thực tế, cảnh báo thông minh ngay khi thuốc sắp hết hoặc hết hàng để kịp thời nhập thay thế.
- **Đồng bộ Cloud Supabase**: Cơ chế đẩy dữ liệu một chiều (One-Way Push) từ máy cục bộ lên đám mây, với Async Background Worker giúp không làm chậm giao diện, hỗ trợ sao lưu phục hồi dữ liệu khi hỏng máy.
- **Báo cáo & Thống kê**: Kiểm soát biểu đồ lượng khách, doanh thu và các loại thuốc sử dụng đa số theo thời gian thực tế.
- **Giao diện hiện đại, mượt mà**: Ứng dụng công nghệ PySide6 (Qt for Python). Giao diện tối ưu, có Loading Overlay và Animated Components, chạy trơn tru trên cả nền tảng Linux/Ubuntu.

---

## 🛠️ Hướng dẫn cài đặt

### 1. Yêu cầu hệ thống
- **Hệ điều hành**: Linux (Ubuntu 24.04 được khuyến nghị), có thể tương thích Windows.
- **Ngôn ngữ & Môi trường**: Python 3.12 trở lên.

### 2. Cài đặt môi trường
Clone repository này về và cài đặt các thư viện liên quan:
```bash
git clone https://github.com/skul9x/quanlyphongkham.git -b Supabase-v2
cd quanlyphongkham

# Tạo môi trường ảo (Virtual Environment)
python3 -m venv venv
source venv/bin/activate

# Cài đặt toàn bộ package cần thiết
pip install -r requirements.txt
```

### 3. Cấu hình Supabase (Tùy chọn)
Mở file `supabase_config.py` và cập nhật thông số `SUPABASE_URL` cùng `SUPABASE_KEY` nếu bạn muốn tận dụng cơ sở dữ liệu lưu trữ sao lưu tự động.

---

## 🚀 Cách sử dụng

### Khởi chạy quá trình Development:
Mở terminal và gõ:
```bash
python main_pyside.py
```

### Đóng gói cho hệ điều hành Linux (.deb):
Dự án có đi kèm tập lệnh tự động hỗ trợ build package:
```bash
bash build_deb.sh
```
Sau đó, bạn cài đặt nó thẳng vào OS của bạn:
```bash
sudo dpkg -i deb_build.deb
```

---

## 📂 Cấu trúc thư mục

- `main_pyside.py`: Điểm khởi chạy của toàn bộ ứng dụng phần mềm.
- `database.py`: Lớp trừu tượng quản lý mọi truy vấn lưu trữ và thay đổi CSDL phía máy local (SQLite3).
- `sync_manager.py`: Điều phối vòng lặp luồng chạy ngầm để trao đổi dữ liệu tới Supabase mà không đóng băng màn hình chính.
- `ui_*.py`: Các modules cấu hình giao diện PySide6 (Ví dụ: Thống kê, Bệnh nhân, Nhập thuốc...).
- `worker.py` / `animation_helper.py` / `ux_components.py`: Các helper script giúp phần mềm chạy đa luồng và hoạt ảnh trở nên trơn tru.
- `.brain/`: Thư mục bảo toàn bộ não suy nghĩ và các notes phát triển kiến trúc dự án.
- `docs/` & `plans/`: Thư mục quản lý lộ trình lập trình phần mềm.

---

## 📝 Bản quyền

Copyright 2026 Nguyễn Duy Trường
Mọi quyền được bảo lưu.
