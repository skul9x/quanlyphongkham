from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QGroupBox, QHBoxLayout, 
    QLabel, QRadioButton, QButtonGroup, QFrame, QLineEdit, QPushButton
)
from PySide6.QtCore import Qt
import config

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
        gen_layout = QHBoxLayout(gen_box)
        gen_layout.setContentsMargins(30, 30, 30, 30)
        gen_layout.setSpacing(20)
        
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

        gen_layout.addWidget(lbl_title)
        gen_layout.addWidget(self.txt_app_title)
        gen_layout.addWidget(btn_update_title)
        
        layout.addWidget(gen_box)

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