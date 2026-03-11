━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 HANDOVER DOCUMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 Đang làm: Sửa lỗi luồng Kê đơn thuốc (Diagnosis Check & Stock Crash)
🔢 Đến bước: Đã hoàn thiện và test tay an toàn.

✅ ĐÃ XONG:
   - Sửa lỗi chặn kê đơn do cơ chế nhận diện chẩn đoán sai nguồn. Luôn tìm `diagnosis` field trước khi parse `medical_history`.
   - Bổ sung validation an toàn cho `sqlite3.Row` trên PySide UI: phải convert sang `dict(row)` trước khi dùng `get()`. Fix crash cho màn hình đơn thuốc.
   - Viết script migration an toàn tạo bảng/cột `stock_quantity`, `min_stock_level`.
   - Lưu lại kiến thức phòng tránh crash tương tự vào `.brain` / session.

⏳ CÒN LẠI:
   - Verify quá trình deploy (Packaging sang Ubuntu/Debian .deb) với SQLite mới (cột stock).
   - Có thể thêm Auto Unit Tests để bảo vệ luồng Kê Đơn nếu project scale lớn hơn.

🔧 QUYẾT ĐỊNH QUAN TRỌNG:
   - Local-Only Feature: Inventory tracking chỉ được maintain trong Local database, không map lên Supabase trừ khi có requirement rõ ràng.

⚠️ LƯU Ý CHO SESSION SAU:
   - Bất cứ UI Code nào kéo danh sách từ SQLite ở chế độ "row_factory", PHẢI cast thành `dict(row)` nếu cần dùng những method như get(), keys() để tránh `AttributeError`. 
   - Test tay với `/test` mode vẫn đáng tin nhất do thiếu Test Suite PySide.

📁 FILES QUAN TRỌNG:
   - ui_prescription_window_pyside.py (Sửa Row data fix)
   - ui_patient_pyside.py (Sửa Logic chẩn đoán)
   - .brain/brain.json (Lưu cấu trúc & gotcha)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 Đã lưu! Để tiếp tục: Gõ /recap
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
