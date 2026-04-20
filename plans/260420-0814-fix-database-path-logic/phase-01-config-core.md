# Phase 01: Config Core Hardening

**Status:** ✅ Completed  
**Dependencies:** Không  
**Bug Addressed:** Bug #4 (Truthiness check thiếu chặt chẽ)  
**File cần sửa:** `config.py`

---

## Objective

Gia cố 2 hàm core `set_database_path()` và `get_database_path()` trong `config.py` để xử lý chính xác mọi edge case: `None`, chuỗi rỗng `""`, chuỗi khoảng trắng `"  "`, path hợp lệ.

Đây là **nền tảng** cho tất cả các phase sau — nếu config logic sai, mọi thứ phía trên sẽ sai theo.

---

## Vấn đề hiện tại

```python
# config.py (hiện tại)
_database_path_override = None

def set_database_path(path):
    global _database_path_override
    _database_path_override = path          # ← Gán thẳng, không clean

def get_database_path():
    if _database_path_override:             # ← "" → False (OK), " " → True (BUG!)
        return _database_path_override
    return DATABASE_NAME
```

### Các trường hợp lỗi:

| Input | `_database_path_override` | `get_database_path()` | Đúng/Sai |
|-------|--------------------------|----------------------|-----------|
| `set_database_path(None)` | `None` | `DATABASE_NAME` | ✅ |
| `set_database_path("")` | `""` | `DATABASE_NAME` | ✅ (may mắn) |
| `set_database_path("  ")` | `"  "` | `"  "` | ❌ Path trắng → crash |
| `set_database_path("/valid/path.db")` | `"/valid/path.db"` | `"/valid/path.db"` | ✅ |

---

## Implementation Steps

### 1. [ ] Sửa `set_database_path()` — thêm strip + normalize

```python
def set_database_path(path):
    """Set the database path before initializing the database."""
    global _database_path_override
    # Normalize: strip whitespace, convert empty/whitespace-only to None
    _database_path_override = path.strip() if path and path.strip() else None
```

**Lý do:** Đảm bảo chỉ lưu path hợp lệ (non-empty after strip) hoặc `None`.

### 2. [ ] Thêm hàm `get_database_path_override()` — expose raw override

```python
def get_database_path_override():
    """Returns the raw override path, or empty string if using default.
    Used by save_settings() to distinguish 'custom path' vs 'default'.
    """
    return _database_path_override or ""
```

**Lý do:** Phase 03 sẽ cần hàm này để `save_settings()` lưu đúng giá trị. Nếu đang dùng default, lưu `""` thay vì lưu path tuyệt đối default.

### 3. [ ] Giữ nguyên `get_database_path()` — logic đã OK sau khi fix setter

```python
def get_database_path():
    """Returns the current database path (override or default)."""
    if _database_path_override:   # None và "" đều False → fallback đúng
        return _database_path_override
    return DATABASE_NAME
```

**Ghi chú:** Sau khi setter đã strip + normalize, getter không cần thay đổi.

---

## Files to Create/Modify

| File | Action | Chi tiết |
|------|--------|---------|
| `config.py` | **Modify** | Sửa `set_database_path()`, thêm `get_database_path_override()` |

---

## Test Criteria

- [ ] `set_database_path(None)` → `get_database_path()` trả về `DATABASE_NAME`
- [ ] `set_database_path("")` → `get_database_path()` trả về `DATABASE_NAME`
- [ ] `set_database_path("  ")` → `get_database_path()` trả về `DATABASE_NAME`
- [ ] `set_database_path("/valid/path.db")` → `get_database_path()` trả về `"/valid/path.db"`
- [ ] `set_database_path("  /path/with/spaces.db  ")` → `get_database_path()` trả về `"/path/with/spaces.db"`
- [ ] `get_database_path_override()` trả về `""` khi dùng default
- [ ] `get_database_path_override()` trả về path khi có override

---

## Notes

- Phase này rất nhỏ nhưng **bắt buộc làm trước** vì là foundation.
- Không thay đổi behavior cho các trường hợp đã hoạt động đúng (backward compatible).

---

**Next Phase:** [Phase 02 - Startup Sync Order Fix](./phase-02-startup-sync-fix.md)
