# Phase 02: Fix Sync Worker Blocking & Retries
Status: ⬜ Pending
Dependencies: phase-01-bulk-insert.md

## Objective
Ngăn chặn hiện tượng nghẹt hàng đợi (Head-of-Line Blocking) khi một thao tác đồng bộ thất bại và retry bằng `time.sleep()`. Thay vào đó, dùng cơ chế đẩy lại vào queue với thời gian retry (delayed queue). Cải thiện M6 bằng cách giảm log thừa.

## Requirements
### Functional
- [ ] Sửa lại logic retry trong `_process_queue` để không dùng `sleep` chặn thread chính.
- [ ] Giảm bớt các dòng `print` không cần thiết trong `worker.py` và `sync_manager.py`.

### Non-Functional
- [ ] Performance: Sync worker không bao giờ bị block quá 1 giây nếu rớt mạng.

## Implementation Steps
1. [ ] Step 1 - Cập nhật `_process_queue` trong `sync_manager.py` để thêm thuộc tính `retry_count` và `next_retry_at` vào task dict. Bỏ `time.sleep` trong `for attempt`.
2. [ ] Step 2 - Tắt hoặc chuyển thành logging level thấp hơn các câu `print` khởi động/kết quả trong `worker.py`.

## Files to Create/Modify
- `sync_manager.py` - Rewrite sync worker retry logic.
- `worker.py` - Reduce verbosity.

## Test Criteria
- [ ] Thêm mới bệnh nhân lúc tắt mạng, sau đó bật mạng lại: ứng dụng không bị đơ và tự động retry thành công sau thời gian trễ.

---
Next Phase: phase-03-n1-queries.md
