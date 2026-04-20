from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, 
    QLabel, QLineEdit, QComboBox, QPushButton, 
    QRadioButton, QButtonGroup, QFormLayout, QMessageBox
)
from PySide6.QtCore import Qt
import os
import json
import config
from animation_helper import AnimationHelper


class DrugEditorDialog(QDialog):
    def __init__(self, parent=None, drug_data=None):
        super().__init__(parent)
        self.drug_data = drug_data or {}
        self.setWindowTitle("Thêm/Sửa Thuốc")
        self.resize(400, 300)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        
        self.name_edit = QLineEdit(self.drug_data.get("name", ""))
        form.addRow("Tên thuốc:", self.name_edit)
        
        self.mg_edit = QLineEdit(str(self.drug_data.get("mg", "")))
        form.addRow("Hàm lượng (mg):", self.mg_edit)
        
        self.ml_edit = QLineEdit(str(self.drug_data.get("ml", "")))
        form.addRow("Trong (ml):", self.ml_edit)
        
        self.dose_edit = QLineEdit(str(self.drug_data.get("dose", "")))
        form.addRow("Liều chuẩn (mg/kg):", self.dose_edit)
        
        layout.addLayout(form)
        
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Lưu")
        self.btn_save.clicked.connect(self.accept)
        self.btn_cancel = QPushButton("Hủy")
        self.btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        layout.addLayout(btn_layout)
        
        self.style_inputs()

    def style_inputs(self):
        self.setStyleSheet("""
            QLineEdit { padding: 5px; border: 1px solid #ccc; border-radius: 4px; }
            QPushButton { padding: 5px 15px; border-radius: 4px; }
        """)

    def get_data(self):
        try:
            return {
                "name": self.name_edit.text().strip(),
                "mg": float(self.mg_edit.text().strip()),
                "ml": float(self.ml_edit.text().strip()),
                "dose": float(self.dose_edit.text().strip())
            }
        except ValueError:
            return None

