# Phase 03: UI Updates
Status: ⬜ Pending
Dependencies: Phase 02

## Objective
Cập nhật giao diện Kho Thuốc, thêm cảnh báo, và thống kê thuốc.

## Implementation Steps
1. [ ] `ui_medicine_pyside.py`: Thêm cột "Tồn kho" và "Tồn tối thiểu" vào TreeWidget
2. [ ] `ui_medicine_pyside.py`: Thêm input fields stock_edit, min_stock_edit vào form
3. [ ] `ui_medicine_pyside.py`: Highlight đỏ nhạt cho thuốc tồn kho thấp
4. [ ] `ui_medicine_pyside.py`: Banner cảnh báo thuốc sắp hết trên cùng
5. [ ] `ui_stats_pyside.py`: Thêm nút "💊 Thuốc dùng nhiều nhất"
6. [ ] `ui_prescription_window_pyside.py`: Cảnh báo inline khi thuốc hết kho

## Files to Modify
- `ui_medicine_pyside.py` — Sửa giao diện chính (~80 dòng)
- `ui_stats_pyside.py` — Thêm 1 nút filter + handler (~40 dòng)
- `ui_prescription_window_pyside.py` — Thêm cảnh báo inline (~20 dòng)

---
Next Phase: phase-04-sync.md
