from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QGroupBox, QHBoxLayout, 
    QLabel, QRadioButton, QButtonGroup, QFrame, QLineEdit, QPushButton
)
from PySide6.QtCore import Qt
import config
import sqlite3
import os
import sys

def _validate_sqlite_file(file_path):
    """Validate that a file is a valid SQLite database.
    Returns: (is_valid: bool, error_message: str)
    """
    try:
        conn = sqlite3.connect(file_path)
        # Check SQLite integrity
        result = conn.execute("PRAGMA integrity_check").fetchone()
        if result[0] != "ok":
            conn.close()
            return False, "File database bị hỏng (integrity check failed)"
        
        # Optional: Check if it has expected tables
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        table_names = [t[0] for t in tables]
        conn.close()
        
        # Warn if it doesn't look like a clinic database
        expected_tables = ['patients', 'medicines']
        has_expected = any(t in table_names for t in expected_tables)
        
        if not has_expected:
            return True, (
                f"⚠️ File này không chứa bảng dữ liệu quen thuộc "
                f"(patients, medicines).\n"
                f"Các bảng tìm thấy: {', '.join(table_names) if table_names else '(trống)'}\n\n"
                f"Bạn vẫn muốn sử dụng file này?"
            )
        
        return True, ""
    except sqlite3.DatabaseError as e:
        return False, f"File không phải database SQLite hợp lệ:\n{str(e)}"
    except Exception as e:
        return False, f"Không đọc được file:\n{str(e)}"

