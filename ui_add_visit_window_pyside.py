from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QTextEdit, QPushButton, QFormLayout, QMessageBox
)
from PySide6.QtCore import Qt
import database
from animation_helper import AnimationHelper

class AddVisitWindow(QDialog):
    def __init__(self, parent=None, patient_info=None, on_success_callback=None):
        super().__init__(parent)
        self.patient_info = patient_info
        self.on_success_callback = on_success_callback
        
        name = patient_info['name'] if patient_info else "Unknown"
        self.setWindowTitle(f"Thêm Lượt Khám - {name}")
        self.setModal(True)
        self.setFixedSize(550, 450)
        # self.setStyleSheet("background-color: #f8fafc;")
        self.setup_ui()

    def showEvent(self, event):
        super().showEvent(event)
        AnimationHelper.animate_dialog_open(self)

    def _stop_animations(self):
        """Dừng tất cả animation trước khi đóng dialog để ngăn crash."""
        try:
            if hasattr(self, '_open_anim') and self._open_anim:
                self._open_anim.stop()
                self._open_anim = None
        except RuntimeError:
            pass
        # Gỡ graphics effect nếu còn
        self.setGraphicsEffect(None)

    def reject(self):
        self._stop_animations()
        super().reject()

    def accept(self):
        self._stop_animations()
        super().accept()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header
        header = QLabel("Thông Tin Lượt Khám")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("font-size: 18px; font-weight: 800;")
        layout.addWidget(header)

        form = QFormLayout()
        form.setSpacing(15)
        
        self.weight_edit = QLineEdit()
        if self.patient_info and self.patient_info['weight']:
             self.weight_edit.setText(str(self.patient_info['weight']))
        self.style_input(self.weight_edit)
        form.addRow(self.create_label("Cân nặng (kg):"), self.weight_edit)

        self.diagnosis_edit = QTextEdit()
        self.diagnosis_edit.setPlaceholderText("Nhập chẩn đoán lâm sàng...")
        # Updated style
        self.diagnosis_edit.setStyleSheet("""
            QTextEdit {
                border: 1px solid palette(mid); 
                border-radius: 6px; 
                padding: 10px; 
                background: palette(base);
                color: palette(text);
            }
            QTextEdit:focus { border: 2px solid #6366f1; padding: 9px; }
        """)
        form.addRow(self.create_label("Chẩn đoán (*):"), self.diagnosis_edit)

        layout.addLayout(form)
        layout.addStretch()

        # Actions
        btn_row = QHBoxLayout()
        btn_row.setSpacing(15)

        self.btn_cancel = QPushButton("Hủy")
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        # FIX: Tắt autoDefault để Enter không trigger nút Hủy
        self.btn_cancel.setAutoDefault(False)
        self.btn_cancel.setDefault(False)
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

        self.btn_save = QPushButton("Lưu Lượt Khám")
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        # FIX: Đặt làm default button để Enter trigger Lưu
        self.btn_save.setDefault(True)
        self.btn_save.setStyleSheet("""
            QPushButton { background-color: #4f46e5; border: none; color: white; border-radius: 6px; padding: 10px; font-weight: 600; }
            QPushButton:hover { background-color: #4338ca; }
        """)
        self.btn_save.clicked.connect(self.save_visit)

        btn_row.addWidget(self.btn_cancel)
        btn_row.addWidget(self.btn_save)
        layout.addLayout(btn_row)

    def create_label(self, text):
        l = QLabel(text)
        l.setStyleSheet("font-weight: 600;")
        return l

    def style_input(self, w):
        w.setStyleSheet("""
            QLineEdit { 
                border: 1px solid palette(mid); 
                border-radius: 6px; 
                padding: 8px; 
                background: palette(base);
                color: palette(text);
            }
            QLineEdit:focus { border: 2px solid #6366f1; padding: 7px; }
        """)

    def save_visit(self):
        diag = self.diagnosis_edit.toPlainText().strip()
        if not diag:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập chẩn đoán.")
            self.diagnosis_edit.setFocus()
            return

        weight = self.weight_edit.text().strip().replace(',', '.')
        
        success = database.add_patient_db(
            self.patient_info['name'], self.patient_info['dob'],
            self.patient_info['gender'], self.patient_info['address'],
            self.patient_info['phone'], weight, diag
        )

        if success:
            QMessageBox.information(self, "Thành công", "Đã thêm lượt khám.")
            if self.on_success_callback: self.on_success_callback()
            self.accept()
        else:
            QMessageBox.critical(self, "Lỗi", "Lỗi database.")