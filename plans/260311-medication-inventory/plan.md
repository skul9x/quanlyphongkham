# Plan: Quản lý & Thống kê Thuốc (Medication Inventory)

Created: 2026-03-11
Status: ✅ Complete

## Overview
Thêm tính năng quản lý tồn kho thuốc vào hệ thống Clinic Manager Desktop v5.1.0.
Module sẽ tự động trừ kho khi kê đơn, cảnh báo sắp hết thuốc, và hiện thống kê sử dụng thuốc.

> ⚠️ **Scope: LOCAL ONLY** — Tính năng này chỉ hoạt động trên SQLite local. Không thay đổi gì trên Supabase/Cloud.

## Tech Stack
- **Language:** Python 3.x (không thay đổi)
- **UI:** PySide6 (không thay đổi)
- **Database:** SQLite local (mở rộng bảng `medicines`)

## Phases

| Phase | Name | Status | Progress |
|-------|------|--------|----------|
| 01 | Database Migration (Local) | ✅ Complete | 100% |
| 02 | Backend Inventory Logic | ✅ Complete | 100% |
| 03 | UI Updates | ✅ Complete | 100% |
| 04 | Version Bump + Changelog | ✅ Complete | 100% |
| 05 | Testing & Verification | ✅ Complete | 100% |

**Tổng:** ~35 tasks | Ước tính: 2-3 sessions

## Quick Commands
- Start Phase 1: `/code phase-01`
- Check progress: `/next`
- Save context: `/save-brain`