class HelpTab(QWidget):
    def __init__(self, main_window=None):
        super().__init__(main_window)
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
        # Header
        header_label = QLabel("Trợ Giúp & Cài Đặt")
        header_label.setStyleSheet("font-size: 28px; font-weight: 800; background-color: transparent;")
        layout.addWidget(header_label)
        
        # General Settings Card
        gen_box = QGroupBox("Cài đặt chung")
        gen_layout = QVBoxLayout(gen_box)
        gen_layout.setContentsMargins(30, 20, 30, 20)
        gen_layout.setSpacing(15)
        
        # Row 1: App Title
        row1 = QHBoxLayout()
        lbl_title = QLabel("Tên hiển thị trên Menu:")
        lbl_title.setStyleSheet("font-weight: 600; font-size: 15px; background-color: transparent;")
        
        self.txt_app_title = QLineEdit()
        self.txt_app_title.setPlaceholderText("VD: PHÒNG KHÁM NHI ĐỒNG...")
        self.txt_app_title.setStyleSheet("padding: 5px; border: 1px solid #cbd5e1; border-radius: 4px;")
        if self.main_window:
             # Load current title from main window marquee label
             self.txt_app_title.setText(self.main_window.app_logo.text())

        btn_update_title = QPushButton("Cập nhật")
        btn_update_title.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_update_title.setFixedWidth(100)
        btn_update_title.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6; 
                color: white; 
                font-weight: bold; 
                border-radius: 4px; 
                padding: 6px;
            }
            QPushButton:hover { background-color: #2563eb; }
        """)
        btn_update_title.clicked.connect(self.update_app_title)

        row1.addWidget(lbl_title)
        row1.addWidget(self.txt_app_title)
        row1.addWidget(btn_update_title)
        gen_layout.addLayout(row1)

        # Row 2: Consultation Fee
        row2 = QHBoxLayout()
        lbl_fee = QLabel("Tiền công khám (VNĐ):")
        lbl_fee.setStyleSheet("font-weight: 600; font-size: 15px; background-color: transparent;")
        
        self.txt_fee = QLineEdit()
        self.txt_fee.setPlaceholderText("VD: 100000")
        self.txt_fee.setStyleSheet("padding: 5px; border: 1px solid #cbd5e1; border-radius: 4px;")
        from PySide6.QtGui import QIntValidator
        self.txt_fee.setValidator(QIntValidator(0, 9990000))
        self.txt_fee.setText(str(int(config.get_consultation_fee())))

        btn_update_fee = QPushButton("Lưu")
        btn_update_fee.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_update_fee.setFixedWidth(100)
        btn_update_fee.setStyleSheet("""
            QPushButton {
                background-color: #10b981; 
                color: white; 
                font-weight: bold; 
                border-radius: 4px; 
                padding: 6px;
            }
            QPushButton:hover { background-color: #059669; }
        """)
        btn_update_fee.clicked.connect(self.update_consultation_fee)
        
        row2.addWidget(lbl_fee)
        row2.addWidget(self.txt_fee)
        row2.addWidget(btn_update_fee)
        gen_layout.addLayout(row2)
                
        layout.addWidget(gen_box)

        # 🆕 Database Path Settings Card
        db_box = QGroupBox("Đường dẫn Database")
        db_layout = QVBoxLayout(db_box)
        db_layout.setContentsMargins(30, 20, 30, 20)
        db_layout.setSpacing(10)

        db_instr = QLabel("Cấu hình vị trí lưu trữ file dữ liệu (.db):")
        db_instr.setStyleSheet("color: #64748b; font-size: 13px; background-color: transparent;")
        db_layout.addWidget(db_instr)

        db_path_row = QHBoxLayout()
        self.txt_db_path = QLineEdit()
        self.txt_db_path.setReadOnly(True)
        self.txt_db_path.setText(config.get_database_path())
        self.txt_db_path.setStyleSheet("padding: 8px; border: 1px solid #cbd5e1; border-radius: 4px; background-color: #f8fafc;")
        
        btn_browse = QPushButton("Chọn...")
        btn_browse.setFixedWidth(100)
        btn_browse.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_browse.setStyleSheet("""
            QPushButton { background-color: #3b82f6; color: white; font-weight: bold; border-radius: 4px; padding: 8px; }
            QPushButton:hover { background-color: #2563eb; }
        """)
        btn_browse.clicked.connect(self.browse_db_path)

        btn_open_folder = QPushButton("📁")
        btn_open_folder.setFixedWidth(40)
        btn_open_folder.setToolTip("Mở thư mục chứa database")
        btn_open_folder.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_open_folder.setStyleSheet("""
            QPushButton { 
                background-color: #64748b; color: white; 
                font-weight: bold; border-radius: 4px; padding: 8px; 
                font-size: 14px;
            }
            QPushButton:hover { background-color: #475569; }
        """)
        btn_open_folder.clicked.connect(self.open_db_folder)

        db_path_row.addWidget(self.txt_db_path)
        db_path_row.addWidget(btn_browse)
        db_path_row.addWidget(btn_open_folder)
        db_layout.addLayout(db_path_row)

        btn_reset_db = QPushButton("Quay về mặc định (clinic.db)")
        btn_reset_db.setFixedWidth(200)
        btn_reset_db.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reset_db.setStyleSheet("""
            QPushButton { border: 1px solid #cbd5e1; border-radius: 4px; padding: 5px; color: #64748b; }
            QPushButton:hover { background-color: #f1f5f9; color: #1e293b; }
        """)
        btn_reset_db.clicked.connect(self.reset_db_path)
        
        btn_create_new = QPushButton("Tạo mới")
        btn_create_new.setFixedWidth(100)
        btn_create_new.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_create_new.setStyleSheet("""
            QPushButton { 
                border: 1px solid #3b82f6; border-radius: 4px; 
                padding: 5px; color: #3b82f6; 
                font-weight: 600;
            }
            QPushButton:hover { background-color: #eff6ff; }
        """)
        btn_create_new.clicked.connect(self.create_new_db)

        btn_row2 = QHBoxLayout()
        btn_row2.addWidget(btn_reset_db)
        btn_row2.addWidget(btn_create_new)
        btn_row2.addStretch()
        db_layout.addLayout(btn_row2)

        db_warn = QLabel("⚠️ Thay đổi cần khởi động lại ứng dụng để có hiệu lực.")
        db_warn.setStyleSheet("color: #e11d48; font-size: 12px; font-style: italic; background-color: transparent;")
        db_layout.addWidget(db_warn)

        layout.addWidget(db_box)

        # Theme Settings Card
        theme_box = QGroupBox("Giao diện ứng dụng")
        theme_layout = QHBoxLayout(theme_box)
        theme_layout.setContentsMargins(30, 30, 30, 30)
        theme_layout.setSpacing(20)
        
        lbl_theme = QLabel("Chế độ hiển thị:")
        # Added background-color: transparent to fix rendering issues in Dark Mode
        lbl_theme.setStyleSheet("font-weight: 600; font-size: 15px; background-color: transparent;")
        theme_layout.addWidget(lbl_theme)
        
        self.bg_theme = QButtonGroup(self)
        self.rb_light = self.create_radio("☀️ Sáng (Light Mode)")
        self.rb_dark = self.create_radio("🌙 Tối (Dark Mode)")
        
        self.bg_theme.addButton(self.rb_light, 0)
        self.bg_theme.addButton(self.rb_dark, 1)
        
        theme_layout.addWidget(self.rb_light)
        theme_layout.addWidget(self.rb_dark)
        theme_layout.addStretch()
        
        layout.addWidget(theme_box)

        # Check current theme
        if self.main_window:
            if self.main_window.current_theme == "dark":
                self.rb_dark.setChecked(True)
            else:
                self.rb_light.setChecked(True)
                
        self.bg_theme.buttonClicked.connect(self.on_theme_changed)

        # Document Content
        doc_group = QGroupBox("Hướng dẫn sử dụng")
        doc_layout = QVBoxLayout(doc_group)
        doc_layout.setContentsMargins(20, 20, 20, 20)

        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setFrameShape(QFrame.Shape.NoFrame)
        # Transparent background to inherit theme color
        text_edit.setStyleSheet("background-color: transparent; border: none;")
        
        # Simplified CSS that relies on default colors from Theme Manager
        help_content = f"""
        <style>
            h3 {{ margin-top: 20px; color: #4f46e5; }}
            li {{ margin-bottom: 8px; font-size: 14px; }}
            p {{ font-size: 14px; line-height: 1.6; }}
            b {{ font-weight: bold; }}
            .highlight {{ color: #059669; font-weight: bold; }}
        </style>
        
        <p>Phiên bản: <b>{config.APP_VERSION} (Cloud Sync Edition)</b></p>
        <p>Hệ thống Quản lý Phòng khám Nhi hiện đại, tích hợp công nghệ đám mây.</p>
        <hr>
        
        <h3>1. Quản lý Bệnh nhân & Khám bệnh</h3>
        <ul>
            <li><b>Hồ sơ điện tử:</b> Lưu trữ lịch sử khám, đơn thuốc và ghi chú chi tiết.</li>
            <li><b>Tìm kiếm thông minh:</b> Tìm nhanh theo Tên hoặc Số điện thoại (Ctrl+F).</li>
            <li><b>Tính liều tự động:</b> Hỗ trợ tính liều lượng thuốc dựa trên cân nặng của trẻ.</li>
        </ul>

        <h3>2. Kho Thuốc & Vật tư</h3>
        <ul>
            <li><b>Quản lý tồn kho:</b> Theo dõi nhập/xuất thuốc chính xác.</li>
            <li><b>Nhập Excel:</b> Tiết kiệm thời gian nhập liệu từ file có sẵn.</li>
        </ul>

        <h3>3. <span class="highlight">✨ MỚI: Đồng bộ Đám mây (Cloud Sync)</span></h3>
        <ul>
            <li><b>An toàn dữ liệu:</b> Tự động sao lưu lên Supabase Cloud. Mất máy tính <b>không mất dữ liệu</b>.</li>
            <li><b>Khôi phục tự động:</b> Cài lại phần mềm, dữ liệu sẽ tự động tải về đầy đủ.</li>
            <li><b>Two-Way Sync:</b> Cơ chế đồng bộ 2 chiều thông minh, đảm bảo dữ liệu luôn nhất quán.</li>
        </ul>

        <h3>4. <span class="highlight">📱 MỚI: Ứng dụng Di động (ClinicViewer)</span></h3>
        <ul>
            <li><b>Quản lý từ xa:</b> Theo dõi danh sách bệnh nhân và doanh thu ngay trên điện thoại Android.</li>
            <li><b>Đồng bộ tức thì:</b> Dữ liệu từ máy tính sẽ xuất hiện trên điện thoại trong vài giây.</li>
        </ul>
        
        <p style="opacity: 0.6; margin-top:30px; font-style: italic;">
            © Nguyễn Duy Trường - Hotline hỗ trợ: 0388.634.123<br>
            Email: skul9x@gmail.com
        </p>
        """
        text_edit.setHtml(help_content)
        
        doc_layout.addWidget(text_edit)
        
        # Set stretch=1 để khung hướng dẫn chiếm hết khoảng trống còn lại
        layout.addWidget(doc_group, 1) 
        # layout.addStretch() -> Bỏ dòng này để không bị ép co lại

    def create_radio(self, text):
        rb = QRadioButton(text)
        rb.setCursor(Qt.CursorShape.PointingHandCursor)
        # Added background-color: transparent
        rb.setStyleSheet("""
            QRadioButton { font-size: 15px; spacing: 8px; background-color: transparent; }
            QRadioButton::indicator { width: 18px; height: 18px; }
        """)
        return rb

    def on_theme_changed(self, button):
        if not self.main_window: return
        if button == self.rb_light:
            self.main_window.set_theme("light")
        elif button == self.rb_dark:
            self.main_window.set_theme("dark")

    def update_app_title(self):
        if not self.main_window: return
        new_title = self.txt_app_title.text().strip()
        if not new_title:
             # Revert if empty
             self.txt_app_title.setText(self.main_window.app_logo.text())
             return
             
        self.main_window.set_app_title(new_title)
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Thành công", "Đã cập nhật tên phòng khám!")

    def update_consultation_fee(self):
        if not self.main_window: return
        fee_str = self.txt_fee.text().strip()
        if not fee_str:
            fee_str = "0"
            self.txt_fee.setText("0")
        
        try:
            fee_val = float(fee_str)
            config.set_consultation_fee(fee_val)
            self.main_window.save_settings()
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Thành công", f"Đã cập nhật tiền công khám thành {int(fee_val):,} VNĐ!")
        except Exception:
            pass


    def browse_db_path(self):
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        
        # Mở FileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Chọn file Database", "", "Database files (*.db);;All files (*.*)"
        )
        if not file_path:
            return
        
        # ① Validate SQLite
        is_valid, message = _validate_sqlite_file(file_path)
        
        if not is_valid:
            QMessageBox.warning(self, "File không hợp lệ", message)
            return
        
        # ② Warning nếu file hợp lệ nhưng không phải clinic DB
        if message:  # has warning message
            reply = QMessageBox.question(
                self, "Cảnh báo",
                message,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        # ③ Confirmation dialog
        current_path = config.get_database_path()
        reply = QMessageBox.question(
            self, "Xác nhận chuyển Database",
            f"Bạn có chắc muốn chuyển sang database mới?\n\n"
            f"📂 Hiện tại: {current_path}\n"
            f"📂 Mới: {file_path}\n\n"
            f"Dữ liệu hiện tại sẽ không bị xóa,\n"
            f"nhưng ứng dụng sẽ đọc/ghi vào file mới.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # ④ Lưu
        config.set_database_path(file_path)
        self.txt_db_path.setText(file_path)
        if self.main_window:
            self.main_window.save_settings()
        QMessageBox.information(
            self, "Thành công", 
            "Đã lưu đường dẫn mới!\n"
            "Vui lòng khởi động lại ứng dụng để áp dụng thay đổi."
        )

    def reset_db_path(self):
        from PySide6.QtWidgets import QMessageBox
        
        # Chỉ cần confirm nếu đang dùng custom path
        if config.get_database_path_override():
            reply = QMessageBox.question(
                self, "Xác nhận",
                f"Quay về database mặc định?\n\n"
                f"📂 Đang dùng: {config.get_database_path()}\n"
                f"📂 Mặc định: {config.DATABASE_NAME}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        config.set_database_path(None)
        self.txt_db_path.setText(config.get_database_path())
        if self.main_window:
            self.main_window.save_settings()
        QMessageBox.information(self, "Thành công", 
            "Đã quay về mặc định!\nVui lòng khởi động lại ứng dụng để áp dụng thay đổi.")

    def open_db_folder(self):
        """Open the folder containing the current database file."""
        import subprocess
        import platform
        
        db_path = config.get_database_path()
        folder = os.path.dirname(db_path)
        
        if not os.path.exists(folder):
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Lỗi", f"Thư mục không tồn tại:\n{folder}")
            return
        
        # Cross-platform folder open
        system = platform.system()
        if system == "Linux":
            subprocess.Popen(["xdg-open", folder])
        elif system == "Darwin":  # macOS
            subprocess.Popen(["open", folder])
        elif system == "Windows":
            subprocess.Popen(["explorer", folder])

    def create_new_db(self):
        """Create a new empty database at a user-chosen location."""
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        import sqlite3
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Tạo Database mới", "clinic.db", 
            "Database files (*.db)"
        )
        if not file_path:
            return
        
        # Ensure .db extension
        if not file_path.endswith('.db'):
            file_path += '.db'
        
        # Check if file already exists
        if os.path.exists(file_path):
            reply = QMessageBox.question(
                self, "File đã tồn tại",
                f"File {os.path.basename(file_path)} đã tồn tại.\n"
                "Bạn muốn sử dụng file này thay vì tạo mới?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        else:
            # Create empty SQLite file
            try:
                conn = sqlite3.connect(file_path)
                conn.close()
            except Exception as e:
                QMessageBox.warning(self, "Lỗi", f"Không tạo được file:\n{str(e)}")
                return
        
        # Set as current DB
        config.set_database_path(file_path)
        self.txt_db_path.setText(file_path)
        if self.main_window:
            self.main_window.save_settings()
        QMessageBox.information(
            self, "Thành công", 
            f"Đã tạo database mới tại:\n{file_path}\n\n"
            "Vui lòng khởi động lại ứng dụng để áp dụng thay đổi.\n"
            "(Ứng dụng sẽ tự tạo các bảng dữ liệu khi khởi động)"
        )