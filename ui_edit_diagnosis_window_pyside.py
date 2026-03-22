from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, 
    QTextEdit, QPushButton, QFormLayout, QMessageBox, QHBoxLayout
)
from PySide6.QtCore import Qt
import database
from animation_helper import AnimationHelper

class EditDiagnosisWindow(QDialog):
    def __init__(self, parent=None, visit_id=None, on_success_callback=None):
        super().__init__(parent)
        self.visit_id = visit_id
        self.on_success_callback = on_success_callback
        
        self.visit_data = database.get_patient_by_id(visit_id) if visit_id else None
        name = self.visit_data['name'] if self.visit_data else "Unknown"

        self.setWindowTitle(f"Sửa Chẩn Đoán - {name}")
        self.setModal(True)
        self.setFixedSize(600, 250)
        # self.setStyleSheet("background-color: #f8fafc;")
        self.setup_ui()

    def showEvent(self, event):
        super().showEvent(event)
        AnimationHelper.animate_dialog_open(self)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        title = QLabel("Sửa Chẩn Đoán")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: 800;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(15)
        
        self.weight_edit = QLineEdit()
        if self.visit_data: self.weight_edit.setText(str(self.visit_data['weight'] or ""))
        self.style_input(self.weight_edit)
        form.addRow(self.lbl("Cân nặng (kg):"), self.weight_edit)

        self.diagnosis_edit = QLineEdit()
        self.style_input(self.diagnosis_edit)
        form.addRow(self.lbl("Chẩn đoán:"), self.diagnosis_edit)
        
        layout.addLayout(form)
        
        if self.visit_data:
            hist = self.visit_data['medical_history'] or ""
            lines = hist.split('\n')
            if lines:
                self.diagnosis_edit.setText(lines[0])

        layout.addStretch()

        btn_row = QHBoxLayout()
        self.btn_cancel = QPushButton("Hủy")
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.setStyleSheet("""
            QPushButton { 
                background: palette(base); 
                border: 1px solid palette(mid); 
                border-radius: 6px; 
                padding: 10px; 
                font-weight: 600; 
                color: palette(text); 
            } 
            QPushButton:hover { background: palette(midlight); }
        """)
        self.btn_cancel.clicked.connect(self.reject)
        
        self.btn_save = QPushButton("Lưu Thay Đổi")
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setStyleSheet("QPushButton { background: #4f46e5; border: none; border-radius: 6px; padding: 10px; font-weight: 600; color: white; } QPushButton:hover { background: #4338ca; }")
        self.btn_save.clicked.connect(self.save)
        
        btn_row.addWidget(self.btn_cancel)
        btn_row.addWidget(self.btn_save)
        layout.addLayout(btn_row)

    def lbl(self, t):
        l = QLabel(t)
        l.setStyleSheet("font-weight: 600;")
        return l

    def style_input(self, w):
        w.setStyleSheet("""
            QLineEdit { 
                border: 1px solid palette(mid); 
                border-radius: 6px; 
                padding: 6px 12px;
                min-height: 24px;
                background: palette(base);
                color: palette(text);
                font-size: 14px;
            } 
            QLineEdit:focus { border: 2px solid #6366f1; padding: 5px 11px; }
        """)

    def save(self):
        w = self.weight_edit.text().strip().replace(',', '.')
        d = self.diagnosis_edit.text().strip()
        
        if not d:
            QMessageBox.warning(self, "Lỗi", "Chẩn đoán trống.")
            return
            
        if database.update_visit_details_db(self.visit_id, w, d):
            QMessageBox.information(self, "OK", "Đã cập nhật.")
            if self.on_success_callback: self.on_success_callback()
            self.accept()
        else:
            QMessageBox.critical(self, "Lỗi", "Lỗi DB.")