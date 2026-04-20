# Phase 03: Reset & Save Logic Fix

**Status:** ⬜ Pending  
**Dependencies:** Phase 01 (Config Core)  
**Bug Addressed:** Bug #2 🔴 CRITICAL — Reset DB path lưu sai giá trị vào settings.json  
**Files cần sửa:** `main_pyside.py`, `ui_help_pyside.py`

---

## Objective

Đảm bảo khi user nhấn "Quay về mặc định", `settings.json` lưu `"database_path": ""` thay vì path tuyệt đối mặc định. Và khi user gõ lại đường dẫn mới, nó cũng lưu đúng.

---

## Vấn đề hiện tại

### Flow "Quay về mặc định" HIỆN TẠI (SAI):

```python
# ui_help_pyside.py dòng 296-302
def reset_db_path(self):
    config.set_database_path(None)          # ① Override = None ✅ (đúng)
    self.txt_db_path.setText(config.DATABASE_NAME)
    if self.main_window:
        self.main_window.save_settings()    # ② Gọi save ← BUG

# main_pyside.py dòng 333-353
def save_settings(self):
    settings = {
        ...
        "database_path": config.get_database_path(),  # ③ get_database_path() khi override=None
                                                       #    → trả về DATABASE_NAME (path tuyệt đối)
                                                       #    → Lưu: "/home/.../clinic.db" ← SAI!
        ...
    }
```

### Hậu quả:

1. `settings.json` lưu: `"database_path": "/home/skul9x/.../clinic.db"` (path tuyệt đối)
2. Khi khởi động lại → `_load_database_path_from_settings()` đọc path này → set override thành default path
3. **Khi copy app sang máy khác** hoặc **đổi thư mục**: path không tồn tại → fallback → nhưng in WARNING gây confusion
4. Về semantic: ứng dụng "tưởng" đang dùng custom path trong khi thực ra là default

---

## Implementation Steps

### 1. [ ] Sửa `save_settings()` — dùng `get_database_path_override()` thay vì `get_database_path()`

```python
# main_pyside.py, save_settings()
def save_settings(self):
    settings = {
        "theme": self.current_theme,
        "sidebar_collapsed": self.sidebar_collapsed,
        "app_title": self.app_logo.text(),
        "database_path": config.get_database_path_override(),  # ← Dùng override, không phải resolved
        "consultation_fee": config.get_consultation_fee(),
        "window_geometry": { ... }
    }
```

**Lý do:**
- `get_database_path_override()` trả về `""` khi dùng default → `settings.json` lưu `"database_path": ""`
- `get_database_path_override()` trả về custom path khi có override → lưu đúng

### 2. [ ] Sửa `reset_db_path()` — hiển thị text thân thiện hơn

```python
# ui_help_pyside.py
def reset_db_path(self):
    from PySide6.QtWidgets import QMessageBox
    config.set_database_path(None)
    self.txt_db_path.setText(config.get_database_path())  # ← Hiển thị path thực tế (resolved)
    if self.main_window:
        self.main_window.save_settings()
    QMessageBox.information(self, "Thành công", 
        "Đã quay về mặc định!\nVui lòng khởi động lại ứng dụng để áp dụng thay đổi.")
```

**Ghi chú:** Dùng `config.get_database_path()` để hiển thị (cho user thấy path thực tế), nhưng `save_settings()` dùng `get_database_path_override()` để lưu (phân biệt custom vs default).

### 3. [ ] Sửa `_load_database_path_from_settings()` — skip chuỗi rỗng

Kiểm tra lại logic load để đảm bảo xử lý đúng giá trị `""`:

```python
# main_pyside.py
def _load_database_path_from_settings(self):
    try:
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
                db_path = settings.get("database_path", "").strip()  # ← Thêm .strip()
                if db_path and os.path.exists(db_path):
                    config.set_database_path(db_path)
                    print(f"[CONFIG] Database path: {db_path}")
                elif db_path:
                    print(f"[CONFIG] WARNING: DB path does not exist: {db_path}, using default")
                # db_path == "" → Không làm gì, dùng default ✅
    except (json.JSONDecodeError, IOError):
        pass
```

**Ghi chú:** Logic gần như giống cũ, chỉ thêm `.strip()` cho safety. Quan trọng là **không set override khi db_path rỗng**.

---

## Trạng thái settings.json TRƯỚC và SAU fix

### Trường hợp 1: User dùng default path

| | Trước fix | Sau fix |
|---|-----------|---------|
| `settings.json` | `"database_path": "/home/.../clinic.db"` | `"database_path": ""` |
| Khởi động lại | Set override = default path (dư thừa) | Không set override → dùng default tự nhiên |
| Copy sang máy khác | WARNING: path không tồn tại | Hoạt động bình thường |

### Trường hợp 2: User chọn custom path

| | Trước fix | Sau fix |
|---|-----------|---------|
| `settings.json` | `"database_path": "/custom/path.db"` | `"database_path": "/custom/path.db"` |
| Khởi động lại | Set override = custom path ✅ | Set override = custom path ✅ |
| Copy sang máy khác | WARNING nếu path không tồn tại | WARNING nếu path không tồn tại |

### Trường hợp 3: User nhấn "Quay về mặc định"

| | Trước fix | Sau fix |
|---|-----------|---------|
| `settings.json` | `"database_path": "/home/.../clinic.db"` (vẫn có path!) | `"database_path": ""` |
| Semantic | Tưởng custom, thực ra default | Rõ ràng: đang dùng default |

---

## Files to Create/Modify

| File | Action | Chi tiết |
|------|--------|---------|
| `main_pyside.py` | **Modify** | Sửa `save_settings()` dùng `get_database_path_override()`, thêm `.strip()` trong `_load_database_path_from_settings()` |
| `ui_help_pyside.py` | **Modify** | Sửa `reset_db_path()` hiển thị resolved path |

---

## Test Criteria

- [ ] Nhấn "Quay về mặc định" → `settings.json` lưu `"database_path": ""`
- [ ] Chọn custom path → `settings.json` lưu đúng custom path
- [ ] Khởi động lại sau reset → Dùng default, **không in WARNING**
- [ ] Khởi động lại sau set custom → Dùng custom, in log đúng
- [ ] Copy thư mục app sang nơi khác → Dùng default vẫn hoạt động bình thường

---

## Notes

- Phase này phụ thuộc Phase 01 (cần `get_database_path_override()` đã được tạo).
- Fix cũng gián tiếp cải thiện portability (di chuyển app giữa các máy).
- Hàm `_load_db_path_early()` ở Phase 02 cũng hưởng lợi từ fix này.

---

**Previous Phase:** [Phase 02 - Startup Sync Order Fix](./phase-02-startup-sync-fix.md)  
**Next Phase:** [Phase 04 - Validation & Safety](./phase-04-validation-safety.md)
