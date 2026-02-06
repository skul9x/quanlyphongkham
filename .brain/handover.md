━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 HANDOVER DOCUMENT - 2026-02-07
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 Trạng thái: **Dự án ổn định (v5.0.1)**
🔢 Đến bước: Hoàn tất Sửa lỗi logic, Merge Git và Chuẩn bị đóng gói.

✅ ĐÃ XONG TRONG SESSION NÀY:
3. **Double-Write Fix (Quan trọng):** Đã sửa logic "Double-Write" trong `save_prescription`. Thêm `{spec}` (đơn vị tính) vào chuỗi legacy text. 
   - *Kết quả:* App Mobile và Form cũ giờ sẽ hiển thị đầy đủ "x 10 Viên" thay vì "x 10".
   - *Kiểm chứng:* Đã pass Unit Test (`tests/quick_test_logic.py`).
4. **Git Strategy:**
   - Đã merge thành công lịch sử từ Remote.
   - Đã loại bỏ file `clinic.db` khỏi Git để tránh conflict binary và bảo mật dữ liệu.
   - Force Push lên nhánh `Supabase-v2` để đồng bộ.
   
✅ CÁC THAY ĐỔI TRƯỚC ĐÓ (v5.0.0 -> v5.0.1):
   - **Help UI**: Cập nhật thông tin Cloud Sync, sửa lỗi layout.
   - **Packaging**: Cập nhật lệnh PyInstaller (`dong goi.txt`) với hidden-imports (`postgrest`, `httpx`, `openpyxl`).
   - **Sync Stability**: Triển khai pattern Commit-then-Sync, Simple Retry.

⏳ CÒN LẠI (Tồn đọng):
   - **Đóng gói Final**: Chạy lệnh trong `dong goi.txt` để tạo file `.exe` cuối cùng cho khách hàng.
   - **Refactor Currency**: (Thấp) Thống nhất format tiền tệ để tránh lỗi hiển thị `.rstrip()` (ví dụ 500.50 -> 500.5).

🔧 QUYẾT ĐỊNH QUAN TRỌNG:
   - **Untrack DB**: Quyết định không track file Database trong Git để mỗi máy Dev/Prod có DB riêng, chỉ sync qua Supabase.
   - **Legacy Parsing Regex**: Logic parse chuỗi legacy trong `database.py` đã được kiểm tra và xác nhận tương thích với format mới có đơn vị tính.

⚠️ LƯU Ý CHO SESSION SAU:
   - Khi đóng gói, nhớ kiểm tra kỹ log của PyInstaller xem có warning `hidden-import` nào mới không.
   - File `config.py` đang để version `5.0.1`.

📁 FILES QUAN TRỌNG:
   - `ui_prescription_window_pyside.py`: Logic kê đơn (Double-Write).
   - `database.py`: Core logic xử lý DB và Sync Trigger (Legacy Parsing).
   - `.gitignore`: Cấu hình bỏ qua file DB.
   - `dong goi.txt`: Lệnh build app.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 Đã lưu! Để tiếp tục: Gõ /recap
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
