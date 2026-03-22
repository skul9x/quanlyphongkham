# 🎨 DESIGN: Bộ lọc tồn kho màn hình Thuốc

**Ngày tạo:** 2026-03-11
**Dựa trên:** `docs/BRIEF_Medicine_Filter.md`

---

## 1. PHẦN 1: CÁCH LƯU THÔNG TIN (Dữ liệu)

### State Management (Trạng thái giao diện bộ lọc)
Sự kết hợp giữa Nguồn dữ liệu mộc và Tiêu chí của người dùng:
- `self.all_medicines_data` (Biến) chứa danh sách toàn bộ Thuốc tải từ DB.
- `search_input` (Ô nhập liệu): Chứa văn bản tìm kiếm theo Tên không dấu hoặc có dấu.
- `filter_combo` (Hộp chọn MỚI): Chứa trạng thái hiện tại (`All`, `InStock`, `LowStock`, `OutOfStock`).

Mỗi khi người dùng gõ tìm kiếm TRÙNG LÚC chọn Filter, giao diện sẽ ghép cả 2 điều kiện này để cho ra danh sách `filtered` cuối cùng.

---

## 2. PHẦN 2: THÀNH PHẦN HIỂN THỊ (UI Components Mới)

| # | Tên Component | Chứa đựng | Nhiệm vụ (Event) |
|---|---|---|---|
| 1 | `QComboBox` | Nằm cạnh ô Tìm kiếm. Có 4 tùy chọn: Tất cả trạng thái (0), Còn hàng (1), Sắp hết (2), Hết kho (3). | Lắng nghe `currentIndexChanged` -> gọi hàm `apply_filters()`. |
| 2 | Biển Cảnh Báo (`QFrame` / `QLabel`) | Hiện đang là tĩnh. Sẽ bọc thêm sự kiện `mousePressEvent`. Cập nhật khi con trỏ lướt ngang thành hình "bàn tay". | Khi người dùng Click chuột trái -> Đổi Index của `QComboBox` sang số 3 (hoặc 2) -> gọi hàm `apply_filters()`. |

---

## 3. PHẦN 3: LUỒNG HOẠT ĐỘNG (User Journey)

### Hành trình 1: Bác sĩ lọc thuốc khi Cảnh báo chớp đỏ
1️⃣ Bác sĩ mở màn hình Kho Thuốc.\
2️⃣ Đập vào mắt là biển báo "CẢNH BÁO: 109 thuốc hết kho".\
3️⃣ Bác sĩ TÒ MÒ nhấp chuột trái vào tấm biển (Không cần thao tác lên ô Dropdown).\
4️⃣ Danh sách lập tức Rút gọn chỉ còn 109 bài thuốc kia.\
5️⃣ Ở kế bên, Hộp chọn thả xuống tự động nhảy chữ sang "Hết kho" để khớp với logic.

### Hành trình 2: Quản lý phòng khám chủ động kiểm kê
1️⃣ Quản lý mở thanh Thả xuống (Dropdown) chọn "Sắp hết".\
2️⃣ Kéo chuột xuống ô "Tìm kiếm", gõ chữ "pana".\
3️⃣ App tự động chắt lọc ra các thuốc vừa Tên có chữ "pana" VỪA có số lượng <= Tồn tối thiểu.

---

## 4. PHẦN 4: CHECKLIST KIỂM TRA (Test Cases)

### 📋 TC-01: Bộ lọc Hộp Chọn Cơ Bản (Happy Path)
- **Given:** Người dùng mở Kho thuốc. Đang có nhiều loại thuốc (cả còn hàng và hết hàng).
- **When:** Người dùng lần lượt đổi Hộp chọn qua 4 trạng thái.
- **Then:**
    - [ ] `Còn hàng` -> Ẩn thuốc Hết (X) hoặc Sắp hết (Cảnh báo).
    - [ ] `Sắp hết` -> Chỉ hiện thuốc có Tồn Kho <= Tồn Tối Thiểu & > 0.
    - [ ] `Hết kho` -> Chỉ hiện thuốc có Tồn kho <= 0.
    - [ ] `Tất cả` -> Hiện đủ.

### 📋 TC-02: Lọc Kết Hợp
- **Given:** Người dùng chọn bộ lọc `Hết kho` từ Hộp chọn.
- **When:** Người dùng gõ tên "Amox" vào ô Truy vấn Tên.
- **Then:**
    - [ ] Các loại Amox không bị hết kho KHÔNG hiển thị.
    - [ ] Chỉ hiển thị Amox ĐÃ CHÁY HÀNG.
    - [ ] Xóa chữ "Amox" thì nó nhả về toàn bộ danh sách Hết kho.

### 📋 TC-03: Click Cảnh Báo (Đỉnh cao User Experience)
- **Given:** Màn hình có cảnh báo "CẢNH BÁO: X loại đã Hết Kho" đang bật.
- **When:** Người dùng bấm vào khung cảnh báo đó.
- **Then:**
    - [ ] Hộp chọn `QComboBox` lập tức nhảy sang Index "Hết Kho" (số 3).
    - [ ] Danh sách rà lại tự động chỉ hiện X loại thuốc hết kho đó.
    - [ ] (Edge Case) Nếu chỉ có thông báo "Sắp hết", click vào biển cảnh báo thì `QComboBox` nhảy về mục "Sắp hết" (số 2).
