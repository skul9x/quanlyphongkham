# Cấu Trúc Dự Án Clinic Manager v4.4

Dự án được tổ chức theo cấu trúc phẳng (flat structure) để đơn giản hóa việc import và quản lý trong Python.

## 📂 Core Files
| File | Mô tả |
|------|-------|
| `main_pyside.py` | **Entry Point**. File chính để chạy ứng dụng. Khởi tạo MainWindow, setup theme và navigation. |
| `config.py` | Chứa các hằng số cấu hình (Version, Database path, Timezone, App Title...). |
| `database.py` | Layer xử lý Database (SQLite). Chứa tất cả hàm CRUD, Migration logic và Initializer. |
| `worker.py` | Xử lý đa luồng (QRunnable) để tránh treo UI khi thực hiện tác vụ nặng. |
| `utils.py` | Các hàm tiện ích chung (Format ngày tháng, tính toán tuổi, text helpers...). |

## 🎨 UI Modules (Giao diện)
Các file giao diện được tách theo chức năng (Modular UI):

| File | Màn hình / Chức năng |
|------|----------------------|
| `ui_patient_pyside.py` | **Tab Bệnh nhân**. Quản lý danh sách và hồ sơ bệnh nhân. |
| `ui_patient_list.py` | Widget danh sách bệnh nhân (Table view, Pagination, Search). |
| `ui_patient_detail.py` | Widget chi tiết hồ sơ bệnh nhân (Thông tin, Lịch sử khám). |
| `ui_medicine_pyside.py` | **Tab Kho thuốc**. Quản lý nhập/xuất/tồn thuốc. |
| `ui_stats_pyside.py` | **Tab Thống kê**. Báo cáo doanh thu, biểu đồ lượt khám. |
| `ui_prescription_window_pyside.py` | **Cửa sổ Kê đơn**. Giao diện chọn thuốc, tính liều, lưu đơn. |
| `ui_add_patient_window_pyside.py` | Dialog thêm bệnh nhân mới. |
| `ui_edit_visit_window_pyside.py` | Dialog sửa thông tin lượt khám (Hành chính). |
| `ui_add_visit_window_pyside.py` | Dialog thêm lượt khám mới (Tái khám). |
| `ui_dose_calculator_pyside.py` | Công cụ tính liều lượng thuốc (theo cân nặng/tuổi). |
| `ui_history_window_pyside.py` | Xem lịch sử đơn thuốc chi tiết. |

## 🧩 Components & Helpers
| File | Mô tả |
|------|-------|
| `ux_components.py` | Các custom widget tái sử dụng (Button, Card, SearchBar...). |
| `animation_helper.py` | Helper class để tạo hiệu ứng chuyển động, fade-in, slide... |
| `theme_manager_pyside.py` | Quản lý theme (Light/Dark node) và load stylesheet. |
| `modern_theme.py` | Định nghĩa màu sắc và style cho Dark Mode/Light Mode. |

## 💾 Data & Resources
| File | Mô tả |
|------|-------|
| `clinic.db` | SQLite Database chính. Chứa dữ liệu bệnh nhân, thuốc, đơn thuốc. |
| `settings.json` | Lưu cài đặt người dùng (Theme, Window size, Last opened...). |
| `drugs.json` | Dữ liệu thuốc mẫu (để import ban đầu). |
| `logo.ico` | Icon ứng dụng. |

## 🛠️ Build & Dist
| File | Mô tả |
|------|-------|
| `dong goi.txt` | Lệnh PyInstaller để đóng gói ứng dụng ra file .exe. |
| `.gitignore` | File cấu hình git ignore. |

---
**Lưu ý cho Developer:**
- Logic Database nằm hoàn toàn trong `database.py`. Không viết SQL queries trực tiếp trong UI files.
- UI sử dụng `PySide6`.
- Luôn update `APP_VERSION` trong `config.py` khi release.
