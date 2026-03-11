# Changelog - Clinic System

## [5.1.0] - 2026-03-11
### Added
- **Quản lý tồn kho thuốc**: Thêm hệ thống theo dõi số lượng tồn kho (`stock_quantity`) và mức cảnh báo tối thiểu (`min_stock_level`) cho từng loại thuốc.
- **Cảnh báo thuốc hết kho**: Banner cảnh báo nổi bật trên tab "Kho Thuốc" khi có thuốc sắp hết hoặc đã hết.
- **Tự động trừ kho**: Hệ thống tự động trừ số lượng tồn kho khi bác sĩ kê đơn thuốc.
- **Cảnh báo inline khi kê đơn**: Hiển thị cảnh báo trực tiếp trong cửa sổ kê đơn khi số lượng kê vượt quá tồn kho.
- **Thống kê thuốc**: Thêm nút "💊 Báo Cáo Thuốc" trong tab Thống Kê - xem thuốc dùng nhiều nhất theo tháng hoặc tất cả thời gian.
- **Backend**: 3 hàm mới: `update_medicine_stock_db()`, `get_low_stock_medicines_db()`, `get_medicine_usage_stats_db()`.

### Changed
- **Kho Thuốc UI**: Thêm 2 cột "Tồn kho" và "Tối thiểu" vào bảng danh sách thuốc. Dòng thuốc hết kho highlight đỏ, sắp hết highlight vàng.
- **Form thuốc**: Thêm 2 ô nhập liệu "Tồn kho hiện tại" và "Tồn tối thiểu (Ngưỡng cảnh báo)".
- **Kê đơn UI**: Bảng chọn thuốc hiển thị cột "Tồn kho" với màu cảnh báo tương ứng.

## [5.0.6] - 2026-03-02
### Changed
- Cải thiện UI: Đơn giản hóa cửa sổ "Sửa chẩn đoán", loại bỏ ô sửa thuốc bằng Text để tránh xung đột dữ liệu với hệ thống Đơn thuốc mới. 
- Nút bấm: "Sửa chẩn đoán + Đơn thuốc" -> "Sửa chẩn đoán".

### Fixed
- Lỗi hiển thị: Khắc phục triệt để lỗi "Text Clipping" (mất chân chữ g, y, p, q) trên Linux cho các ô nhập liệu trong cửa sổ "Thêm bệnh nhân" và "Sửa chẩn đoán".
- Đồng bộ: Tối ưu hóa logic `update_visit_details_db` để bảo toàn danh sách thuốc cũ khi chỉ sửa đổi chẩn đoán.
- Ổn định: Đảm bảo đồng bộ Cloud ngay lập tức sau khi cập nhật thông tin lâm sàng.

## [5.0.5] - 2026-02-23

## [5.0.3] - 2026-02-07
### Fixed
- Clinic Manager (Desktop): **Sync Delete Đồng Bộ** - Xóa bệnh nhân giờ sẽ chờ Cloud xóa xong mới return. Mobile App sẽ không còn thấy dữ liệu đã xóa.

## [5.0.2] - 2026-02-07
### Fixed
- Clinic Manager (Desktop): **Fix Zombie Data Bug** - Chuyển từ Two-Way Sync sang One-Way Push. Local là Master, Cloud chỉ là Backup. Tránh hiện tượng dữ liệu đã xóa tự động hồi sinh từ Cloud.
- Clinic Manager (Desktop): **Fix AUTOINCREMENT Sequence** - Reset `sqlite_sequence` sau khi restore từ Cloud để tránh ID conflict khi tạo record mới.

### Changed
- Sync Direction: **One-Way Push Only** (Local → Cloud). Auto-pull từ Cloud đã bị disable.
- Restore: Chỉ xảy ra khi Local DB trống (fresh install).

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
