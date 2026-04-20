# Phase 05: UX Improvements

**Status:** ⬜ Pending  
**Dependencies:** Phase 04 (Validation & Safety)  
**Bug Addressed:** Suggestion #6 (Mở thư mục), Suggestion #7 (Tạo DB mới)  
**File cần sửa:** `ui_help_pyside.py`

---

## Objective

Nâng cấp UX cho phần "Đường dẫn Database" bằng 2 tính năng tiện ích:
1. **Nút "Mở thư mục"** — mở folder chứa file DB hiện tại (để backup thủ công)
2. **Nút "Tạo mới"** — tạo file database trống tại vị trí tùy chọn

---

## Implementation Steps

### 1. [ ] Thêm nút "📁 Mở thư mục" vào db_path_row

Đặt cạnh nút "Chọn..." hiện tại:

```python
# ui_help_pyside.py, trong setup_ui(), sau btn_browse

btn_open_folder = QPushButton("📁")
btn_open_folder.setFixedWidth(40)
btn_open_folder.setToolTip("Mở thư mục chứa database")
btn_open_folder.setCursor(Qt.CursorShape.PointingHandCursor)
btn_open_folder.setStyleSheet("""
    QPushButton { 
        background-color: #64748b; color: white; 
        font-weight: bold; border-radius: 4px; padding: 8px; 
        font-size: 14px;
    }
    QPushButton:hover { background-color: #475569; }
""")
btn_open_folder.clicked.connect(self.open_db_folder)

db_path_row.addWidget(self.txt_db_path)
db_path_row.addWidget(btn_browse)
db_path_row.addWidget(btn_open_folder)  # ← NEW
```

### 2. [ ] Implement `open_db_folder()`

```python
def open_db_folder(self):
    """Open the folder containing the current database file."""
    import subprocess
    import platform
    
    db_path = config.get_database_path()
    folder = os.path.dirname(db_path)
    
    if not os.path.exists(folder):
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.warning(self, "Lỗi", f"Thư mục không tồn tại:\n{folder}")
        return
    
    # Cross-platform folder open
    system = platform.system()
    if system == "Linux":
        subprocess.Popen(["xdg-open", folder])
    elif system == "Darwin":  # macOS
        subprocess.Popen(["open", folder])
    elif system == "Windows":
        subprocess.Popen(["explorer", folder])
```

### 3. [ ] Chuyển nút "Chọn..." thành 2 option: "Chọn file có sẵn" và "Tạo mới"

Thay vì thêm nút riêng, sửa nút "Chọn..." thành hiển thị menu context:

**Option A (Đơn giản — thêm nút riêng):**

```python
btn_create_new = QPushButton("Tạo mới")
btn_create_new.setFixedWidth(80)
btn_create_new.setCursor(Qt.CursorShape.PointingHandCursor)
btn_create_new.setStyleSheet("""
    QPushButton { 
        border: 1px solid #3b82f6; border-radius: 4px; 
        padding: 8px; color: #3b82f6; 
    }
    QPushButton:hover { background-color: #eff6ff; }
""")
btn_create_new.clicked.connect(self.create_new_db)
```

### 4. [ ] Implement `create_new_db()`

```python
def create_new_db(self):
    """Create a new empty database at a user-chosen location."""
    from PySide6.QtWidgets import QFileDialog, QMessageBox
    import sqlite3
    
    file_path, _ = QFileDialog.getSaveFileName(
        self, "Tạo Database mới", "clinic.db", 
        "Database files (*.db)"
    )
    if not file_path:
        return
    
    # Ensure .db extension
    if not file_path.endswith('.db'):
        file_path += '.db'
    
    # Check if file already exists
    if os.path.exists(file_path):
        reply = QMessageBox.question(
            self, "File đã tồn tại",
            f"File {os.path.basename(file_path)} đã tồn tại.\n"
            "Bạn muốn sử dụng file này thay vì tạo mới?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
    else:
        # Create empty SQLite file
        try:
            conn = sqlite3.connect(file_path)
            conn.close()
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không tạo được file:\n{str(e)}")
            return
    
    # Set as current DB
    config.set_database_path(file_path)
    self.txt_db_path.setText(file_path)
    if self.main_window:
        self.main_window.save_settings()
    QMessageBox.information(
        self, "Thành công", 
        f"Đã tạo database mới tại:\n{file_path}\n\n"
        "Vui lòng khởi động lại ứng dụng để áp dụng thay đổi.\n"
        "(Ứng dụng sẽ tự tạo các bảng dữ liệu khi khởi động)"
    )
```

### 5. [ ] Cập nhật layout hàng nút phụ

Sắp xếp lại layout cho tidy:

```python
# Hàng nút phụ (bên dưới path row)
btn_row2 = QHBoxLayout()
btn_row2.addWidget(btn_reset_db)
btn_row2.addWidget(btn_create_new)  # ← NEW
btn_row2.addStretch()
db_layout.addLayout(btn_row2)
```

---

## UI Layout SAU KHI FIX

```
┌─ Đường dẫn Database ────────────────────────────────────┐
│ Cấu hình vị trí lưu trữ file dữ liệu (.db):           │
│                                                          │
│ ┌────────────────────────────────┐ [Chọn...] [📁]       │
│ │ /path/to/current/clinic.db     │                       │
│ └────────────────────────────────┘                       │
│                                                          │
│ [Quay về mặc định (clinic.db)]  [Tạo mới]               │
│                                                          │
│ ⚠️ Thay đổi cần khởi động lại ứng dụng để có hiệu lực. │
└──────────────────────────────────────────────────────────┘
```

---

## Files to Create/Modify

| File | Action | Chi tiết |
|------|--------|---------|
| `ui_help_pyside.py` | **Modify** | Thêm nút 📁, thêm nút "Tạo mới", implement `open_db_folder()`, `create_new_db()` |

---

## Test Criteria

- [ ] Nhấn 📁 → Mở đúng thư mục chứa file DB hiện tại
- [ ] Nhấn 📁 khi thư mục không tồn tại → Hiện warning
- [ ] Nhấn "Tạo mới" → FileDialog save → Tạo file `.db` rỗng → Lưu path
- [ ] Nhấn "Tạo mới" → Chọn file đã tồn tại → Hỏi confirm sử dụng
- [ ] Nhấn "Tạo mới" → Cancel → Không thay đổi gì
- [ ] UI hiển thị đẹp, không bị vỡ layout ở cả Light/Dark mode

---

## Notes

- Phase này **không bắt buộc** (nice-to-have) nhưng cải thiện UX đáng kể.
- Nút 📁 đặc biệt hữu ích cho user muốn backup thủ công file DB.
- `create_new_db()` chỉ tạo file rỗng — `initialize_database()` sẽ tự tạo bảng khi app khởi động lại.
- Cross-platform: dùng `xdg-open` (Linux), `open` (macOS), `explorer` (Windows).

---

**Previous Phase:** [Phase 04 - Validation & Safety](./phase-04-validation-safety.md)  
**Next Phase:** [Phase 06 - Testing & Verification](./phase-06-testing.md)
