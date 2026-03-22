# Phase 02: Backend Inventory Logic
Status: ⬜ Pending
Dependencies: Phase 01

## Objective
Thêm logic trừ kho tự động khi kê đơn và các hàm query tồn kho.

## Implementation Steps
1. [ ] Thêm hàm `update_medicine_stock_db(mid, new_qty)` 
2. [ ] Thêm hàm `get_low_stock_medicines_db()`
3. [ ] Thêm hàm `get_medicine_usage_stats_db(period)`
4. [ ] Sửa `create_prescription_db()` — trừ kho trong Transaction
5. [ ] Sửa `add_medicine_db()` — nhận thêm stock params
6. [ ] Sửa `update_medicine_db()` — nhận thêm stock params
7. [ ] Sửa `get_all_medicines_db()` — SELECT thêm cột mới
8. [ ] Sửa `get_medicine_by_id_db()` — SELECT thêm cột mới

## Files to Modify
- `database.py` — Thêm/sửa ~8 hàm

## Test Criteria
- [ ] Tạo đơn thuốc → stock giảm đúng số lượng
- [ ] Query thuốc sắp hết kho → trả đúng danh sách
- [ ] Thống kê thuốc dùng nhiều → trả đúng data

---
Next Phase: phase-03-ui.md
