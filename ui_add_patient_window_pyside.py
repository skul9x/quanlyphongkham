from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QFormLayout, QMessageBox
)
from PySide6.QtCore import Qt
from datetime import datetime
import database
from animation_helper import AnimationHelper

class AddPatientWindow(QDialog):
    def __init__(self, parent=None, on_success_callback=None):
        super().__init__(parent)
        self.on_success_callback = on_success_callback
        self.setWindowTitle("Thêm Bệnh Nhân Mới")
        self.setModal(True)
        self.setFixedSize(500, 500)
        # Removed hardcoded background color
        # self.setStyleSheet("background-color: #f8fafc;")
        self.setup_ui()

    def showEvent(self, event):
        super().showEvent(event)
        AnimationHelper.animate_dialog_open(self)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Thông Tin Bệnh Nhân")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: 800; margin-bottom: 10px;")
        layout.addWidget(title)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setSpacing(15)

        # Name (limit 200 chars to prevent UI freeze)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Nhập họ tên đầy đủ...")
        self.name_edit.setMaxLength(200)
        self.style_input(self.name_edit)
        form_layout.addRow(self.create_label("Họ tên (*):"), self.name_edit)

        # DOB
        dob_layout = QHBoxLayout()
        dob_layout.setSpacing(5)
        self.day_edit = self.create_date_input("DD", 2)
        self.month_edit = self.create_date_input("MM", 2)
        self.year_edit = self.create_date_input("YYYY", 4)
        
        dob_layout.addWidget(self.day_edit)
        dob_layout.addWidget(QLabel("/"))
        dob_layout.addWidget(self.month_edit)
        dob_layout.addWidget(QLabel("/"))
        dob_layout.addWidget(self.year_edit)
        form_layout.addRow(self.create_label("Ngày sinh:"), dob_layout)

        # Gender
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["Nam", "Nữ", "Khác"])
        self.style_input(self.gender_combo)
        form_layout.addRow(self.create_label("Giới tính:"), self.gender_combo)

        # Address (limit 500 chars)
        self.address_edit = QLineEdit()
        self.address_edit.setMaxLength(500)
        self.style_input(self.address_edit)
        form_layout.addRow(self.create_label("Địa chỉ:"), self.address_edit)

        # Phone (limit 15 chars)
        self.phone_edit = QLineEdit()
        self.phone_edit.setMaxLength(15)
        self.style_input(self.phone_edit)
        form_layout.addRow(self.create_label("Điện thoại:"), self.phone_edit)

        # Weight (limit 6 chars, e.g. "150.5")
        self.weight_edit = QLineEdit()
        self.weight_edit.setMaxLength(6)
        self.style_input(self.weight_edit)
        form_layout.addRow(self.create_label("Cân nặng (kg):"), self.weight_edit)

        # Diagnosis - Required field
        self.diagnosis_edit = QLineEdit()
        self.diagnosis_edit.setPlaceholderText("Nhập chẩn đoán bệnh...")
        self.diagnosis_edit.setMaxLength(500)
        self.style_input(self.diagnosis_edit)
        form_layout.addRow(self.create_label("Chẩn đoán (*):"), self.diagnosis_edit)

        layout.addLayout(form_layout)
        layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        self.btn_cancel = QPushButton("Hủy bỏ")
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        # Updated style to use theme colors
        self.btn_cancel.setStyleSheet("""
            QPushButton { 
                background-color: palette(base); 
                border: 1px solid palette(mid); 
                color: palette(text); 
                border-radius: 6px; 
                padding: 10px; 
                font-weight: 600; 
            }
            QPushButton:hover { background-color: palette(midlight); }
        """)
        self.btn_cancel.clicked.connect(self.reject)
        
        self.btn_save = QPushButton("Lưu Hồ Sơ")
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setStyleSheet("""
            QPushButton { background-color: #10b981; border: none; color: white; border-radius: 6px; padding: 10px; font-weight: 600; }
            QPushButton:hover { background-color: #059669; }
        """)
        self.btn_save.clicked.connect(self.accept_record)
        
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        layout.addLayout(btn_layout)
        
        self._bind_focus_events()

    def create_label(self, text):
        lbl = QLabel(text)
        # Removed explicit color, relies on theme
        lbl.setStyleSheet("font-weight: 600;")
        return lbl

    def style_input(self, widget):
        # Updated to use theme colors and fix text clipping
        widget.setStyleSheet("""
            QLineEdit, QComboBox {
                border: 1px solid palette(mid);
                border-radius: 6px;
                padding: 6px 12px;
                min-height: 24px;
                background-color: palette(base);
                color: palette(text);
                font-size: 14px;
            }
            QLineEdit:focus, QComboBox:focus { border: 2px solid #6366f1; padding: 5px 11px; }
        """)

    def create_date_input(self, placeholder, max_len):
        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        inp.setMaxLength(max_len)
        inp.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.style_input(inp)
        return inp

    def _bind_focus_events(self):
        self.day_edit.textChanged.connect(lambda t: self.month_edit.setFocus() if len(t) == 2 else None)
        self.month_edit.textChanged.connect(lambda t: self.year_edit.setFocus() if len(t) == 2 else None)
        self.year_edit.textChanged.connect(lambda t: self.gender_combo.setFocus() if len(t) == 4 else None)

    def accept_record(self):
        name = self.name_edit.text().strip().title()
        if not name:
            AnimationHelper.shake_widget(self.name_edit)
            self.name_edit.setFocus()
            return

        dob_iso = None
        d, m, y = self.day_edit.text(), self.month_edit.text(), self.year_edit.text()
        if d and m and y:
            try:
                dob_iso = datetime.strptime(f"{int(d):02d}/{int(m):02d}/{int(y):04d}", '%d/%m/%Y').strftime('%Y-%m-%d')
            except:
                AnimationHelper.shake_widget(self.day_edit)
                return

        # Validate diagnosis (required)
        diagnosis = self.diagnosis_edit.text().strip()
        if not diagnosis:
            AnimationHelper.shake_widget(self.diagnosis_edit)
            self.diagnosis_edit.setFocus()
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập chẩn đoán cho bệnh nhân!")
            return

        success = database.add_patient_db(
            name, dob_iso, self.gender_combo.currentText(),
            self.address_edit.text().strip(), self.phone_edit.text().strip(),
            self.weight_edit.text().strip().replace(',', '.'), diagnosis
        )
        
        if success:
            QMessageBox.information(self, "Thành công", "Đã thêm bệnh nhân mới.")
            if self.on_success_callback: self.on_success_callback()
            self.accept()
        else:
            QMessageBox.critical(self, "Lỗi", "Lỗi cơ sở dữ liệu.")