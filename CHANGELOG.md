# Changelog

## [2026-03-22] - Phase 02: Update Add Visit UI (Improving Visit-to-Prescription Flow)

### Added
- **ui_add_visit_window_pyside.py**: Added "LƯU & KÊ ĐƠN NGAY 💊" primary button for a seamless transition to the prescription stage.
- **ui_add_visit_window_pyside.py**: Added button disabling logic after click to prevent duplicate visit creation (double-click safety).

### Changed
- **ui_add_visit_window_pyside.py**: Demoted "Lưu Lượt Khám" to "Chỉ Lưu" as a secondary button (ghost style with Indigo border).
- **ui_add_visit_window_pyside.py**: Removed the success MessageBox popup to maintain focus and speed up the user workflow.
- **ui_add_visit_window_pyside.py**: Updated `on_success_callback` to pass both `action` ("prescribe" or "refresh") and `new_id` (visit ID).

## [2026-03-22] - Phase 01: Database Layer Enhancement

### Changed
- **database.py**: Modified `add_patient_db()` to return `new_id` (integer) on success instead of `True`, and `None` on failure instead of `False`. This enables the UI layer to track newly created visit IDs for seamless workflow automation.

### Refactored
- **ui_add_visit_window_pyside.py**: Updated `save_visit()` method to capture `new_visit_id` from database call (line 145). Variable renamed from `success` to `new_visit_id` for clarity.
- **ui_add_patient_window_pyside.py**: Updated `accept_record()` method to capture `new_patient_id` from database call (line 187). Variable renamed from `success` to `new_patient_id` for clarity.

### Technical Notes
- Backward compatible: Integer IDs are truthy, so existing `if success:` checks continue to work as `if new_id:`.
- Prepares foundation for Phase 02: Adding "Lưu & Kê đơn ngay" button with callback mechanism.

---

## [2026-03-11] - v5.1.1: Inventory Filter & Interactive Alerts

### Added
- Status Dropdown Filter in Medicine Tab (All, InStock, LowStock, OutOfStock)
- Interactive Click-to-Filter Alert Banner

### Fixed
- Prescription block due to medical_history parsing vs diagnosis field
- sqlite3.Row .get() crash in prescription window

---

## [Previous versions...]
