# Phase 01: Database Migration
Status: ⬜ Pending
Dependencies: None

## Objective
Thêm 2 cột `stock_quantity` và `min_stock_level` vào bảng `medicines` bằng migration idempotent.

## Implementation Steps
1. [ ] Thêm migration block trong `initialize_database()` (database.py)
2. [ ] Kiểm tra `PRAGMA table_info(medicines)` trước khi ALTER
3. [ ] Test: Chạy app 2 lần liên tiếp → migration không lỗi

## Files to Modify
- `database.py` — Thêm ALTER TABLE migration (~15 dòng)

## Test Criteria
- [ ] App khởi động không lỗi
- [ ] Thuốc cũ có stock_quantity=0, min_stock_level=5
- [ ] Chạy lại app lần 2 → không lỗi duplicate column

---
Next Phase: phase-02-backend.md
