# Plan: Performance Optimization
Created: 2026-03-31T22:01:19+07:00
Status: 🟡 In Progress

## Overview
Dự án có một số vấn đề nghiêm trọng về hiệu năng khi xử lý dữ liệu lớn, đặc biệt là lỗi N+1 query (gọi Database từng dòng), Blocking luồng đồng bộ, và sử dụng hàm không hợp lệ với Index. Kế hoạch này sẽ giải quyết triệt để các vấn đề hiệu năng được nêu trong `performance.md`.

## Tech Stack
- Frontend: PySide6 (UI)
- Backend: Python
- Database: SQLite (Local) + Supabase (Cloud)

## Phases

| Phase | Name | Status | Progress |
|-------|------|--------|----------|
| 01 | Fix Bulk Insert (Restore & Import) | ⬜ Pending | 0% |
| 02 | Fix Sync Worker Blocking & Retries | ⬜ Pending | 0% |
| 03 | Fix N+1 Queries (History & Sync) | ⬜ Pending | 0% |
| 04 | Optimize Database Queries & UI | ⬜ Pending | 0% |
| 05 | Testing & Verification | ⬜ Pending | 0% |

## Quick Commands
- Start Phase 1: `/code phase-01`
- Check progress: `/next`
- Save context: `/save-brain`
