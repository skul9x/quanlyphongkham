# Plan: Fix Database Path Logic Bugs

**Created:** 2026-04-20 08:14  
**Status:** 🟡 In Progress  
**Source:** [report.md](../../report.md) (Audit 2026-04-20)

---

## Overview

Sửa **5 lỗi logic** và thêm **2 cải tiến UX** cho tính năng "Đường dẫn Database" trong tab Cài đặt. Lỗi nghiêm trọng nhất: SyncWorker chạy trước khi load custom DB path → sync sai file database.

## Scope

| Component | Files liên quan |
|-----------|----------------|
| Config Layer | `config.py` |
| Startup Flow | `main_pyside.py` (block `__main__` + `MainWindow.__init__`) |
| Settings UI | `ui_help_pyside.py` (`browse_db_path`, `reset_db_path`) |
| Settings Persistence | `main_pyside.py` (`save_settings`, `_load_database_path_from_settings`) |

## Phases

| Phase | Name | Status | Bugs Addressed | Estimated |
|-------|------|--------|----------------|-----------|
| 01 | Config Core Hardening | ⬜ Pending | Bug #4 (Truthiness) | 5 min |
| 02 | Startup Sync Order Fix | ⬜ Pending | Bug #1 (Sync sai DB) | 10 min |
| 03 | Reset & Save Logic Fix | ⬜ Pending | Bug #2 (Reset lưu sai) | 10 min |
| 04 | Validation & Safety | ⬜ Pending | Bug #3, #5 (Validate + Confirm) | 15 min |
| 05 | UX Improvements | ⬜ Pending | Suggestion #6, #7 | 15 min |
| 06 | Testing & Verification | ⬜ Pending | Tất cả | 10 min |

**Tổng:** 6 phases, ~65 phút

## Dependency Graph

```
Phase 01 (Config Core)
    ↓
Phase 02 (Startup Fix)  ←  Phase 03 (Save/Reset Fix)
    ↓                            ↓
Phase 04 (Validation) ──────────→
    ↓
Phase 05 (UX) ← optional
    ↓
Phase 06 (Testing)
```

> **Ghi chú:** Phase 01 phải làm trước vì Phase 02 & 03 phụ thuộc vào config functions đã được fix.

## Quick Commands
- Bắt đầu Phase 1: `/code phase-01`
- Check tiến độ: `/next`
- Lưu context: `/save-brain`
