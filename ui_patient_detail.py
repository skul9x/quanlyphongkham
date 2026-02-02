from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, 
    QGroupBox, QFrame, QGridLayout, QStackedWidget
)
from PySide6.QtCore import Qt, Signal
from ux_components import EmptyStateWidget, AnimatedButton
from animation_helper import AnimationHelper
import utils

class PatientDetailWidget(QWidget):
    action_visit_clicked = Signal()
    action_prescribe_clicked = Signal()
    action_history_clicked = Signal()
    action_edit_clicked = Signal()
    action_diagnosis_clicked = Signal()
    action_delete_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.stack = QStackedWidget()
        
        self.empty_state = EmptyStateWidget("Chọn một bệnh nhân để xem hồ sơ chi tiết", "👤")
        self.stack.addWidget(self.empty_state)
        
        self.profile_scroll = QScrollArea()
        self.profile_view = QWidget()
        self.profile_scroll.setWidget(self.profile_view)
        self.profile_scroll.setWidgetResizable(True)
        self.profile_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.profile_scroll.setStyleSheet("background-color: transparent;")
        
        self.setup_profile_view()
        self.stack.addWidget(self.profile_scroll)
        
        main_layout.addWidget(self.stack)

    def setup_profile_view(self):
        profile_layout = QVBoxLayout(self.profile_view)
        profile_layout.setContentsMargins(40, 40, 40, 40)
        profile_layout.setSpacing(25)
        
        header_card = QFrame()
        header_card.setStyleSheet("background: transparent; border: none;")
        h_layout = QHBoxLayout(header_card)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(20)
        
        lbl_avatar = QLabel("🏥")
        lbl_avatar.setFixedSize(64, 64)
        lbl_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_avatar.setStyleSheet("font-size: 32px; background-color: rgba(224, 231, 255, 0.9); border-radius: 32px; border: 1px solid #c7d2fe; color: #1e293b;")
        
        name_col = QVBoxLayout()
        name_col.setSpacing(4)
        self.lbl_name = QLabel("---")
        self.lbl_name.setStyleSheet("font-size: 24px; font-weight: 800; border: none;")
        self.lbl_meta = QLabel("ID: #--- • Ngày khám gần nhất: ---")
        self.lbl_meta.setStyleSheet("font-size: 13px; opacity: 0.7; border: none;")
        name_col.addWidget(self.lbl_name)
        name_col.addWidget(self.lbl_meta)
        
        h_layout.addWidget(lbl_avatar)
        h_layout.addLayout(name_col)
        h_layout.addStretch()
        
        profile_layout.addWidget(header_card)
        
        action_box = QGroupBox("Tác vụ nhanh")
        btn_grid = QGridLayout(action_box)
        btn_grid.setSpacing(12)
        
        self.btn_visit = self.create_action_btn("Thêm lượt khám", "🩺", "#10b981", self.action_visit_clicked)
        # Make "Thêm lượt khám" button stand out as primary action
        self.btn_visit.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                border: 1px solid #059669;
                color: white;
                text-align: left;
                padding-left: 15px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #059669;
                border: 1px solid #047857;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
        """)
        self.btn_prescribe = self.create_action_btn("Kê đơn thuốc", "💊", "#4f46e5", self.action_prescribe_clicked)
        self.btn_history = self.create_action_btn("Lịch sử thuốc", "📜", "#f59e0b", self.action_history_clicked)
        self.btn_edit = self.create_action_btn("Sửa thông tin", "✏️", "#64748b", self.action_edit_clicked)
        self.btn_diag = self.create_action_btn("Sửa chẩn đoán + Đơn thuốc", "📝", "#64748b", self.action_diagnosis_clicked)
        self.btn_delete = self.create_action_btn("Xóa hồ sơ", "🗑️", "#ef4444", self.action_delete_clicked)
        
        btn_grid.addWidget(self.btn_visit, 0, 0)
        btn_grid.addWidget(self.btn_prescribe, 0, 1)
        btn_grid.addWidget(self.btn_history, 0, 2)
        btn_grid.addWidget(self.btn_edit, 1, 0)
        btn_grid.addWidget(self.btn_diag, 1, 1)
        btn_grid.addWidget(self.btn_delete, 1, 2)
        
        profile_layout.addWidget(action_box)
        
        info_box = QGroupBox("Thông tin cá nhân")
        info_grid = QGridLayout(info_box)
        info_grid.setHorizontalSpacing(40)
        info_grid.setVerticalSpacing(15)
        
        self.lbl_dob = self.add_info_row(info_grid, 0, 0, "Ngày sinh:")
        self.lbl_gender = self.add_info_row(info_grid, 0, 1, "Giới tính:")
        self.lbl_phone = self.add_info_row(info_grid, 1, 0, "Điện thoại:")
        self.lbl_address = self.add_info_row(info_grid, 1, 1, "Địa chỉ:")
        self.lbl_weight = self.add_info_row(info_grid, 2, 0, "Cân nặng/Dị ứng:")
        
        profile_layout.addWidget(info_box)
        
        clinical_box = QGroupBox("Lâm sàng")
        c_layout = QVBoxLayout(clinical_box)
        
        c_layout.addWidget(QLabel("Chẩn đoán:"))
        self.lbl_diagnosis = QLabel("---")
        self.lbl_diagnosis.setWordWrap(True)
        self.lbl_diagnosis.setStyleSheet("background-color: palette(base); padding: 10px; border-radius: 6px; font-style: italic; border: 1px solid palette(mid);")
        c_layout.addWidget(self.lbl_diagnosis)
        
        c_layout.addSpacing(10)
        c_layout.addWidget(QLabel("Đơn thuốc hiện tại:"))
        self.lbl_medicine = QLabel("---")
        self.lbl_medicine.setWordWrap(True)
        self.lbl_medicine.setStyleSheet("background-color: palette(base); padding: 10px; border-radius: 6px; font-family: monospace; border: 1px solid palette(mid);")
        c_layout.addWidget(self.lbl_medicine)
        
        profile_layout.addWidget(clinical_box)
        profile_layout.addStretch()

    def create_action_btn(self, text, icon, color, signal):
        btn = AnimatedButton(f"{icon}  {text}")
        btn.setFixedHeight(40)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: palette(base);
                border: 1px solid palette(mid);
                color: palette(text);
                text-align: left;
                padding-left: 15px;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {color};
                color: white;
                border: 1px solid {color};
            }}
        """)
        btn.clicked.connect(signal.emit)
        return btn

    def add_info_row(self, layout, row, col, label_text):
        container = QWidget()
        v_layout = QVBoxLayout(container)
        v_layout.setContentsMargins(0, 0, 0, 0)
        v_layout.setSpacing(2)
        
        lbl_caption = QLabel(label_text)
        lbl_caption.setStyleSheet("font-size: 12px; font-weight: 600; text-transform: uppercase; border: none; opacity: 0.7;")
        
        lbl_value = QLabel("---")
        lbl_value.setStyleSheet("font-size: 15px; font-weight: 500; border: none;")
        
        v_layout.addWidget(lbl_caption)
        v_layout.addWidget(lbl_value)
        
        layout.addWidget(container, row, col)
        return lbl_value

    def update_data(self, p):
        if not p:
            self.stack.setCurrentWidget(self.empty_state)
            return
            
        self.lbl_name.setText(p['name'])
        self.lbl_meta.setText(f"ID: #{p['id']} • Khám lúc: {p['created_at']}")
        self.lbl_dob.setText(utils.format_date_dmy(p['dob']) + f" ({utils.calculate_age(p['dob'])})")
        self.lbl_gender.setText(p['gender'])
        self.lbl_phone.setText(p['phone'])
        self.lbl_address.setText(p['address'])
        self.lbl_weight.setText(str(p['weight'] or "Không"))
        
        history = p['medical_history'] or ""
        parts = history.split('\n', 1)
        self.lbl_diagnosis.setText(parts[0] if parts else "Chưa có chẩn đoán")
        self.lbl_medicine.setText(parts[1] if len(parts) > 1 else "Chưa kê đơn")
        
        self.stack.setCurrentWidget(self.profile_scroll)
        self.profile_view.setVisible(True)
        self.profile_view.adjustSize()