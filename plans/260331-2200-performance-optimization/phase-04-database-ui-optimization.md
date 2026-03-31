# Phase 04: Optimize Database Queries & UI
Status: ✅ Completed (2026-03-31)
Dependencies: None

## Objective
Xử lý lỗi về index do sử dụng `strftime` (M4), lỗi chuẩn hóa chuỗi bị lặp trong UI tìm kiếm (M5), và duplicate signal (M7).

## Requirements
### Functional
- [ ] Sửa đổi truy vấn dùng `strftime` để lọc ngày tháng sang toán tử so sánh lớn/nhỏ hơn (`>=` và `<`).
- [ ] Thêm các Index còn thiếu cho các bảng `prescriptions_header` và `prescription_details`.
- [ ] Lưu sẵn bộ cài đặt name_norm trong bộ nhớ List Thuốc tại class `MedicineTab`.
- [ ] Gỡ bỏ kết nối signal lặp trong `ui_stats_pyside.py`.

### Non-Functional
- [ ] UI mượt mà hơn khi gõ phím tìm kiếm thuốc.
- [ ] Tab Thống Kê giảm một nửa thao tác ảo, không tải gấp đôi data.

## Implementation Steps
1. [ ] Step 1 - Cập nhật `database.py`, viết lại `get_stats_by_day_for_month` và `get_patient_dobs_by_time` để loại bỏ `strftime` ở khóa lọc, chuyển thành khoảng thời gian đầu cuối.
2. [ ] Step 2 - Cập nhật database_migration (nếu có) hoặc schema khởi tạo để thêm IDX cho các khóa ngoại của Prescription.
3. [ ] Step 3 - Sửa `ui_medicine_pyside.py`, thêm biến lưu bộ đệm `name_norm` cho từng Item lúc `on_medicines_loaded`. Ở `apply_filters`, đối chiếu với bộ đệm sẵn thay vì chạy `remove_diacritics` trên hàng nghìn Object.
4. [ ] Step 4 - Sửa `ui_stats_pyside.py`, tìm đoạn `worker.signals.result.connect` dư thừa và xóa.

## Files to Create/Modify
- `database.py`
- `ui_medicine_pyside.py`
- `ui_stats_pyside.py`

## Test Criteria
- [ ] Các loại báo cáo thống kê vẫn trích xuất đúng số liệu thống kê.
- [ ] Khung search Thuốc đáp ứng tức thời ngay khi gõ.
- [ ] DB Query plan chạy trên index thay vì scan table (có thể test bằng EXPLAIN QUERY PLAN).

---
Next Phase: phase-05-testing.md
