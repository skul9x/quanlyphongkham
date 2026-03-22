# 💡 BRIEF: Quản lý và Thống kê Thuốc (Clinic Medication Management & Analytics)

**Ngày tạo:** 2026-03-11
**Brainstorm cùng:** skul9x

---

## 1. VẤN ĐỀ CẦN GIẢI QUYẾT
Hiện tại, phiên bản Clinic Manager Desktop (v5.0.6) của chúng ta quản lý bệnh nhân và kê đơn rất tốt, nhưng khâu quản lý kho thuốc có thể còn thủ công. Các phòng khám thường gặp khó khăn trong việc:
*   Theo dõi chính xác số lượng thuốc tồn kho theo thời gian thực.
*   Kiểm soát thuốc cận date/hết hạn dẫn đến lãng phí hoặc nguy hiểm cho bệnh nhân.
*   Mất nhiều thời gian để tính toán doanh thu, lợi nhuận từ tiền thuốc.
*   Khó khăn trong việc dự báo loại thuốc nào cần nhập thêm.

## 2. GIẢI PHÁP ĐỀ XUẤT
Phát triển một Module "Quản lý & Thống kê Thuốc" tích hợp sâu vào hệ thống hiện tại. Module này sẽ tự động trừ kho khi có đơn thuốc mới, cảnh báo thông minh, và cung cấp các báo cáo trực quan giúp chủ phòng khám ra quyết định kinh doanh.

## 3. ĐỐI TƯỢNG SỬ DỤNG
- **Primary:** Bác sĩ/Chủ phòng khám (Xem báo cáo, ra quyết định nhập thuốc).
- **Secondary:** Nhân viên y tế/Người phụ trách kho (Nhập kho, kiểm kê, xử lý cảnh báo).

## 4. NGHIÊN CỨU THỊ TRƯỜNG & KINH NGHIỆM XƯƠNG MÁU
Qua nghiên cứu các hệ thống quản lý nhà thuốc/phòng khám chuẩn, đây là những "best practices" cực kỳ quan trọng:

### Kinh nghiệm "xương máu" khi dev chức năng này:
1.  **FEFO (First-Expired, First-Out):** Không dùng FIFO (vào trước ra trước) mà phải dùng FEFO (Hết hạn trước xuất trước). Cùng 1 loại thuốc nhưng mua ở 2 đợt khác nhau sẽ có HSD khác nhau. DB phải thiết kế theo "Lô hàng" (Batch) thay vì chỉ số lượng tổng.
2.  **Đồng bộ dữ liệu:** Vì app của mình có Sync Up Supabase, việc trừ kho phải được xử lý cẩn thận trong Transaction (cùng lúc với kê đơn) để tránh data inconsistency (kê đơn xong nhưng kho báo lỗi/chưa trừ).
3.  **UI/UX cho Cảnh báo:** Đừng làm cảnh báo quá phiền phức (pop-up liên tục). Nên dùng Dashboard Alert (VD: "Có 5 loại thuốc sắp hết hạn") để họ click vào xem.
4.  **Audit Trail (Truy vết):** Mọi thay đổi về số lượng thuốc (nhập, xuất, hủy) phải được ghi log (Ngày, Giờ, Lý do, User). Rất quan trọng khi đối soát lệch kho.

## 5. TÍNH NĂNG ĐỀ XUẤT

### 🚀 MVP (Bắt buộc có - Phase 1):
- [ ] **Quản lý Danh mục & Tồn kho cơ bản:** Thêm/Sửa/Xóa thuốc, thiết lập số lượng tồn kho đầu kỳ.
- [ ] **Tự động trừ kho (Auto-deduction):** Tự động trừ số lượng thuốc trong kho khi bác sĩ lưu đơn thuốc.
- [ ] **Cảnh báo tồn tối thiểu:** Đặt ngưỡng (VD: < 5 hộp thì hiện màu đỏ cảnh báo cần nhập thêm).
- [ ] **Thống kê cơ bản:** Báo cáo xem loại thuốc nào dùng nhiều nhất trong tháng.

### 🎁 Nâng cao (Phase 2):
- [ ] **Quản lý Lô & Hạn sử dụng (FEFO):** Quản lý thuốc theo từng đợt nhập (Ngày nhập, HSD). Cảnh báo thuốc sắp hết hạn (VD: trước 30 ngày).
- [ ] **Nhập hàng & Quản lý Nhà cung cấp:** Tạo phiếu nhập kho, theo dõi giá nhập vs giá bán để tính lợi nhuận gộp.
- [ ] **Audit Log (Lịch sử kho):** Ghi nhận chi tiết: Thuốc A tăng 100 viên (Nhập kho), Thuốc A giảm 10 viên (Theo toa bệnh nhân XYZ).
- [ ] **Biểu đồ & Analytics:** Biểu đồ doanh thu tiền thuốc, dự báo nhu cầu thuốc tháng tới dựa trên AI/Thống kê.
- [ ] **Hỗ trợ Barcode:** Quét mã vạch thuốc để nhập/xuất kho nhanh mà không cần gõ tên. (Tính năng xịn xò thường thấy ở các app lớn).

## 6. ƯỚC TÍNH SƠ BỘ
- **Độ phức tạp:** **Trung Khá**. Phần khó nhất là thiết kế lại Database Schema để hỗ trợ việc quản lý theo Lô (Batch) nếu chọn làm (thay vì chỉ lưu 1 biến quantity ở bảng thuốc hiện tại). Phần đồng bộ Supabase cần đặc biệt lưu ý Constraint.
- **Rủi ro:** Khi cập nhật app lên bản mới có tính năng kho, phải viết script Data Migration để cấp số lượng tồn kho ban đầu (hoặc set = 0) cho các phòng khám đang dùng bản v5.0.6 hiện tại.

## 7. BƯỚC TIẾP THEO
→ Anh xem danh sách tính năng trên, phần MVP có đủ dùng trước chưa, hay anh muốn thêm bớt gì không?
