# Phase 01: Update Database Logic
Status: ✅ Complete
Dependencies: None

## Objective
Thay đổi hàm lưu lượt khám (`add_patient_db`) để trả về ID của lượt khám mới thay vì chỉ trả về True/False như hiện tại, giúp cho frontend biết được ID nào vừa được tạo.

## Requirements
### Functional
- [x] Cập nhật hàm `add_patient_db` trong `database.py`.
- [x] Lấy `lastrowid` sau khi execute lệnh INSERT thành công.
- [x] Trả về `new_id` thay vì trả về `True`.

## Implementation Steps
1. [x] Mở file `database.py`.
2. [x] Tìm hàm `add_patient_db()`.
3. [x] Cập nhật phần sau khi `c.execute(INSERT...)` thêm `new_id = c.lastrowid`.
4. [x] Cập nhật phần trả về cuối hàm sửa `return True` thành `return new_id`. Nếu lỗi return `None`.

## Files to Create/Modify
- `database.py` - Sửa logic hàm lưu bệnh nhân.

## Test Criteria
- [ ] Hàm `add_patient_db` trả về một số nguyên (ID) khi lưu thành công.
- [ ] Các tính năng đồng bộ (nếu có trong `add_patient_db`) không bị ảnh hưởng.

---
Next Phase: [Phase 02](phase-02-ui-add-visit.md)
