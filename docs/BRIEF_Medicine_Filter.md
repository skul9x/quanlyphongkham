# 💡 BRIEF: Tính năng Bộ lọc tồn kho (Kho Thuốc)

**Ngày tạo:** 2026-03-11
**Workflow:** `/brainstorm` -> `/plan`

---

## 1. VẤN ĐỀ CẦN GIẢI QUYẾT
- Màn hình quản lý Thuốc hiện tại gặp khó khăn trong việc theo dõi các loại thuốc sắp hết hoặc đã hết do danh sách quá dài.
- Người dùng cần một phương thức nhanh chóng để lọc và hiển thị chỉ những loại thuốc cần chú ý (để nhập thêm hoặc ngưng kê đơn).

## 2. GIẢI PHÁP ĐỀ XUẤT
Bổ sung cơ chế lọc 2 lớp linh hoạt ngay trên màn hình Kho Thuốc:
1.  **Hộp chọn (Dropdown):** Cung cấp các tuỳ chọn lọc trạng thái (Tất cả, Đang còn, Sắp hết, Đã hết kho) để người dùng chủ động chọn lọc, thiết kế gọn gàng không chiếm diện tích.
2.  **Cảnh báo tương tác (Clickable Alert):** Biến thanh cảnh báo danh sách thuốc sắp hết/đã hết ở đầu trang thành một nút bấm. Khi nhấp vào, tự động chuyển bộ lọc để chỉ hiện các loại thuốc đang nằm trong diện cảnh báo.

## 3. ĐỐI TƯỢNG SỬ DỤNG
- **Primary:** Bác sĩ, Nhân viên quản lý kho thuốc của phòng khám.

## 4. TÍNH NĂNG CHI TIẾT

### 🚀 MVP (Bắt buộc có):
- [ ] Thêm một QComboBox (Dropdown) bên cạnh ô tìm kiếm thuốc.
- [ ] Các tùy chọn trong Dropdown: "Tất cả trạng thái", "Còn hàng", "Sắp hết", "Hết kho".
- [ ] Logic lọc: Kết hợp text trong ô tìm kiếm với trạng thái được chọn trong Dropdown để hiển thị kết quả trên bảng.
- [ ] Biến QLabel cảnh báo đỏ (vd: "CẢNH BÁO: 109 loại đã HẾT KHO") thành đối tượng có thể click (sử dụng sự kiện mousePressEvent hoặc đổi thành QPushButton thiết kế dạng flat).
- [ ] Khi click vào cảnh báo, Dropdown tự động chuyển sang trạng thái tương ứng (VD: Click vào "109 loại đã HẾT KHO" -> Dropdown tự chuyển sang "Hết kho" và danh sách cập nhật).

## 5. BƯỚC TIẾP THEO
- Phân tích kỹ thuật trên file `ui_medicine_pyside.py` để lập Implementation Plan.
