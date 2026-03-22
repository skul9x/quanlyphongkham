# Plan: Improve Visit & Prescription Flow (Cải thiện luồng Thêm lượt khám -> Kê đơn)
Created: 2026-03-22 10:22:23
Status: ✅ Complete

## Overview
Theo phân tích từ UX.txt, luồng "Thêm lượt khám -> Kê đơn" hiện tại đang bị gián đoạn. Bác sĩ phải đóng popup thêm lượt khám, tìm lại lượt khám vừa tạo và bấm kê đơn thủ công. Mục tiêu của plan này là tạo ra một luồng liền mạch: thêm nút "Lưu & Kê đơn ngay", tự động đóng popup, focus vào lượt khám mới và mở thẳng màn hình kê thuốc.

## Tech Stack
- Frontend: PySide6
- Database: SQLite (`database.py`)

## Phases

| Phase | Name | Status | Progress |
|-------|------|--------|----------|
| 01 | Update Database Logic | ✅ Complete | 100% |
| 02 | Update Add Visit UI | ✅ Complete | 100% |
| 03 | Main Screen Integration | ✅ Complete | 100% |

## Quick Commands
- Start Phase 1: `/code phase-01`
- Check progress: `/next`
- Save context: `/save-brain`
