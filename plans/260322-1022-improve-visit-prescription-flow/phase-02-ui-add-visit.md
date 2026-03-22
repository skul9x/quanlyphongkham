# Phase 02: Update Add Visit UI
Status: ✅ Complete
Dependencies: Phase 01

## Objective
Cải thiện giao diện của sổ "Thêm lượt khám", thêm nút "Lưu & Kê đơn ngay" và cập nhật logic gọi callback để hỗ trợ thao tác tự động.

## Requirements
### Functional
- [x] Thêm file nút bấm "LƯU & KÊ ĐƠN NGAY 💊" làm nút Primary.
- [x] Sửa nút lưu hiện tại thành nút Secondary ("Chỉ Lưu").
- [x] Disable nút sau khi click để phòng ngừa double-click.
- [x] Bỏ MessageBox báo thành công không cần thiết (tránh bắt bác sĩ bấm OK).
- [x] Truyền ID vừa tạo và action (`"prescribe"` hoặc `"refresh"`) về màn hình chính thông qua callback.

## Implementation Steps
1. [x] Mở file `ui_add_visit_window_pyside.py`.
2. [x] Trong hàm `setup_ui`, thêm nút `btn_save_and_prescribe` với style và logic mới.
3. [x] Trong hàm `save_visit`, lấy kết quả trả về từ `add_patient_db` làm `new_visit_id`.
4. [x] Bỏ các lệnh gọi popup messagebox thông báo thành công.
5. [x] Cập nhật gọi `self.on_success_callback(action=..., new_id=new_visit_id)`.

## Files to Create/Modify
- `ui_add_visit_window_pyside.py` - Thêm UI và sửa logic gọi callback.

## Test Criteria
- [ ] Cửa sổ hiện 3 nút: "Hủy", "Chỉ Lưu", "LƯU & KÊ ĐƠN NGAY".
- [ ] Bấm nút không bị crash.
- [ ] Callback được gọi đúng với `action` tương ứng.

---
Next Phase: [Phase 03](phase-03-integration.md)
