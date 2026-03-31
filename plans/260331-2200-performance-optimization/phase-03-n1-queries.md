# Phase 03: Fix N+1 Queries (History & Sync)
Status: ✅ Completed (2026-03-31)
Dependencies: None

## Objective
Kế hoạch này giải quyết (M1, M2, M3): Tình trạng vòng lặp gọi nhiều câu lệnh SELECT/SYNC phụ trên từng đối tượng đơn lẻ, thay vì dùng WHERE IN (...) hoặc gom theo mẻ.

## Requirements
### Functional
- [ ] Xóa lặp vòng khi gán details vào đơn thuốc trong `get_prescriptions_by_patient_db`.
- [ ] Chuyển đổi Incremental Sync fetch thành tìm kiếm batch IN(...) cho các patient bị thiếu.
- [ ] Sửa đổi `append_items_to_prescription_db` để chỉ sync những detail mới, không đồng bộ lại toàn bộ header details.

### Non-Functional
- [ ] Performance: Giảm đáng kể số vòng kết nối mạng và I/O local DB. Lịch sử bệnh án load tức thì.

## Implementation Steps
1. [ ] Step 1 - Sửa `get_prescriptions_by_patient_db`: Query lấy toàn bộ headers, gom ID, sau đó `SELECT * FROM prescription_details WHERE prescription_header_id IN (...)` và gom nhóm bằng Dict Python.
2. [ ] Step 2 - Sửa `append_items_to_prescription_db`: Lấy list detail ID nội bộ mới được thêm vào, và chỉ loop sync những detail này.
3. [ ] Step 3 - Thêm hàm `get_patients_by_ids` trong DB và gọi nó trong `_incremental_sync`.

## Files to Create/Modify
- `database.py` - Update queries for N+1 fixes.
- `sync_manager.py` - Update `_incremental_sync`.

## Test Criteria
- [ ] Danh sách lịch sử đơn thuốc của bệnh nhân lâu năm tải lên mượt mà không bị khựng.
- [ ] Thêm thuốc mới vào đơn thuốc có sẵn chỉ đồng bộ dữ liệu mới chứ không đồng bộ thừa.

---
Next Phase: phase-04-database-ui-optimization.md
