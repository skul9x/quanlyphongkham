# Phase 02: Startup Sync Order Fix

**Status:** ✅ Completed  
**Dependencies:** Phase 01 (Config Core)  
**Bug Addressed:** Bug #1 🔴 CRITICAL — Splash Screen sync dùng default DB, MainWindow dùng custom DB  
**File cần sửa:** `main_pyside.py`

---

## Objective

Đảm bảo custom database path được load từ `settings.json` **TRƯỚC KHI** SyncWorker bắt đầu chạy. Hiện tại SyncWorker chạy trước → sync dữ liệu từ file mặc định `clinic.db` thay vì file custom.

---

## Vấn đề hiện tại

### Flow khởi động HIỆN TẠI (SAI):

```
__main__:
  1. app = QApplication(...)
  2. splash = SplashScreen()
  3. worker = SyncWorker()
  4. worker_thread.start()
     └── worker.run_sync()
         └── sync_manager.startup_sync()
             └── database._get_db_connection()
                 └── config.get_database_path()
                     └── _database_path_override = None  ← ❌ CHƯA ĐƯỢC SET!
                     └── Trả về DATABASE_NAME (default clinic.db)
  
  ... sync xong ...
  
  5. MainWindow.__init__()
     └── _load_database_path_from_settings()  ← ❌ QUÁ MUỘN!
         └── config.set_database_path(custom_path)
     └── setup_database()
         └── database.initialize_database()
             └── config.get_database_path()
                 └── Trả về custom_path  ← ✅ Đúng, nhưng sync đã sai rồi
```

### Hậu quả:

1. **Sync UP (local→cloud):** Đẩy dữ liệu từ `clinic.db` mặc định (có thể rỗng) lên cloud → **ghi đè dữ liệu thật**
2. **Sync DOWN (cloud→local):** Tải dữ liệu cloud về `clinic.db` mặc định → **dữ liệu bị lưu sai file**
3. User mở MainWindow → load custom DB → **không thấy dữ liệu vừa sync**

---

## Implementation Steps

### 1. [ ] Thêm hàm `_load_db_path_early()` vào block `__main__`

Đặt **TRƯỚC** khi tạo SyncWorker, **SAU** khi define `APP_DIR`:

```python
# main_pyside.py, trong block __main__, TRƯỚC splash/worker

def _load_db_path_early():
    """Load database path from settings.json before ANY database access."""
    settings_file = os.path.join(APP_DIR, "settings.json")
    try:
        if os.path.exists(settings_file):
            with open(settings_file, 'r') as f:
                settings = json.load(f)
                db_path = settings.get("database_path", "")
                if db_path and os.path.exists(db_path):
                    config.set_database_path(db_path)
                    print(f"[STARTUP] Database path loaded early: {db_path}")
                elif db_path:
                    print(f"[STARTUP] WARNING: Saved DB path does not exist: {db_path}, using default")
    except (json.JSONDecodeError, IOError) as e:
        print(f"[STARTUP] Could not read settings: {e}")

# Gọi ngay
_load_db_path_early()
```

### 2. [ ] Sửa flow trong `__main__` block

```python
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName(config.APP_TITLE)
    app.setOrganizationName("NguyenDuyTruong")
    
    # ✅ NEW: Load DB path FIRST, before any DB access
    _load_db_path_early()
    
    # [STARTUP] Show Splash Screen
    from ui_splash_screen import SplashScreen
    splash = SplashScreen()
    splash.show()
    
    # ... rest giữ nguyên ...
```

### 3. [ ] Loại bỏ logic trùng lặp trong `MainWindow.__init__`

Vì path đã được load sớm ở `__main__`, hàm `_load_database_path_from_settings()` trong `MainWindow.__init__` **vẫn giữ nguyên** nhưng sẽ trở thành idempotent (gọi lại không ảnh hưởng gì vì path đã đúng).

Tùy chọn: có thể thêm guard:

```python
def _load_database_path_from_settings(self):
    # Skip if already loaded (by _load_db_path_early)
    if config._database_path_override is not None:
        return
    # ... existing logic ...
```

**Hoặc** đơn giản hơn: giữ nguyên, vì `set_database_path()` gọi lại cùng value không gây side effect.

---

## Flow khởi động SAU KHI FIX:

```
__main__:
  1. app = QApplication(...)
  2. _load_db_path_early()  ← ✅ NEW! Load custom path ngay
     └── config.set_database_path("/custom/path/clinic.db")
  3. splash = SplashScreen()
  4. worker = SyncWorker()
  5. worker_thread.start()
     └── worker.run_sync()
         └── sync_manager.startup_sync()
             └── config.get_database_path()
                 └── Trả về "/custom/path/clinic.db"  ← ✅ ĐÚNG!
  6. MainWindow.__init__()
     └── _load_database_path_from_settings()  ← Idempotent, không ảnh hưởng
     └── setup_database()  ← ✅ Đúng file
```

---

## Files to Create/Modify

| File | Action | Chi tiết |
|------|--------|---------|
| `main_pyside.py` | **Modify** | Thêm `_load_db_path_early()` trước SyncWorker, sửa `__main__` block |

---

## Test Criteria

- [ ] Khi `settings.json` có `database_path` hợp lệ → SyncWorker sync đúng file custom
- [ ] Khi `settings.json` có `database_path` không tồn tại → Fallback về default, in warning
- [ ] Khi `settings.json` có `database_path: ""` → Dùng default, không lỗi
- [ ] Khi `settings.json` không tồn tại → Dùng default, không crash
- [ ] MainWindow vẫn load settings bình thường (không bị double-set gây side effect)
- [ ] Log console in đúng path đang dùng khi khởi động

---

## Notes

- Đây là bug **nghiêm trọng nhất** vì có thể gây **mất dữ liệu** trên cloud.
- Fix rất đơn giản (chỉ di chuyển logic lên sớm hơn) nhưng impact rất lớn.
- Không cần thay đổi `sync_manager.py` hay `database.py` — chúng đã dùng `config.get_database_path()` đúng cách.

---

**Previous Phase:** [Phase 01 - Config Core Hardening](./phase-01-config-core.md)  
**Next Phase:** [Phase 03 - Reset & Save Logic Fix](./phase-03-reset-save-fix.md)
