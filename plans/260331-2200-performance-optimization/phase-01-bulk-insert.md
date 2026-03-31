# Phase 01: Fix Bulk Insert (Restore & Import)
Status: ✅ Completed
Dependencies: None

## Objective
Giải quyết vấn đề nghiêm trọng nhất (C1 & C3): Mồ/đóng kết nối SQLite và `commit` cho từng bản ghi khi khôi phục từ Cloud hoặc nhập từ Excel, gây nghẽn cổ chai disk I/O.

## Requirements
### Functional
- [x] Thêm các hàm `bulk_insert_*` vào `database.py`.
- [x] Cập nhật `pull_all_from_cloud` trong `sync_manager.py` để sử dụng hàm bulk.
- [x] Tối ưu hóa luồng `import_excel` trong `ui_medicine_pyside.py` để dùng bulk insert sau khi parse xong.

### Non-Functional
- [x] Performance: Thời gian phục hồi từ Cloud và Import Excel phải nhanh hơn ít nhất 5x khi có dữ liệu lớn.

## Implementation Steps
1. [x] Step 1 - Thêm `insert_medicines_bulk`, `insert_patients_bulk`, `insert_headers_bulk`, `insert_details_bulk` vào `database.py`.
2. [x] Step 2 - Sửa `pull_all_from_cloud` để truyền list cho các hàm `bulk` thay vì vòng lặp for.
3. [x] Step 3 - Sửa `import_excel` để gom toàn bộ dữ liệu hợp lệ vào mảng, kiểm tra trùng lặp 1 lần, rồi gọi bulk insert.

## Files to Create/Modify
- `database.py` - Add bulk insert functions.
- `sync_manager.py` - Update `pull_all_from_cloud`.
- `ui_medicine_pyside.py` - Update `import_excel`.

## Test Criteria
- [ ] Khôi phục dữ liệu từ Cloud thành công mà không lỗi.
- [ ] Nhập file Excel danh mục thuốc thành công.

---
Next Phase: phase-02-sync-worker.md