class DoseCalculatorWindow(QDialog):
    def __init__(self, parent=None, patient_weight=None):
        super().__init__(parent)
        self.patient_weight = patient_weight
        self.setWindowTitle("Tính Liều Thuốc Nhi Khoa")
        self.resize(500, 550)
        # Removed hardcoded white background
        # self.setStyleSheet("background-color: #f8fafc;")
        self.drugs_data = self.load_drugs_data()
        self.setup_ui()

    def showEvent(self, event):
        super().showEvent(event)
        AnimationHelper.animate_dialog_open(self)

    def load_drugs_data(self):
        default_drugs = [
            {"name": "ZT-Amox", "mg": 200, "ml": 5, "dose": 50},
            {"name": "Cefdinir", "mg": 125, "ml": 5, "dose": 14},
            {"name": "Bactirid", "mg": 100, "ml": 5, "dose": 8},
            {"name": "ZiUSA", "mg": 200, "ml": 5, "dose": 10},
            {"name": "Biseptol", "mg": 240, "ml": 5, "dose": 48}
        ]
        try:
            # 1. Try Writable User Data path first
            user_drugs_path = os.path.join(config._DATA_DIR, "drugs.json")
            if os.path.exists(user_drugs_path):
                with open(user_drugs_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            
            # 2. Fallback: Try App Bundle path (bundled with the application)
            bundle_drugs_path = os.path.join(config._APP_DIR, "drugs.json")
            if os.path.exists(bundle_drugs_path):
                # Optional: Copy to data dir for future editing if in frozen mode
                if config._DATA_DIR != config._APP_DIR:
                    try:
                        import shutil
                        shutil.copy2(bundle_drugs_path, user_drugs_path)
                    except: pass
                
                with open(bundle_drugs_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading drugs.json: {e}")
        
        return default_drugs

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Title
        title = QLabel("Công Cụ Tính Liều")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: 800;")
        layout.addWidget(title)

        # Inputs Card
        input_group = QGroupBox("Thông số đầu vào")
        # Updated style to use transparent background and theme colors
        input_group.setStyleSheet("""
            QGroupBox { 
                border: 1px solid palette(mid); 
                border-radius: 8px; 
                margin-top: 1em; 
                padding: 15px; 
                background-color: palette(base);
            }
            QGroupBox::title { 
                subcontrol-origin: margin; 
                left: 10px; 
                font-weight: bold; 
                background-color: transparent;
                color: palette(text);
            }
        """)
        form = QFormLayout(input_group)
        form.setSpacing(15)
        
        self.drug_combo = QComboBox()
        self.drug_combo.addItem("-- Chọn thuốc mẫu --")
        for drug in self.drugs_data:
            self.drug_combo.addItem(drug["name"], drug)
        self.drug_combo.currentIndexChanged.connect(self.fill_drug_data)
        self.style_input(self.drug_combo)
        
        # Drug Selection Row with Buttons
        drug_row = QHBoxLayout()
        drug_row.addWidget(self.drug_combo, stretch=1)
        
        btn_style = """
            QPushButton { 
                font-weight: bold; 
                border: 1px solid #d1d5db;
                border-radius: 4px; 
                padding: 4px 8px;
                background-color: #f3f4f6;
                color: #111827;
                font-size: 14px;
            }
            QPushButton:hover { 
                background-color: #e5e7eb; 
                border-color: #9ca3af;
            }
        """
        
        self.btn_add = QPushButton("➕")
        self.btn_add.setToolTip("Thêm thuốc mới")
        self.btn_add.setStyleSheet(btn_style)
        self.btn_add.clicked.connect(self.add_drug)
        
        self.btn_edit = QPushButton("✏️")
        self.btn_edit.setToolTip("Sửa thuốc đang chọn")
        self.btn_edit.setStyleSheet(btn_style)
        self.btn_edit.clicked.connect(self.edit_drug)
        
        self.btn_del = QPushButton("🗑️")
        self.btn_del.setToolTip("Xóa thuốc đang chọn")
        self.btn_del.setStyleSheet(btn_style)
        self.btn_del.clicked.connect(self.delete_drug)
        
        drug_row.addWidget(self.btn_add)
        drug_row.addWidget(self.btn_edit)
        drug_row.addWidget(self.btn_del)
        
        form.addRow(self.label("Chọn thuốc mẫu:"), drug_row)
        
        self.mg_edit = QLineEdit()
        self.style_input(self.mg_edit)
        form.addRow(self.label("Hàm lượng (mg):"), self.mg_edit)
        
        self.ml_edit = QLineEdit()
        self.style_input(self.ml_edit)
        form.addRow(self.label("Trong (ml):"), self.ml_edit)
        
        self.dose_edit = QLineEdit()
        self.style_input(self.dose_edit)
        form.addRow(self.label("Liều chuẩn (mg/kg):"), self.dose_edit)
        
        self.weight_edit = QLineEdit()
        if self.patient_weight is not None:
            self.weight_edit.setText(str(self.patient_weight))
        self.style_input(self.weight_edit)
        form.addRow(self.label("Cân nặng (kg):"), self.weight_edit)
        
        layout.addWidget(input_group)

        # Frequency
        freq_layout = QHBoxLayout()
        freq_layout.addWidget(self.label("Chia liều:"))
        self.div_group = QButtonGroup(self)
        
        self.rb1 = QRadioButton("1 lần/ngày")
        self.rb1.setStyleSheet("font-weight: 500;")
        self.div_group.addButton(self.rb1, 1)
        freq_layout.addWidget(self.rb1)
        
        self.rb2 = QRadioButton("2 lần/ngày")
        self.rb2.setStyleSheet("font-weight: 500;")
        self.rb2.setChecked(True)
        self.div_group.addButton(self.rb2, 2)
        freq_layout.addWidget(self.rb2)
        
        self.rb3 = QRadioButton("3 lần/ngày")
        self.rb3.setStyleSheet("font-weight: 500;")
        self.div_group.addButton(self.rb3, 3)
        freq_layout.addWidget(self.rb3)
        
        freq_layout.addStretch()
        layout.addLayout(freq_layout)

        # Result Card
        res_group = QGroupBox("Kết quả tính toán")
        # Updated to use theme friendly or semi-transparent dark blue
        res_group.setStyleSheet("""
            QGroupBox { 
                background-color: rgba(99, 102, 241, 0.15); 
                border: 1px solid #6366f1; 
                border-radius: 8px; 
                margin-top: 10px; 
            }
            QGroupBox::title { 
                color: #4f46e5; 
                font-weight: bold; 
                padding: 5px; 
                background-color: transparent;
            }
        """)
        res_layout = QVBoxLayout(res_group)
        
        self.lbl_per_dose = QLabel("--- ml / lần")
        self.lbl_per_dose.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_per_dose.setStyleSheet("font-size: 24px; font-weight: 800; color: #4f46e5; background: transparent;")
        
        self.lbl_total_day = QLabel("(Tổng: --- ml/ngày)")
        self.lbl_total_day.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_total_day.setStyleSheet("color: #4338ca; font-weight: 600; background: transparent;")
        
        res_layout.addWidget(self.lbl_per_dose)
        res_layout.addWidget(self.lbl_total_day)
        layout.addWidget(res_group)

        # Actions
        act_layout = QHBoxLayout()
        self.btn_calc = QPushButton("TÍNH NGAY")
        self.btn_calc.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_calc.setFixedHeight(45)
        self.btn_calc.setStyleSheet("""
            QPushButton { background-color: #10b981; color: white; font-weight: 800; font-size: 15px; border-radius: 6px; border: none; }
            QPushButton:hover { background-color: #059669; }
        """)
        self.btn_calc.clicked.connect(self.calculate)
        
        act_layout.addWidget(self.btn_calc)
        layout.addLayout(act_layout)

    def label(self, text):
        l = QLabel(text)
        # Removed hardcoded color
        l.setStyleSheet("font-weight: 600; background: transparent;")
        return l

    def style_input(self, w):
        # Updated for theme compatibility
        w.setStyleSheet("""
            QLineEdit, QComboBox { 
                border: 1px solid palette(mid); 
                border-radius: 6px; 
                padding: 8px; 
                background-color: palette(base);
                color: palette(text);
            }
            QLineEdit:focus { border: 2px solid #6366f1; padding: 7px; }
        """)

    def fill_drug_data(self, index):
        data = self.drug_combo.currentData()
        if data:
            self.mg_edit.setText(str(data.get('mg', '')))
            self.ml_edit.setText(str(data.get('ml', '')))
            self.dose_edit.setText(str(data.get('dose', '')))

    def calculate(self):
        try:
            mg_text = self.mg_edit.text().strip()
            ml_text = self.ml_edit.text().strip()
            dose_text = self.dose_edit.text().strip()
            weight_text = self.weight_edit.text().strip()
            
            if not all([mg_text, ml_text, dose_text, weight_text]):
                QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập đủ các trường dữ liệu.")
                return

            mg = float(mg_text)
            ml = float(ml_text)
            dose_per_kg = float(dose_text)
            weight = float(weight_text)
            times = self.div_group.checkedId()
            
            if times == -1: times = 1
            
            if mg <= 0:
                QMessageBox.warning(self, "Lỗi", "Hàm lượng mg phải > 0.")
                return
                
            total_ml = (dose_per_kg * weight * ml) / mg
            ml_per_time = total_ml / times
            
            self.lbl_per_dose.setText(f"{ml_per_time:.1f} ml / lần")
            self.lbl_total_day.setText(f"(Tổng: {total_ml:.1f} ml/ngày)")
            AnimationHelper.shake_widget(self.lbl_per_dose)
            
        except ValueError:
            QMessageBox.warning(self, "Lỗi định dạng", "Vui lòng nhập số hợp lệ (dùng dấu chấm cho số thập phân).")
        except ZeroDivisionError:
            QMessageBox.warning(self, "Lỗi", "Không thể chia cho 0.")

    def add_drug(self):
        dialog = DrugEditorDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if data:
                self.drugs_data.append(data)
                self.save_drugs_data()
                self.refresh_drug_combo()
                # Select the new drug
                index = self.drug_combo.findText(data["name"])
                if index >= 0:
                    self.drug_combo.setCurrentIndex(index)
            else:
                QMessageBox.warning(self, "Lỗi", "Dữ liệu không hợp lệ. Vui lòng kiểm tra lại.")

    def edit_drug(self):
        idx = self.drug_combo.currentIndex()
        if idx <= 0: # 0 is "-- Chọn thuốc mẫu --"
            return
            
        current_data = self.drug_combo.currentData()
        dialog = DrugEditorDialog(self, current_data)
        if dialog.exec():
            data = dialog.get_data()
            if data:
                # Update data in list
                # We need to find the item in self.drugs_data that matches
                # Since list order matches combo order (minus 1 for header), we can use index-1
                data_idx = idx - 1
                if 0 <= data_idx < len(self.drugs_data):
                    self.drugs_data[data_idx] = data
                    self.save_drugs_data()
                    self.refresh_drug_combo()
                    self.drug_combo.setCurrentIndex(idx)
            else:
                QMessageBox.warning(self, "Lỗi", "Dữ liệu không hợp lệ.")

    def delete_drug(self):
        idx = self.drug_combo.currentIndex()
        if idx <= 0:
            return
            
        drug_name = self.drug_combo.currentText()
        confirm = QMessageBox.question(
            self, "Xác nhận xóa", 
            f"Bạn có chắc muốn xóa thuốc '{drug_name}' không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            data_idx = idx - 1
            if 0 <= data_idx < len(self.drugs_data):
                del self.drugs_data[data_idx]
                self.save_drugs_data()
                self.refresh_drug_combo()
                self.drug_combo.setCurrentIndex(0)

    def save_drugs_data(self):
        try:
            drugs_path = os.path.join(config._DATA_DIR, "drugs.json")
            with open(drugs_path, "w", encoding="utf-8") as f:
                json.dump(self.drugs_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi lưu file", f"Không thể lưu dữ liệu thuốc: {e}")

    def refresh_drug_combo(self):
        current_text = self.drug_combo.currentText()
        self.drug_combo.blockSignals(True)
        self.drug_combo.clear()
        self.drug_combo.addItem("-- Chọn thuốc mẫu --")
        for drug in self.drugs_data:
            self.drug_combo.addItem(drug["name"], drug)
        
        # Try to restore selection if possible
        idx = self.drug_combo.findText(current_text)
        if idx >= 0:
            self.drug_combo.setCurrentIndex(idx)
        else:
            self.drug_combo.setCurrentIndex(0)
        self.drug_combo.blockSignals(False)