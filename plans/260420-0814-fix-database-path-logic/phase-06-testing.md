# Phase 06: Testing & Verification

**Status:** ✅ Completed  
**Dependencies:** Phase 01–05 (tất cả)  
**File cần tạo:** `plans/260420-0814-fix-database-path-logic/reports/test_results.md`

---

## Objective

Kiểm tra toàn bộ flow Database Path sau khi sửa xong Phase 01-05. Gồm **unit test** cho config functions + **manual test** cho UI flow.

---

## 6.1. Unit Tests — Config Functions

### Test Script (chạy trực tiếp bằng Python)

```python
# test_db_path_config.py (tạo tạm, chạy rồi xóa)
import sys, os
sys.path.insert(0, '.')
import config

def test_set_none():
    config.set_database_path(None)
    assert config.get_database_path() == config.DATABASE_NAME
    assert config.get_database_path_override() == ""
    print("✅ set_database_path(None) → default")

def test_set_empty():
    config.set_database_path("")
    assert config.get_database_path() == config.DATABASE_NAME
    assert config.get_database_path_override() == ""
    print("✅ set_database_path('') → default")

def test_set_whitespace():
    config.set_database_path("   ")
    assert config.get_database_path() == config.DATABASE_NAME
    assert config.get_database_path_override() == ""
    print("✅ set_database_path('   ') → default")

def test_set_valid():
    config.set_database_path("/tmp/test.db")
    assert config.get_database_path() == "/tmp/test.db"
    assert config.get_database_path_override() == "/tmp/test.db"
    print("✅ set_database_path('/tmp/test.db') → custom path")

def test_set_with_spaces():
    config.set_database_path("  /tmp/test.db  ")
    assert config.get_database_path() == "/tmp/test.db"
    assert config.get_database_path_override() == "/tmp/test.db"
    print("✅ set_database_path('  /tmp/test.db  ') → stripped path")

def test_reset():
    config.set_database_path("/tmp/test.db")
    config.set_database_path(None)
    assert config.get_database_path() == config.DATABASE_NAME
    print("✅ Reset: custom → None → default")

if __name__ == "__main__":
    test_set_none()
    test_set_empty()
    test_set_whitespace()
    test_set_valid()
    test_set_with_spaces()
    test_reset()
    print("\n🎉 ALL CONFIG TESTS PASSED!")
```

### Checklist:

- [ ] `test_set_none` — Pass
- [ ] `test_set_empty` — Pass
- [ ] `test_set_whitespace` — Pass
- [ ] `test_set_valid` — Pass
- [ ] `test_set_with_spaces` — Pass
- [ ] `test_reset` — Pass

---

## 6.2. Manual Tests — Settings Persistence

### Test A: Save & Load với custom path

1. [ ] Chạy app → Tab Cài đặt → Chọn file `.db` custom
2. [ ] Đóng app → Check `settings.json` → `database_path` = custom path
3. [ ] Mở lại app → Check console log → `[STARTUP] Database path loaded early: <custom_path>`
4. [ ] Tab Cài đặt → Hiển thị đúng custom path

### Test B: Save & Load sau reset

1. [ ] Đang dùng custom path → Nhấn "Quay về mặc định"
2. [ ] Check `settings.json` → `database_path` = `""`
3. [ ] Mở lại app → Check console log → Không in `[STARTUP] Database path loaded early`
4. [ ] Tab Cài đặt → Hiển thị default path

### Test C: Startup sync order

1. [ ] Set custom path trong `settings.json` thủ công
2. [ ] Chạy app → Quan sát log console:
   - `[STARTUP] Database path loaded early: <custom_path>` phải xuất hiện **TRƯỚC** `sync_manager.startup_sync()`
3. [ ] Verify SyncWorker đang dùng đúng file (có thể thêm log tạm vào `database._get_db_connection()`)

---

## 6.3. Manual Tests — Validation & Safety

### Test D: File validation

1. [ ] Chọn file `.db` hợp lệ (có bảng patients) → Hiện confirmation → OK
2. [ ] Chọn file `.txt` đổi tên `.db` → Dialog "File không hợp lệ" → Block
3. [ ] Chọn file `.db` từ app khác → Warning "Không có bảng quen thuộc" → Cho phép chọn Yes
4. [ ] Chọn file `.db` rỗng (0 byte) → Xử lý đúng (tùy implementation)

### Test E: Confirmation dialogs

1. [ ] Chọn file mới → Confirmation → Chọn No → Không thay đổi gì
2. [ ] Chọn file mới → Confirmation → Chọn Yes → Lưu thành công
3. [ ] Nhấn "Quay về mặc định" khi đang ở custom → Hiện confirmation
4. [ ] Nhấn "Quay về mặc định" khi đã ở mặc định → Không hiện confirmation (hoặc inform only)

---

## 6.4. Manual Tests — UX Improvements (Nếu có Phase 05)

### Test F: Nút mở thư mục

1. [ ] Nhấn 📁 khi DB ở default path → Mở đúng thư mục app
2. [ ] Nhấn 📁 khi DB ở custom path → Mở đúng thư mục custom
3. [ ] Nhấn 📁 khi thư mục bị xóa → Hiện warning

### Test G: Tạo DB mới

1. [ ] Nhấn "Tạo mới" → Chọn vị trí → Tạo file thành công
2. [ ] Nhấn "Tạo mới" → Chọn file đã tồn tại → Hỏi confirm sử dụng
3. [ ] Nhấn "Tạo mới" → Cancel → Không thay đổi
4. [ ] Khởi động lại sau khi tạo mới → App tạo bảng tự động → Chạy bình thường

---

## 6.5. Regression Tests

Đảm bảo các tính năng KHÔNG liên quan vẫn hoạt động:

- [ ] Thêm bệnh nhân → Lưu vào DB đúng
- [ ] Kê đơn thuốc → Lưu vào DB đúng
- [ ] Sync lên Supabase → Sync từ đúng file DB
- [ ] Đổi theme Light/Dark → Không ảnh hưởng DB path
- [ ] Đổi tên phòng khám → Không ảnh hưởng DB path
- [ ] Đổi tiền công khám → Không ảnh hưởng DB path

---

## Report Template

Sau khi test xong, tạo file:

```markdown
# Test Results — Fix Database Path Logic

**Date:** YYYY-MM-DD
**Tester:** [Name]

## Summary
- ✅ Passed: X/Y tests
- ❌ Failed: Z tests (nếu có)

## Detailed Results

| Test | Status | Notes |
|------|--------|-------|
| Config: set None | ✅ | |
| Config: set empty | ✅ | |
| ... | ... | ... |

## Issues Found
- (Nếu có issue mới phát hiện khi test)
```

---

## Notes

- Unit test script nên được chạy trong terminal (`python test_db_path_config.py`) rồi **xóa** sau khi test xong.
- Manual tests cần chạy app thực tế.
- Regression tests quan trọng — sửa DB path không được làm hỏng tính năng khác.

---

**Previous Phase:** [Phase 05 - UX Improvements](./phase-05-ux-improvements.md)  
**Workflow Complete** 🎉
