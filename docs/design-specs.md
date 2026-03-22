# Design Specifications: Tab Quản Lý Kho Thuốc

Dựa trên yêu cầu của User:
- **Focus:** Tab Kho Thuốc trước.
- **Vibe:** Sạch sẽ, đồng bộ với app hiện tại (PySide6 native).
- **Layout:** Cột mới (Tồn kho, Cảnh báo), Banner cố định trên cùng.

---

## 🎨 Color Palette (PySide6 / CSS tương đương)

Vì app dùng PySide6 với theme mặc định, ta sẽ tiêm stylesheet (CSS Pyside) vừa đủ để làm nổi bật cảnh báo mà KHÔNG phá vỡ theme của OS.

| Ý nghĩa | Mã màu (Light Mode) | Mã màu (Khuyên dùng cho Style) | Áp dụng ở đâu |
|---------|---------------------|--------------------------------|---------------|
| **Cảnh báo Nguy Hiểm (Hết kho)** | `#FEF2F2` (Nền), `#DC2626` (Chữ/Viền) | `rgba(220, 38, 38, 0.1)` (Nền row) | Nền của row trong TreeWidget khi Tồn kho = 0. Banner nền. |
| **Cảnh báo Chú ý (Sắp hết)** | `#FFFBEB` (Nền), `#D97706` (Chữ/Viền) | `rgba(217, 119, 6, 0.1)` (Nền row) | Nền của row trong TreeWidget khi 0 < Tồn kho <= Min. Banner nền. |
| **Chữ thông thường/Tiêu đề** | `#1F2937` | Màu mặc định OS | Text nội dung, Text tiêu đề form |
| **Border / Phân cách** | `#E5E7EB` | `#d1d5db` | Viền xung quanh Banner Alert |

*(Lưu ý cho /code: Trong PySide6, khi set background cho QTreeWidgetItem, dùng `QColor(254, 242, 242)` cho Đỏ và `QColor(255, 251, 235)` cho Vàng để text màu đen vẫn đọc rõ trên màn hình)*

## 📐 Layout Components

### 1. Banner Alert (Khung cảnh báo trên cùng)

**Đặc tả:**
- **Vị trí:** Ngay dưới `HeaderTitle` ("Quản Lý Danh Mục Thuốc"), chiếm full chiều ngang.
- **Loại Widget:** `QFrame` (chứa `QHBoxLayout`).
- **Nội dung:**
  - Icon: ⚠️ (Cảnh báo) hoặc ❌ (Báo động đỏ).
  - Label: Text in đậm (Bold), size to hơn body một chút (14px). Vd: `CÓ 2 LOẠI THUỐC ĐÃ HẾT KHO, 1 LOẠI SẮP HẾT!`
  - Nút (Tùy chọn): Có thể có nút X để tạm tắt (tùy vào /code).
- **Stylesheet (Gợi ý cho /code):**
  ```css
  QFrame#AlertBanner {
      background-color: #FEF2F2; /* Hoặc #FFFBEB tùy mức độ */
      border: 1px solid #F87171; /* Hoặc #FCD34D */
      border-radius: 6px;
      padding: 8px 12px;
      margin-bottom: 15px;
  }
  QLabel#AlertText {
      color: #991B1B; /* Hoặc #92400E */
      font-weight: bold;
      font-size: 14px;
  }
  ```

### 2. Danh sách Thuốc (TreeWidget)

**Đặc tả:**
- **Thêm cột:**
  - Cột 1: Tên thuốc (Stretch)
  - Cột 2: Quy cách
  - Cột 3: Giá bán
  - Cột 4: **Tồn kho** (ResizeToContents, Center Alignment) 🆕
  - Cột 5: **Tối thiểu** (ResizeToContents, Center Alignment) 🆕
- **Định dạng dữ liệu Tồn kho:**
  - Rất quan trọng: Chỉ hiển thị CON SỐ `(100)`, không gắn thêm chữ "viên" hay gì để tránh rối mắt. Cần highlight font đậm (`font.setBold(True)`) nếu nó gặp nguy hiểm (<= min).
- **Row Styling (Logical State):**
  - Trạng thái bình thường: Màu nền mặc định, font chữ mặc định.
  - Trạng thái **Nguy Hiểm (Tồn kho = 0)**:
    - Bôi màu nền cả dòng (`setBackground(0, QColor(...))`).
    - Thêm Icon ❌ hoặc text `0 (Hết)` vào cột "Tồn kho" cho rõ.
  - Trạng thái **Cảnh báo (0 < Tồn kho <= Min)**:
    - Bôi màu nền vàng nhạt.
    - Thêm Icon ⚠️.

### 3. Form hiển thị chi tiết (Bên dưới danh sách)

**Đặc tả:**
- Form Layout hiện tại là `QGridLayout`. Cần thêm 2 dòng mới:
  - Label: "Tồn kho hiện tại:" + `QLineEdit` (`stock_edit`) (chỉ cho phép nhập số).
  - Label: "Tồn tối thiểu (Ngưỡng cảnh báo):" + `QLineEdit` (`min_stock_edit`) (chỉ cho phép nhập số).
- **UX Constraint:** Cả 2 ô này bắt giá trị Mặc định là 0 và 5 nếu thêm mới.

---

## 🔄 Interaction Flow (Animation / Cảm giác)

- **Khi load form / Khi lọc tìm kiếm:** Tính toán số lượng thuốc sắp hết và HIỆN / ẨN Banner Alert một cách tự động. Không chuyển trang (Mượt mà).
- **Phản hồi khi lưu:** Giữ nguyên Toast message / QMessageBox gốc của app để đảm bảo sự đồng bộ. Không sáng tạo thêm popup màu mè.

## 📝 Chú ý cho Developer phase 03 (/code)

- Vui lòng đọc kỹ File này và tuân thủ các quy định về màu `QColor` để highlight các dòng dữ liệu trong TreeWidget. Mục tiêu là UI "Clean, Đồng bộ nhưng Bật lên được điểm cần chú ý".
