# Phase 04: Validation & Safety

**Status:** ⬜ Pending  
**Dependencies:** Phase 01, 02, 03  
**Bug Addressed:** Bug #3 🟡 (Không validate file .db) + Bug #5 🟡 (Không cảnh báo khi chuyển DB)  
**File cần sửa:** `ui_help_pyside.py`

---

## Objective

Thêm 2 lớp bảo vệ khi user chọn file database mới:
1. **Validate** file có phải SQLite hợp lệ không
2. **Confirm** trước khi chuyển để tránh bấm nhầm

---

## Vấn đề hiện tại

### Bug #3: Không validate file .db

```python
# ui_help_pyside.py dòng 284-294
def browse_db_path(self):
    file_path, _ = QFileDialog.getOpenFileName(
        self, "Chọn file Database", "", "Database files (*.db);;All files (*.*)"
    )
    if file_path:
        config.set_database_path(file_path)  # ← Lưu ngay, không kiểm tra!
        self.txt_db_path.setText(file_path)
        if self.main_window:
            self.main_window.save_settings()
        QMessageBox.information(...)
```

**Rủi ro:**
- User chọn file `.db` bị hỏng → Crash khi khởi động lại
- User chọn file SQLite nhưng schema khác (ví dụ: từ app khác) → Lỗi truy vấn
- User chọn file không phải SQLite (VD: đổi tên `.txt` thành `.db`) → Crash

### Bug #5: Không cảnh báo khi chuyển

- Không có confirmation dialog → dễ bấm nhầm
- Không nói rõ hậu quả (dữ liệu cũ vẫn ở file cũ, không bị xóa)

---

## Implementation Steps

### 1. [ ] Thêm hàm helper `_validate_sqlite_file()` 

Đặt trong `ui_help_pyside.py` (hoặc có thể đặt trong `utils.py`):

```python
def _validate_sqlite_file(file_path):
    """Validate that a file is a valid SQLite database.
    Returns: (is_valid: bool, error_message: str)
    """
    import sqlite3
    try:
        conn = sqlite3.connect(file_path)
        # Check SQLite integrity
        result = conn.execute("PRAGMA integrity_check").fetchone()
        if result[0] != "ok":
            conn.close()
            return False, "File database bị hỏng (integrity check failed)"
        
        # Optional: Check if it has expected tables
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        table_names = [t[0] for t in tables]
        conn.close()
        
        # Warn if it doesn't look like a clinic database
        expected_tables = ['patients', 'medicines']
        has_expected = any(t in table_names for t in expected_tables)
        
        if not has_expected:
            return True, (
                f"⚠️ File này không chứa bảng dữ liệu quen thuộc "
                f"(patients, medicines).\n"
                f"Các bảng tìm thấy: {', '.join(table_names) if table_names else '(trống)'}\n\n"
                f"Bạn vẫn muốn sử dụng file này?"
            )
        
        return True, ""
    except sqlite3.DatabaseError as e:
        return False, f"File không phải database SQLite hợp lệ:\n{str(e)}"
    except Exception as e:
        return False, f"Không đọc được file:\n{str(e)}"
```

### 2. [ ] Sửa `browse_db_path()` — thêm validation + confirmation

```python
def browse_db_path(self):
    from PySide6.QtWidgets import QFileDialog, QMessageBox
    
    # Mở FileDialog
    file_path, _ = QFileDialog.getOpenFileName(
        self, "Chọn file Database", "", 
        "Database files (*.db);;All files (*.*)"
    )
    if not file_path:
        return
    
    # ① Validate SQLite
    is_valid, message = _validate_sqlite_file(file_path)
    
    if not is_valid:
        QMessageBox.warning(self, "File không hợp lệ", message)
        return
    
    # ② Warning nếu file hợp lệ nhưng không phải clinic DB
    if message:  # has warning message
        reply = QMessageBox.question(
            self, "Cảnh báo",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
    
    # ③ Confirmation dialog
    current_path = config.get_database_path()
    reply = QMessageBox.question(
        self, "Xác nhận chuyển Database",
        f"Bạn có chắc muốn chuyển sang database mới?\n\n"
        f"📂 Hiện tại: {current_path}\n"
        f"📂 Mới: {file_path}\n\n"
        f"Dữ liệu hiện tại sẽ không bị xóa,\n"
        f"nhưng ứng dụng sẽ đọc/ghi vào file mới.",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    if reply != QMessageBox.StandardButton.Yes:
        return
    
    # ④ Lưu
    config.set_database_path(file_path)
    self.txt_db_path.setText(file_path)
    if self.main_window:
        self.main_window.save_settings()
    QMessageBox.information(
        self, "Thành công", 
        "Đã lưu đường dẫn mới!\n"
        "Vui lòng khởi động lại ứng dụng để áp dụng thay đổi."
    )
```

