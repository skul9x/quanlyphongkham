# Phase 03: Main Screen Integration
Status: ✅ Complete
Dependencies: Phase 02

## Objective
Đón tín hiệu từ callback ở màn hình gọi (Patient Detail hoặc Main Window) để tự động hóa việc mở cửa sổ kê đơn và focus vào dòng lượt khám vừa tạo.

## Requirements
### Functional
- [x] Cập nhật hàm nhận callback sau khi thêm lượt khám thành công (handle success callback).
- [x] Reload danh sách hiện tại.
- [x] Tự động chuyển focus/selection sang lượt khám `new_id`.
- [x] Gọi hàm mở cửa sổ Kê đơn trực tiếp cho bệnh nhân đó nếu `action == "prescribe"`.

## Implementation Steps
1. [x] Xác định file đang khởi tạo `AddVisitWindow` (có thể là `ui_patient_detail.py` hoặc `main_pyside.py`).
2. [x] Tìm hàm được gán vào `on_success_callback`.
3. [x] Cập nhật hàm này để chấp nhận 2 tham số mới: `action` và `new_id`.
4. [x] Gọi hàm reload data `self.refresh_data()` hoặc tương đương.
5. [x] Thêm logic tự động chọn vào list (nếu có `new_id`).
6. [x] Gọi hàm mở popup kê đơn (vd: `self.open_prescription_window(new_id)`) dựa trên điều kiện `action`.

## Files to Create/Modify
- `ui_patient_pyside.py` ✅ - Updated `refresh_current()` to accept `action` and `new_id` parameters, added `_open_prescription_for_visit()` helper method.

## Test Criteria
- [x] Khi bấm "Chỉ Lưu" ở popup -> popup đóng, danh sách reload và tự động select dòng vừa thêm, NHƯNG không mở kê đơn.
- [x] Khi bấm "Lưu & Kê đơn ngay" -> popup đóng, danh sách reload, dòng được chọn -> Mở luôn popup kê đơn cho dòng đó.
- [x] Toàn bộ luồng không hiện thông báo dư thừa.

---
Next Phase: None (Completion)
