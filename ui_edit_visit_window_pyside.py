from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QFormLayout, QSpinBox, QMessageBox, QGroupBox
)
from PySide6.QtCore import Qt, QThreadPool
from datetime import datetime
import pytz
import database
import config
from animation_helper import AnimationHelper
from worker import Worker

class EditVisitWindow(QDialog):
    def __init__(self, parent=None, visit_id=None, on_success_callback=None):
        super().__init__(parent)
        self.visit_id = visit_id
        self.on_success_callback = on_success_callback
        self.visit_data = None
        self.threadpool = QThreadPool()
        self._active_workers = set()
        
        self.setWindowTitle(f"Sửa Thông Tin - ID: {visit_id}")
        self.setModal(True)
        self.setFixedSize(600, 600)
        self.setup_ui()
        
        # Load data asynchronously to avoid blocking main thread
        self._load_patient_data()

    def _cleanup_worker(self, worker):
        if worker in self._active_workers:
            self._active_workers.discard(worker)

    def _load_patient_data(self):
        """Load patient data in background thread - fixes Blocking Main Thread."""
        def task():
            return database.get_patient_by_id(self.visit_id)
        
        def on_done(data):
            if not data:
                QMessageBox.warning(self, "Lỗi", "Không tìm thấy dữ liệu bệnh nhân.")
                self.close()
                return
            # FIX: Convert sqlite3.Row to dict so .get() method works
            self.visit_data = dict(data)
            self.populate_data()
        
        worker = Worker(task)
        worker.setAutoDelete(False)
        self._active_workers.add(worker)
        worker.signals.result.connect(on_done)
        worker.signals.finished.connect(lambda: self._cleanup_worker(worker))
        self.threadpool.start(worker)

    def showEvent(self, event):
        super().showEvent(event)
        AnimationHelper.animate_dialog_open(self)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Group 1: Info
        grp_info = QGroupBox("Thông tin hành chính")
        grp_info.setStyleSheet(self.get_group_style())
        f_layout = QFormLayout(grp_info)
        f_layout.setSpacing(15)

        self.name_edit = QLineEdit()
        self.style_input(self.name_edit)
        f_layout.addRow(self.lbl("Họ tên (*):"), self.name_edit)
        
        # DOB
        dob_layout = QHBoxLayout()
        self.day_edit = self.date_input("DD", 2)
        self.month_edit = self.date_input("MM", 2)
        self.year_edit = self.date_input("YYYY", 4)
        dob_layout.addWidget(self.day_edit)
        dob_layout.addWidget(QLabel("/"))
        dob_layout.addWidget(self.month_edit)
        dob_layout.addWidget(QLabel("/"))
        dob_layout.addWidget(self.year_edit)
        f_layout.addRow(self.lbl("Ngày sinh:"), dob_layout)

        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["Nam", "Nữ", "Khác"])
        self.style_input(self.gender_combo)
        f_layout.addRow(self.lbl("Giới tính:"), self.gender_combo)

        self.address_edit = QLineEdit()
        self.style_input(self.address_edit)
        f_layout.addRow(self.lbl("Địa chỉ:"), self.address_edit)
        
        self.phone_edit = QLineEdit()
        self.style_input(self.phone_edit)
        f_layout.addRow(self.lbl("Điện thoại:"), self.phone_edit)
        
        self.weight_edit = QLineEdit()
        self.style_input(self.weight_edit)
        f_layout.addRow(self.lbl("Cân nặng (kg):"), self.weight_edit)
        
        layout.addWidget(grp_info)

        # Group 2: Time
        grp_time = QGroupBox("Thời gian khám")
        grp_time.setStyleSheet(self.get_group_style())
        t_layout = QHBoxLayout(grp_time)
        
        self.visit_day = self.spin(1, 31)
        self.visit_month = self.spin(1, 12)
        self.visit_year = self.spin(2000, 2100)
        self.visit_hour = self.spin(0, 23)
        self.visit_minute = self.spin(0, 59)
        
        t_layout.addWidget(QLabel("Ngày:"))
        t_layout.addWidget(self.visit_day)
        t_layout.addWidget(QLabel("/"))
        t_layout.addWidget(self.visit_month)
        t_layout.addWidget(QLabel("/"))
        t_layout.addWidget(self.visit_year)
        t_layout.addSpacing(20)
        t_layout.addWidget(QLabel("Giờ:"))
        t_layout.addWidget(self.visit_hour)
        t_layout.addWidget(QLabel(":"))
        t_layout.addWidget(self.visit_minute)
        
        layout.addWidget(grp_time)
        layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_cancel = QPushButton("Hủy")
        self.btn_cancel.setStyleSheet(self.btn_style(False))
        self.btn_cancel.clicked.connect(self.reject)
        
        self.btn_save = QPushButton("Lưu Thay Đổi")
        self.btn_save.setStyleSheet(self.btn_style(True))
        self.btn_save.clicked.connect(self.save_changes)
        
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        layout.addLayout(btn_layout)

    def get_group_style(self):
        return """
            QGroupBox {
                border: 1px solid palette(mid); 
                border-radius: 8px; 
                margin-top: 1.2em; 
                padding: 15px; 
                font-weight: 700; 
                background-color: palette(base);
                color: palette(text);
            }
            QGroupBox::title { 
                subcontrol-origin: margin; 
                left: 10px; 
                padding: 0 5px; 
                background-color: transparent;
            }
            QLabel { background-color: transparent; }
        """

    def btn_style(self, primary):
        if primary:
            return "QPushButton { background-color: #4f46e5; color: white; border-radius: 6px; padding: 10px; font-weight: 600; border: none; } QPushButton:hover { background-color: #4338ca; }"
        return """
            QPushButton { 
                background-color: palette(base); 
                color: palette(text); 
                border: 1px solid palette(mid); 
                border-radius: 6px; 
                padding: 10px; 
                font-weight: 600; 
            } 
            QPushButton:hover { background-color: palette(midlight); }
        """

    def lbl(self, text):
        l = QLabel(text)
        l.setStyleSheet("font-weight: 600; background-color: transparent;")
        return l

    def style_input(self, w):
        w.setStyleSheet("""
            QLineEdit, QComboBox, QSpinBox { 
                border: 1px solid palette(mid); 
                border-radius: 6px; 
                padding: 6px; 
                background: palette(base);
                color: palette(text);
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus { border: 2px solid #6366f1; padding: 5px; }
        """)

    def date_input(self, ph, ml):
        i = QLineEdit()
        i.setPlaceholderText(ph)
        i.setMaxLength(ml)
        i.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.style_input(i)
        return i

    def spin(self, min_v, max_v):
        s = QSpinBox()
        s.setRange(min_v, max_v)
        self.style_input(s)
        return s

    def populate_data(self):
        """Populate form with patient data - fixes Null Pointer Exception with safe .get()"""
        d = self.visit_data
        
        # FIX: Use .get() with defaults to prevent KeyError/NoneType errors
        self.name_edit.setText(str(d.get('name') or ''))
        self.gender_combo.setCurrentText(str(d.get('gender') or 'Nam'))
        self.address_edit.setText(str(d.get('address') or ''))
        self.phone_edit.setText(str(d.get('phone') or ''))
        self.weight_edit.setText(str(d.get('weight') or ''))
        
        dob = d.get('dob')
        if dob:
            try:
                dt = datetime.strptime(dob, '%Y-%m-%d')
                self.day_edit.setText(f"{dt.day:02d}")
                self.month_edit.setText(f"{dt.month:02d}")
                self.year_edit.setText(f"{dt.year}")
            except (ValueError, TypeError) as e:
                print(f"[WARN] Invalid DOB format: {dob}, error: {e}")

        created_at = d.get('created_at')
        if created_at:
            try:
                # Parse UTC timestamp and convert to local timezone
                utc = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                local = utc.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(config.TIMEZONE))
                self.visit_day.setValue(local.day)
                self.visit_month.setValue(local.month)
                self.visit_year.setValue(local.year)
                self.visit_hour.setValue(local.hour)
                self.visit_minute.setValue(local.minute)
            except (ValueError, TypeError) as e:
                print(f"[WARN] Invalid created_at format: {created_at}, error: {e}")
                # FIX: Fallback to current time if parse fails
                now = datetime.now()
                self.visit_day.setValue(now.day)
                self.visit_month.setValue(now.month)
                self.visit_year.setValue(now.year)
                self.visit_hour.setValue(now.hour)
                self.visit_minute.setValue(now.minute)

    def save_changes(self):
        name = self.name_edit.text().strip()
        if not name:
            AnimationHelper.shake_widget(self.name_edit)
            return

        dob_iso = None
        d, m, y = self.day_edit.text(), self.month_edit.text(), self.year_edit.text()
        if d and m and y:
            try:
                dob_iso = datetime.strptime(f"{int(d):02d}/{int(m):02d}/{int(y):04d}", '%d/%m/%Y').strftime('%Y-%m-%d')
            except (ValueError, TypeError):
                QMessageBox.warning(self, "Lỗi", "Ngày sinh không hợp lệ")
                return

        try:
            local_tz = pytz.timezone(config.TIMEZONE)
            new_local = datetime(
                self.visit_year.value(), self.visit_month.value(), self.visit_day.value(),
                self.visit_hour.value(), self.visit_minute.value(), 0
            )
            new_utc = local_tz.localize(new_local).astimezone(pytz.utc).strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            QMessageBox.warning(self, "Lỗi", "Thời gian không hợp lệ")
            return

        # FIX: Use atomic update function to prevent Transaction Propagation Error
        # FIX: Run in background thread to prevent Blocking Main Thread
        def task():
            return database.update_patient_with_timestamp_db(
                self.visit_id, name, dob_iso, self.gender_combo.currentText(),
                self.address_edit.text(), self.phone_edit.text(), 
                self.weight_edit.text(), self.visit_data.get('medical_history', ''),
                new_utc
            )
        
        def on_done(success):
            if success:
                QMessageBox.information(self, "OK", "Đã cập nhật thông tin.")
                if self.on_success_callback:
                    self.on_success_callback()
                self.accept()
            else:
                QMessageBox.critical(self, "Lỗi", "Không thể lưu thay đổi vào database.")
        
        worker = Worker(task)
        worker.setAutoDelete(False)
        self.btn_save.setEnabled(False) # Prevent double click
        self._active_workers.add(worker)
        worker.signals.result.connect(on_done)
        worker.signals.finished.connect(lambda: self.btn_save.setEnabled(True))
        worker.signals.finished.connect(lambda: self._cleanup_worker(worker))
        self.threadpool.start(worker)