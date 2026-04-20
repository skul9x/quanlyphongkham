# Phần mềm Quản lý Phòng khám Nhi v5.2.0 🏥

Dự án phần mềm Quản lý Phòng khám Nhi chuyên biệt, được thiết kế để tối ưu hóa quy trình làm việc từ đón tiếp bệnh nhân, chẩn đoán, kê đơn thuốc và quản lý tồn kho. Ứng dụng tích hợp công nghệ đồng bộ đám mây (Cloud Sync) để bảo vệ an toàn dữ liệu và hỗ trợ vận hành trơn tru cả khi không có kết nối internet nội bộ mạng (offline-first).

---

## 💻 Công nghệ sử dụng
- **Ngôn ngữ**: Python 3.12+
- **Giao diện (UI)**: PySide6 (Qt for Python)
- **Cơ sở dữ liệu Local**: SQLite3
- **Cơ sở dữ liệu Đám mây (Cloud)**: Supabase
- **Đóng gói phần mềm**: PyInstaller
- **Công cụ hỗ trợ**: Xử lý đa luồng (Threading/QThread), Async Sync Manager

---

## ✨ Tính năng nổi bật
- **Quản lý bệnh nhân chuyên nghiệp**: Lưu trữ, theo dõi và tìm kiếm hồ sơ bệnh nhân nhanh chóng.
- **Kê đơn thuốc thông minh**: Tự động tính toán liều lượng cho nhi khoa, hỗ trợ in đơn thuốc.
- **Quản lý tồn kho thuốc**: Theo dõi số lượng thuốc, cảnh báo thông minh khi sắp hết hàng.
- **Đồng bộ đám mây (Supabase)**: Cơ chế đẩy dữ liệu một chiều (One-Way Push) lên Cloud, chạy ngầm giúp không làm ảnh hưởng trải nghiệm người dùng.
- **Báo cáo & Thống kê**: Báo cáo doanh thu, lượt khám và các loại thuốc sử dụng định kỳ.

---

## 🛠️ Hướng dẫn cài đặt

### 1. Yêu cầu hệ thống
- **Hệ điều hành**: Theo mặc định hỗ trợ tốt Linux (Ubuntu 24.04), đồng thời hỗ trợ đóng gói được trên Windows (.exe).
- **Môi trường**: Python 3.12+ cài đặt sẵn trên máy.

### 2. Cài đặt mã nguồn
Clone dự án về máy của bạn và cài đặt các phụ thuộc:
```bash
git clone https://github.com/skul9x/quanlyphongkham.git -b Supabase-v2
cd quanlyphongkham

# Tạo môi trường ảo
python3 -m venv venv
source venv/bin/activate

# Cài đặt thư viện
pip install -r requirements.txt
```

### 3. Cấu hình Supabase (Tùy chọn)
Chỉnh sửa cấu hình kết nối đám mây trong file `supabase_config.py` với `SUPABASE_URL` và `SUPABASE_KEY` riêng của phòng khám bạn nếu cần tự setup server mới, nếu không hệ thống sẽ dùng config mặc định.

---

## 🚀 Cách sử dụng

### Dùng trực tiếp bằng mã nguồn (Development Mode):
Mở terminal và kích hoạt môi trường ảo, sau đó chạy:
```bash
python main_pyside.py
```

### Đóng gói tiện lợi (Linux):
Nếu bạn muốn đóng gói thành file `.deb` để cài trực tiếp trên Ubuntu:
```bash
bash build_deb.sh
sudo dpkg -i quanlyphongkham_5.2_amd64.deb
```

---

## 📂 Cấu trúc thư mục

- `main_pyside.py`: File gốc khởi chạy toàn bộ ứng dụng.
- `database.py`: Xử lý giao tiếp các truy vấn dữ liệu cục bộ với SQLite3.
- `sync_manager.py`: Quản lý tác vụ chạy ngầm để đồng bộ bệnh nhân/thuốc lên Supabase.
- `config.py` & `supabase_config.py`: Các hằng số, thiết lập ứng dụng và key môi trường.
- `ui_*.py`: Các file cấu trúc giao diện tương ứng từng màn hình (Bệnh nhân, Thuốc, Cài đặt, Thống kê).
- `worker.py` / `animation_helper.py`: Modules giúp xử lý animation mượt mà và các Thread không bị đứng màn hình.
- `.brain/` & `plans/`: Thư mục chứa lưu trữ kiến thức ngữ cảnh và lộ trình cập nhật của dự án phần mềm.

---

## 📝 Bản quyền

Copyright 2026 Nguyễn Duy Trường
