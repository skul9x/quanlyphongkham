# Changelog - Clinic System

## [4.5.2] - 2026-02-06
### Fixed
- Clinic Manager (Desktop): **Fix Prescription Display Issue** - Triển khai logic "Double-Write" cập nhật đồng thời bảng đơn thuốc mới và trường medical_history (legacy) để tương thích với form cũ và app di động.
- Clinic Manager (Desktop): **Packaging Optimization** - Cập nhật lệnh PyInstaller với đầy đủ hidden-imports (postgrest, httpx, openpyxl) đảm bảo app chạy ổn định sau khi đóng gói.
- Clinic Manager (Desktop): **Fix Race Condition & Transaction Propagation Error** - Đảm bảo dữ liệu local được commit thành công trước khi đẩy lên Cloud.
- Clinic Manager (Desktop): **Fix Duplicate INSERT bug** trong hàm thêm thuốc mới.
- Clinic Manager (Desktop): **Fix Improper Error Handling** - Thêm cơ chế Simple Retry (3 lần) với exponential backoff khi sync fail.
- Clinic Manager (Desktop): **Fix Leaking Mutable State** - Sử dụng shallow copy dữ liệu trước khi đưa vào sync queue.

## [4.5.0] - 2026-02-06
### Added
- Clinic Manager (Desktop): Triển khai Two-Way Sync (Sync 2 chiều Local <-> Cloud). 
- Clinic Manager (Desktop): Cơ chế tự động khôi phục dữ liệu từ Cloud khi database local trống.
- Clinic Manager (Desktop): Tự động so sánh ID bệnh nhân để đẩy dữ liệu local còn thiếu lên Cloud khi startup.

### Fixed
- Clinic Manager (Desktop): Fix lỗi đơn thuốc không hiển thị sau khi sync từ Cloud (do thiếu migration trigger).
- Clinic Manager (Desktop): Cải thiện logic hiển thị đơn thuốc tại UI Chi tiết bệnh nhân (bỏ qua các đơn thuốc rỗng).
- Clinic Manager (Desktop): Đồng bộ hóa cột `diagnosis` và cờ `prescription_migrated` lên Supabase.

## [4.4.0] - 2026-02-06
### Added
- ClinicViewer: Build thành công APK v1.0 cho Android.
- ClinicViewer: Hỗ trợ AGP 8.9.1 và Jetpack Compose mới nhất.
- ClinicViewer: Tích hợp thư viện `appcompat` và `constraintlayout`.

### Changed
- ClinicViewer: Chuyển đổi theme từ Material3 XML sang AppCompat để fix lỗi runtime linking.
- ClinicViewer: Thay thế icon `ContentCopy` bằng icon `Add` (Default) để giảm dependency.

### Fixed
- Clinic Manager (Desktop): Fix lỗi định dạng ngày sync (xử lý chuỗi "tháng" thành "-" để Supabase chấp nhận).
- ClinicViewer: Fix lỗi build AGP 8.5.0 không tương thích với các dependencies mới.
- ClinicViewer: Fix lỗi theme không tìm thấy (Theme.Material3.DayNight.NoActionBar).
