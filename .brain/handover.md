━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 HANDOVER DOCUMENT - 2026-02-06
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 Trạng thái: **Dự án ổn định (v5.0.1)**
🔢 Đến bước: Hoàn tất các bản vá lỗi đồng bộ và tương thích dữ liệu.

✅ ĐÃ XONG TRONG SESSION NÀY:
   - **Version 5.0.1**: Nâng cấp phiên bản, cập nhật Cloud Sync Info, fix layout Help UI.
   - **Fix Prescription Display**: Xử lý lỗi đơn thuốc mới không hiện trong form cũ bằng logic "Double-Write" (Cập nhật đồng thời bảng mới và text legacy).
   - **Packaging Fix**: Cập nhật lệnh đóng gói PyInstaller (`dong goi.txt`) với các hidden-imports quan trọng (`postgrest`, `httpx`, `openpyxl`).
   - **Sync Reliability**: Triển khai pattern Commit-then-Sync, Simple Retry (3 lần), và Fix mutable state leak trong sync queue.
   - **DB Bug**: Fix lỗi duplicate INSERT khi thêm thuốc.

⏳ CÒN LẠI (Tồn đọng):
   - **Stress Test**: Test tắt mạng giữa chừng khi đang kê đơn để kiểm tra độ bền của Retry Mechanism.
   - **Performance**: Tối ưu tốc độ startup sync nếu danh sách bệnh nhân tăng lên con số hàng nghìn.
   - **Migration Cleanup**: (Tương lai) Chuyển đổi hoàn toàn form "Sửa Chẩn Đoán" sang dùng structured data thay vì text legacy.

🔧 QUYẾT ĐỊNH QUAN TRỌNG:
   - **Double-Write**: Chọn ghi dữ liệu vào 2 nơi để đảm bảo app mobile (ClinicViewer) và các form cũ trên desktop không bị hỏng dữ liệu hiển thị.
   - **Commit-then-Sync**: LUÔN commit database local trước khi đẩy dữ liệu vào queue sync để tránh mất dữ liệu nếu app crash sau khi insert cloud nhưng trước khi commit local.

⚠️ LƯU Ý CHO SESSION SAU:
   - File `dong goi.txt` hiện tại có lệnh build cho version `5.0.1`.
   - Nếu đóng gói gặp lỗi thiếu module, kiểm tra thêm trong `main_pyside.py` các import động.

📁 FILES QUAN TRỌNG:
   - `database.py`: Core logic xử lý DB và Sync Trigger.
   - `ui_prescription_window_pyside.py`: Nơi thực hiện Double-Write khi kê đơn.
   - `sync_manager.py`: Quản lý queue và retry logic.
   - `dong goi.txt`: Lệnh build app.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 Đã lưu! Để tiếp tục: Gõ /recap
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
