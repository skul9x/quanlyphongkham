━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 HANDOVER DOCUMENT (v5.1.1)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 Đang làm: Hoàn tất Bộ lọc Kho Thuốc & Sửa lỗi hệ thống
🔢 Đến bước: Đã hoàn thiện mã nguồn, cập nhật tài liệu và test tay thành công.

✅ ĐÃ XONG:
   - **Tính năng Mới**: Bộ lọc Dropdown (Tất cả, Còn hàng, Sắp hết, Hết kho) tại màn hình Thuốc.
   - **Tương tác**: Biến Banner cảnh báo thành "Nút bấm" giúp lọc nhanh các thuốc báo động.
   - **Sửa lỗi Chí mạng**:
     - Fix crash khi xem đơn thuốc (do lỗi `sqlite3.Row` trên PySide).
     - Fix lỗi chặn kê đơn khi đã có chẩn đoán (ưu tiên đọc trường `diagnosis`).
   - **Tài liệu**: Cập nhật `CHANGELOG.md`, `BRIEF_Medicine_Filter.md`, `DESIGN_Medicine_Filter.md`.

⏳ CÒN LẠI:
   - Kiểm tra đóng gói `.deb` cho phiên bản mới `v5.1.1`.
   - Hướng dẫn nhân viên cách dùng bộ lọc mới để kiểm kho nhanh.

🔧 QUYẾT ĐỊNH QUAN TRỌNG:
   - Luôn ép kiểu `dict(row)` cho dữ liệu SQLite trước khi đưa vào UI để tránh `AttributeError`.
   - Giữ nguyên cơ chế Local-Only cho Inventory để bảo vệ cấu trúc Cloud.

⚠️ LƯU Ý CHO SESSION SAU:
   - Khi chạy ứng dụng, nếu thấy cảnh báo đỏ, hãy thử click trực tiếp vào đó để kiểm chứng độ nhạy của bộ lọc mới.
   - Nhớ kiểm tra kỹ các file trong thư mục `docs/` nếu cần bàn giao kỹ thuật.

📁 FILES QUAN TRỌNG:
   - `ui_medicine_pyside.py` (Lọc & Alert)
   - `ui_prescription_window_pyside.py` (Row fix)
   - `ui_patient_pyside.py` (Diagnosis logic)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 Đã lưu tất cả vào Bộ nhớ Vĩnh cửu! 
Để tiếp tục bất cứ lúc nào: Gõ /recap
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
