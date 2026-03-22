# 🎨 DESIGN: Quản lý & Thống kê Thuốc (Medication Inventory)

Ngày tạo: 2026-03-11  
Dựa trên: [BRIEF_Thuoc.md](file:///home/skul9x/Desktop/Test_code/quanlyphongkham-Supabase-v2/docs/BRIEF_Thuoc.md) + [implementation_plan.md](file:///home/skul9x/.gemini/antigravity/brain/e83665d1-a38c-4fc3-a247-6072d952ff3e/implementation_plan.md)

---

## 1. Cách Lưu Thông Tin (Database Schema Changes)

### 1.1. Bảng `medicines` — TRƯỚC VÀ SAU

```
┌─────────────────────────────────────────────────────────────┐
│  💊 MEDICINES (Kho thuốc) — HIỆN TẠI                        │
│  ├── id          (Mã thuốc, tự tăng)                        │
│  ├── name        (Tên thuốc, duy nhất)                      │
│  ├── packing_spec (Quy cách: Viên, Vỉ, Chai...)            │
│  └── price       (Giá bán, VNĐ)                            │
└─────────────────────────────────────────────────────────────┘

                        ↓ THÊM 2 CỘT MỚI ↓

┌─────────────────────────────────────────────────────────────┐
│  💊 MEDICINES (Kho thuốc) — SAU KHI NÂNG CẤP               │
│  ├── id              (Mã thuốc, tự tăng)                    │
│  ├── name            (Tên thuốc, duy nhất)                  │
│  ├── packing_spec    (Quy cách: Viên, Vỉ, Chai...)         │
│  ├── price           (Giá bán, VNĐ)                        │
│  ├── stock_quantity  🆕 (Số lượng tồn kho, mặc định: 0)    │
│  └── min_stock_level 🆕 (Ngưỡng cảnh báo, mặc định: 5)    │
└─────────────────────────────────────────────────────────────┘
```

### 1.2. SQL Migration (Local SQLite)

```sql
-- Idempotent migration: chỉ chạy nếu cột chưa tồn tại
-- Pattern: kiểm tra PRAGMA table_info(medicines) trước
ALTER TABLE medicines ADD COLUMN stock_quantity INTEGER DEFAULT 0;
ALTER TABLE medicines ADD COLUMN min_stock_level INTEGER DEFAULT 5;
```

### 1.3. SQL Migration (Supabase Cloud)

```sql
-- Chạy trên Supabase Dashboard > SQL Editor
ALTER TABLE medicines ADD COLUMN IF NOT EXISTS stock_quantity INTEGER DEFAULT 0;
ALTER TABLE medicines ADD COLUMN IF NOT EXISTS min_stock_level INTEGER DEFAULT 5;
```

### 1.4. Quan hệ giữa các bảng (Không thay đổi)

```
medicines ──────────────┐
  (id, name, price,     │
   stock_quantity 🆕,   │ 1 thuốc có thể xuất hiện
   min_stock_level 🆕)  │ trong nhiều đơn thuốc
                        ▼
prescription_details ───┐
  (medicine_id → FK)    │ 1 đơn thuốc có
  (quantity, unit_price)│ nhiều dòng chi tiết
                        ▼
prescriptions_header
  (patient_id → FK)
  (diagnosis, total_amount)
```

### 1.5. Hàm `insert_medicine_from_cloud()` — Cần cập nhật

```diff
- c.execute('''INSERT OR REPLACE INTO medicines (id, name, packing_spec, price)
-              VALUES (?, ?, ?, ?)''',
-           (data.get('id'), data.get('name'),
-            data.get('packing_spec'), data.get('price')))
+ c.execute('''INSERT OR REPLACE INTO medicines
+              (id, name, packing_spec, price, stock_quantity, min_stock_level)
+              VALUES (?, ?, ?, ?, ?, ?)''',
+           (data.get('id'), data.get('name'),
+            data.get('packing_spec'), data.get('price'),
+            data.get('stock_quantity', 0),
+            data.get('min_stock_level', 5)))
```

---

## 2. Danh Sách Màn Hình (Screen Changes)

### 2.1. Tab "Kho Thuốc" — Bổ sung cột + banner cảnh báo

```
┌─────────────────────────────────────────────────────────────────────┐
│  ⚠️ 3 loại thuốc sắp hết kho → [Xem chi tiết]         🆕 BANNER  │
├─────────────────────────────────────────────────────────────────────┤
│  Kho Thuốc                                     [📥 Nhập Excel]     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 🔍 Tìm tên thuốc...                                        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────┬──────────┬─────────┬──────────┬───────────┐      │
│  │ Tên thuốc    │ Quy cách │ Giá bán │ 🆕Tồn kho│ 🆕Tối thiểu│      │
│  ├──────────────┼──────────┼─────────┼──────────┼───────────┤      │
│  │ Panadol      │ Viên     │ 5,000   │   120    │    10     │      │
│  │ Amoxicillin  │ Viên     │ 3,000   │   ⚠️ 3  │    10     │ ← ĐỎ│
│  │ Vitamin C    │ Viên     │ 1,500   │   0 ❌   │     5     │ ← ĐỎ│
│  └──────────────┴──────────┴─────────┴──────────┴───────────┘      │
│                                                                     │
│  ┌─────────── Thông tin chi tiết ──────────────┐                   │
│  │  Tên thuốc (*): [____________]               │                   │
│  │  Quy cách:      [____________]               │                   │
│  │  Đơn giá (VNĐ): [____________]               │                   │
│  │  🆕 Tồn kho:    [____________]               │                   │
│  │  🆕 Tồn tối thiểu: [________]               │                   │
│  │                                               │                   │
│  │  [✨ Thêm thuốc mới]                         │                   │
│  └───────────────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────────┘
```

**Quy tắc highlight:**
- `stock_quantity <= min_stock_level` VÀ `stock_quantity > 0` → Nền **vàng nhạt** + icon ⚠️
- `stock_quantity == 0` → Nền **đỏ nhạt** + icon ❌
- Bình thường → Không highlight

### 2.2. Cửa sổ Kê Đơn — Thêm cảnh báo tồn kho

```
┌─────────────────────────────────────────────────────────────────────┐
│  Kê Đơn Thuốc: Nguyễn Văn A                                       │
│                                                                     │
│  🔍 [Nhập tên thuốc...]                                            │
│                                                                     │
│  ┌──────────────┬──────────┬─────────┬──────────────┐              │
│  │ Tên thuốc    │ Quy cách │ Giá     │ 🆕 Tồn kho  │              │
│  ├──────────────┼──────────┼─────────┼──────────────┤              │
│  │ Panadol      │ Viên     │ 5,000   │   120 ✅     │              │
│  │ Amoxicillin  │ Viên     │ 3,000   │   ⚠️ 3       │ ← Vàng     │
│  │ Vitamin C    │ Viên     │ 1,500   │   ❌ Hết     │ ← Đỏ       │
│  └──────────────┴──────────┴─────────┴──────────────┘              │
│                                                                     │
│  📋 Đơn thuốc hiện tại                                             │
│  ┌──────────────┬─────┬────────┬──────────┬──────┐                 │
│  │ Tên thuốc    │ SL  │ Đơn giá│ Thành tiền│ 🗑️  │                 │
│  ├──────────────┼─────┼────────┼──────────┼──────┤                 │
│  │ Amoxicillin  │ [5] │ 3,000  │ 15,000   │ Xóa  │                 │
│  │              │     │⚠️Kho:3 │          │      │ 🆕 Inline warn │
│  └──────────────┴─────┴────────┴──────────┴──────┘                 │
│                                                                     │
│  TỔNG CỘNG:                                    15,120 ₫            │
│                                                                     │
│  [☐ Kê tiếp đơn cũ]              [Hủy]  [HOÀN TẤT + LƯU]         │
└─────────────────────────────────────────────────────────────────────┘
```

**Quy tắc cảnh báo khi kê đơn:**
- Khi thêm thuốc vào đơn mà `stock_quantity == 0` → **QMessageBox.warning**: "Thuốc [X] đã hết kho (tồn: 0). Bạn vẫn muốn kê?"
- Khi `quantity > stock_quantity` → **Inline warning** dưới dòng thuốc: "⚠️ Kho chỉ còn [Y], kê [Z]"
- **KHÔNG CHẶN** kê đơn (cho phép kê quá kho — vì bác sĩ có thể mua bổ sung)

### 2.3. Tab "Thống kê" — Thêm nút "Thuốc dùng nhiều nhất"

```
┌─────────────────────────────────────────────────────────────────────┐
│  Báo Cáo & Thống Kê                                                │
│                                                                     │
│  [📅 Theo Ngày] [📅 Tuần] [📅 Tháng] [📅 Năm]                      │
│  [👶 Độ Tuổi]  [⚧ Giới Tính] [📍 Địa Điểm]  [💊 Thuốc] 🆕       │
│                                                                     │
│  Chọn tháng: [03/2026 ▼]                       🆕 (khi bấm 💊)    │
│                                                                     │
│  ┌────────────────────────┬──────────────┬──────────────┐          │
│  │ Tên thuốc              │ SL đã dùng   │ Tổng tiền    │          │
│  ├────────────────────────┼──────────────┼──────────────┤          │
│  │ Panadol                │     85       │   425,000    │          │
│  │ Amoxicillin            │     62       │   186,000    │          │
│  │ Vitamin C              │     50       │    75,000    │          │
│  ├────────────────────────┼──────────────┼──────────────┤          │
│  │ TỔNG CỘNG              │    197       │   686,000    │          │
│  └────────────────────────┴──────────────┴──────────────┘          │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Luồng Hoạt Động (User Flows)

### 3.1. Luồng 1: Nhập tồn kho ban đầu (Lần đầu cập nhật)

```
1️⃣ Mở app → Vào tab "Kho Thuốc"
2️⃣ Thấy tất cả thuốc tồn kho = 0 (vì là lần đầu)
3️⃣ Click vào thuốc "Panadol" → Form bên phải hiện thông tin
4️⃣ Nhập "Tồn kho": 200, "Tồn tối thiểu": 20
5️⃣ Bấm "💾 Cập nhật" → Số liệu lưu lại
6️⃣ Lặp lại cho các thuốc khác
```

### 3.2. Luồng 2: Kê đơn thuốc (Tự động trừ kho)

```
1️⃣ Vào tab "Bệnh nhân" → Chọn bệnh nhân → Bấm "Kê đơn thuốc"
2️⃣ Cửa sổ kê đơn mở ra
3️⃣ Tìm thuốc "Amoxicillin" (thấy cột Tồn kho: 50)
4️⃣ Double-click hoặc Enter → Thuốc vào đơn (SL = 1)
5️⃣ Tăng SL lên 10
   → ✅ Nếu kho đủ (50 > 10): Bình thường
   → ⚠️ Nếu kê nhiều hơn kho: Hiện cảnh báo inline "Kho chỉ còn 50"
6️⃣ Bấm "HOÀN TẤT + LƯU"
7️⃣ Hệ thống:
   - Lưu đơn thuốc (prescriptions_header + prescription_details)
   - Trừ kho: medicines.stock_quantity = 50 - 10 = 40
   - Sync lên Supabase
8️⃣ Quay về tab bệnh nhân → Đơn thuốc đã lưu
```

### 3.3. Luồng 3: Xem cảnh báo thuốc sắp hết

```
1️⃣ Mở app → Vào tab "Kho Thuốc"
2️⃣ Thấy banner: "⚠️ 3 loại thuốc sắp hết kho"
3️⃣ Nhìn xuống bảng → Các thuốc tồn thấp hiện nền đỏ/vàng
4️⃣ Click vào thuốc cần nhập → Sửa "Tồn kho" thành số mới
5️⃣ Bấm "💾 Cập nhật" → Cảnh báo biến mất (nếu đủ kho)
```

---

## 4. Checklist Kiểm Tra (Acceptance Criteria)

### ✅ Tính năng: Quản lý tồn kho

| # | Điều kiện | Loại |
|---|-----------|------|
| AC-01 | Thêm thuốc mới với tồn kho > 0 → Lưu đúng | Cơ bản |
| AC-02 | Sửa tồn kho thuốc cũ → Lưu đúng | Cơ bản |
| AC-03 | Nhập tồn kho âm → Hiện lỗi "Tồn kho phải >= 0" | Validation |
| AC-04 | Nhập tối thiểu âm → Hiện lỗi | Validation |
| AC-05 | Thuốc cũ (trước migration) → tồn kho = 0, tối thiểu = 5 | Data |

### ✅ Tính năng: Tự động trừ kho

| # | Điều kiện | Loại |
|---|-----------|------|
| AC-06 | Kê đơn 10 viên Panadol (kho 50) → Kho giảm xuống 40 | Core |
| AC-07 | Kê tiếp đơn cũ → Kho vẫn bị trừ đúng | Core |
| AC-08 | Kê đơn thuốc hết kho → Cảnh báo nhưng VẪN cho kê | UX |
| AC-09 | Kê đơn nhiều hơn tồn kho → Inline warning + kho có thể âm | UX |

### ✅ Tính năng: Cảnh báo

| # | Điều kiện | Loại |
|---|-----------|------|
| AC-10 | Thuốc `stock <= min_stock` → Nền vàng nhạt, icon ⚠️ | UI |
| AC-11 | Thuốc `stock == 0` → Nền đỏ nhạt, icon ❌ | UI |
| AC-12 | Banner hiện số lượng thuốc cần nhập thêm | UI |
| AC-13 | Sau khi cập nhật tồn kho đủ → Cảnh báo biến mất | UI |

### ✅ Tính năng: Thống kê

| # | Điều kiện | Loại |
|---|-----------|------|
| AC-14 | Bấm "💊 Thuốc" → Hiện bảng thuốc dùng nhiều nhất | Core |
| AC-15 | Lọc theo tháng/năm → Data thay đổi đúng | Filter |
| AC-16 | Tổng cộng ở cuối bảng → Đúng tổng SL + tổng tiền | Data |

---

## 5. Test Cases (Chuẩn bị kiểm tra)

### TC-01: Happy Path — Thêm thuốc mới có tồn kho

```
Given: User ở tab "Kho Thuốc", form trống
When:  Nhập: Tên="Thuốc ABC", Quy cách="Viên", Giá=5000,
       Tồn kho=100, Tối thiểu=10, bấm "Thêm thuốc mới"
Then:  ✓ Thuốc xuất hiện trong danh sách
       ✓ Cột "Tồn kho" hiện 100
       ✓ Cột "Tối thiểu" hiện 10
       ✓ Không highlight (kho đủ)
```

### TC-02: Kê đơn tự động trừ kho

```
Given: Thuốc "Panadol" tồn kho = 50
When:  Kê đơn cho bệnh nhân A, chọn Panadol x 10, bấm Lưu
Then:  ✓ Đơn thuốc lưu thành công
       ✓ Quay lại tab Kho Thuốc: Panadol tồn kho = 40
       ✓ Supabase: medicines.stock_quantity = 40
```

### TC-03: Cảnh báo khi thuốc hết kho

```
Given: Thuốc "Vitamin C" tồn kho = 0
When:  Mở cửa sổ kê đơn, double-click "Vitamin C"
Then:  ✓ QMessageBox warning: "Thuốc Vitamin C đã hết kho (tồn: 0). Vẫn muốn kê?"
       ✓ Bấm "Có" → Thuốc vào đơn bình thường
       ✓ Bấm "Không" → Không thêm vào đơn
```

### TC-04: Cảnh báo kê nhiều hơn tồn kho

```
Given: Thuốc "Amoxicillin" tồn kho = 3
When:  Thêm Amoxicillin vào đơn, tăng SL lên 10
Then:  ✓ Inline warning: "⚠️ Kho chỉ còn 3, kê 10"
       ✓ Vẫn cho phép lưu đơn
       ✓ Sau lưu: Amoxicillin tồn kho = -7 (âm)
```

### TC-05: Banner cảnh báo

```
Given: Có 2 thuốc: A (stock=3, min=5) và B (stock=0, min=5)
When:  Mở tab "Kho Thuốc"
Then:  ✓ Banner trên cùng: "⚠️ 2 loại thuốc sắp hết kho"
       ✓ Thuốc A: nền vàng nhạt
       ✓ Thuốc B: nền đỏ nhạt
```

### TC-06: Thống kê thuốc dùng nhiều

```
Given: Đã kê 5 đơn thuốc trong tháng 03/2026
When:  Vào tab Thống kê, bấm "💊 Thuốc", chọn tháng 03/2026
Then:  ✓ Bảng hiện đúng: Tên thuốc | SL đã dùng | Tổng tiền
       ✓ Sắp xếp giảm dần theo SL đã dùng
       ✓ Dòng TỔNG CỘNG đúng
```

### TC-07: Migration idempotent

```
Given: App đã chạy lần 1 (migration đã apply)
When:  Chạy app lần 2
Then:  ✓ Không lỗi "duplicate column"
       ✓ Dữ liệu tồn kho giữ nguyên
```

---

*Tạo bởi AWF 2.1 — Design Phase*