### 3. [ ] Thêm confirmation cho `reset_db_path()` (tùy chọn)

```python
def reset_db_path(self):
    from PySide6.QtWidgets import QMessageBox
    
    # Chỉ cần confirm nếu đang dùng custom path
    if config.get_database_path_override():
        reply = QMessageBox.question(
            self, "Xác nhận",
            f"Quay về database mặc định?\n\n"
            f"📂 Đang dùng: {config.get_database_path()}\n"
            f"📂 Mặc định: {config.DATABASE_NAME}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
    
    config.set_database_path(None)
    self.txt_db_path.setText(config.get_database_path())
    if self.main_window:
        self.main_window.save_settings()
    QMessageBox.information(
        self, "Thành công", 
        "Đã quay về mặc định!\n"
        "Vui lòng khởi động lại ứng dụng để áp dụng thay đổi."
    )
```

---

## User Experience Flow SAU KHI FIX

```
User nhấn "Chọn..."
  → FileDialog mở
  → User chọn file

Case 1: File không phải SQLite
  → ❌ Dialog: "File không phải database SQLite hợp lệ"
  → Quay lại, không thay đổi gì

Case 2: File SQLite nhưng không phải clinic DB
  → ⚠️ Dialog: "File không chứa bảng patients/medicines. Vẫn muốn dùng?"
  → User chọn Yes/No

Case 3: File SQLite hợp lệ, có bảng clinic
  → 💬 Dialog: "Chắc chắn muốn chuyển? Đang dùng: X, Mới: Y"
  → User chọn Yes → Lưu thành công
  → User chọn No → Hủy
```

---

## Files to Create/Modify

| File | Action | Chi tiết |
|------|--------|---------|
| `ui_help_pyside.py` | **Modify** | Thêm `_validate_sqlite_file()`, sửa `browse_db_path()`, sửa `reset_db_path()` |

---

## Test Criteria

- [ ] Chọn file `.db` hợp lệ (có bảng patients) → Hiện confirmation → Yes → Lưu OK
- [ ] Chọn file `.db` hợp lệ → Confirmation → No → Không thay đổi gì
- [ ] Chọn file `.txt` đổi tên thành `.db` → "File không hợp lệ" → Từ chối
- [ ] Chọn file `.db` từ app khác → Warning "Không có bảng quen thuộc" → Cho phép chọn Yes
- [ ] Chọn file `.db` bị hỏng → "File bị hỏng" → Từ chối
- [ ] Nhấn "Quay về mặc định" khi đang dùng custom → Hiện confirmation
- [ ] Nhấn "Quay về mặc định" khi đã ở mặc định → Không hiện confirmation, chỉ thông báo

---

## Notes

- Validation dùng `PRAGMA integrity_check` — nhanh và chính xác.
- Check bảng `patients/medicines` chỉ là **warning**, không block — vì user có thể muốn dùng DB mới chưa có data.
- Confirmation dialog giúp tránh "mis-click" nhưng không quá phiền (chỉ 1 bước xác nhận).

---

**Previous Phase:** [Phase 03 - Reset & Save Logic Fix](./phase-03-reset-save-fix.md)  
**Next Phase:** [Phase 05 - UX Improvements](./phase-05-ux-improvements.md)
