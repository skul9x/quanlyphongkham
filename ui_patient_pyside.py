from PySide6.QtWidgets import QWidget, QHBoxLayout, QMessageBox
from PySide6.QtCore import QThreadPool, QTimer
import re
from collections import Counter
import traceback

import database
from ui_add_patient_window_pyside import AddPatientWindow
from ui_add_visit_window_pyside import AddVisitWindow
from ui_edit_visit_window_pyside import EditVisitWindow
from ui_edit_diagnosis_window_pyside import EditDiagnosisWindow
from ui_prescription_window_pyside import PrescriptionWindow
from ui_history_window_pyside import HistoryWindow
from worker import Worker
from ux_components import LoadingOverlay
from ui_patient_list import PatientListWidget
from ui_patient_detail import PatientDetailWidget

class PatientTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.threadpool = QThreadPool()
        self.current_patient = None
        
        # --- FIX: Track active workers to prevent GC ---
        self._active_workers = set()
        
        # --- Pagination state for infinite scroll ---
        self._page_size = 50
        self._current_search_term = ""
        
        self.setup_ui()
        
        self.overlay = LoadingOverlay(self)
        
        self.load_patients()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.list_widget = PatientListWidget()
        self.list_widget.patient_selected.connect(self.on_patient_selected)
        self.list_widget.add_patient_clicked.connect(self.open_add_patient)
        self.list_widget.search_requested.connect(self._on_search_requested)
        self.list_widget.load_more_requested.connect(self._on_load_more_requested)
        # QListView uses doubleClicked signal with QModelIndex
        self.list_widget.patient_list.doubleClicked.connect(lambda idx: self.open_prescription())
        
        self.detail_widget = PatientDetailWidget()
        self.detail_widget.action_visit_clicked.connect(self.open_add_visit)
        self.detail_widget.action_prescribe_clicked.connect(self.open_prescription)
        self.detail_widget.action_history_clicked.connect(self.show_history)
        self.detail_widget.action_edit_clicked.connect(self.open_edit_info)
        self.detail_widget.action_diagnosis_clicked.connect(self.open_edit_diagnosis)
        self.detail_widget.action_delete_clicked.connect(self.delete_patient)
        
        main_layout.addWidget(self.list_widget)
        main_layout.addWidget(self.detail_widget)

    # --- FIX: WORKER MANAGEMENT HELPERS ---
    def _cleanup_worker(self, worker):
        if worker in self._active_workers:
            self._active_workers.discard(worker)

    def run_worker(self, func, on_success, *args, **kwargs):
        # self.overlay.show_loading() # Optional for patient loading as it's background
        
        def wrapped_func():
            return func(*args, **kwargs)

        worker = Worker(wrapped_func)
        worker.setAutoDelete(False)
        self._active_workers.add(worker)
        
        worker.signals.result.connect(on_success)
        worker.signals.finished.connect(self.overlay.hide_loading)
        worker.signals.finished.connect(lambda: self._cleanup_worker(worker))
        
        self.threadpool.start(worker)
    # --------------------------------------

    def load_patients(self):
        """Load initial batch of patients with pagination."""
        self.overlay.show_loading()
        self._current_search_term = ""
        self.list_widget._has_more_data = True
        self.run_worker(
            database.search_patients_db, 
            self._on_initial_load_complete, 
            "", 
            limit=self._page_size, 
            offset=0
        )
    
    def _on_initial_load_complete(self, patients):
        """Handle initial load result."""
        self.list_widget.set_patients(patients)
        # If we got fewer than page_size, there's no more data
        if len(patients) < self._page_size:
            self.list_widget._has_more_data = False

    def _on_search_requested(self, text):
        """
        Handle search request from debounced input.
        Resets pagination and loads fresh search results.
        """
        self._current_search_term = text
        self.list_widget._has_more_data = True
        self.run_worker(
            database.search_patients_db, 
            self._on_initial_load_complete, 
            text, 
            limit=self._page_size, 
            offset=0
        )
    
    def _on_load_more_requested(self):
        """Handle infinite scroll - load more patients."""
        current_count = self.list_widget.model.patient_count()
        print(f"[SCROLL] Loading more... offset={current_count}")
        
        self.run_worker(
            database.search_patients_db,
            self._on_load_more_complete,
            self._current_search_term,
            limit=self._page_size,
            offset=current_count
        )
    
    def _on_load_more_complete(self, patients):
        """Handle load more result - append to existing list."""
        self.list_widget._is_loading_more = False
        
        if not patients:
            self.list_widget._has_more_data = False
            print("[SCROLL] No more data to load.")
            return
        
        self.list_widget.model.append_patients(patients)
        print(f"[SCROLL] Loaded {len(patients)} more patients")
        
        # If we got fewer than page_size, there's no more data
        if len(patients) < self._page_size:
            self.list_widget._has_more_data = False

    def on_patient_selected(self, p_basic):
        if not p_basic:
            self.current_patient = None
            self.detail_widget.update_data(None)
            return
            
        self.run_worker(database.get_patient_by_id, self.display_patient_details, p_basic['id'])

    def display_patient_details(self, p):
        if not p: return
        self.current_patient = dict(p) 
        self.detail_widget.update_data(self.current_patient)

    def open_add_patient(self):
        AddPatientWindow(self, on_success_callback=self.load_patients).exec()

    def open_add_visit(self):
        if not self.current_patient: return
        AddVisitWindow(self, self.current_patient, on_success_callback=self.refresh_current).exec()

    def open_prescription(self):
        if not self.current_patient: return
        
        # Check diagnosis from dedicated field first, then fallback to legacy
        diagnosis = self.current_patient.get('diagnosis') or ""
        if not diagnosis:
            medical_history = self.current_patient.get('medical_history') or ""
            diagnosis = medical_history.split('\n', 1)[0].strip() if medical_history else ""
        
        if not diagnosis or diagnosis == "Chưa có chẩn đoán":
            QMessageBox.warning(
                self, 
                "Thiếu chẩn đoán", 
                "Vui lòng nhập chẩn đoán trước khi kê đơn!\n\n"
                "Bấm nút 'Sửa chẩn đoán' để thêm chẩn đoán cho bệnh nhân."
            )
            return
        
        win = PrescriptionWindow(self, patient_id=self.current_patient['id'], on_success_callback=self.refresh_current)
        win.show()

    def show_history(self):
        if not self.current_patient: return
        
        p_name = self.current_patient['name']
        p_dob = self.current_patient['dob']
        self.overlay.show_loading()

        def fetch_history_task():
            try:
                histories = database.get_all_diagnoses_by_name_dob(p_name, p_dob)
                all_drugs = []
                drug_pattern = re.compile(r"^\s*\d+[).]\s*(.+?)(?:\s*x\s*\d+.*)?$", re.IGNORECASE)
                
                for text in histories:
                    if not text: continue
                    for line in text.splitlines():
                        line = line.strip()
                        if not line: continue
                        match = drug_pattern.match(line)
                        if match: 
                            drug_clean = match.group(1).strip()
                            if drug_clean:
                                all_drugs.append(drug_clean.title())
                return all_drugs
            except Exception:
                traceback.print_exc()
                return []

        def on_history_success(all_drugs):
            self.overlay.hide_loading()
            if not all_drugs:
                QMessageBox.information(self, "Lịch sử", f"Chưa tìm thấy thuốc nào trong lịch sử của {p_name}.")
                return
            
            try:
                counts = sorted(Counter(all_drugs).items(), key=lambda x: (-x[1], x[0]))
                HistoryWindow(self, title=f"Lịch sử dùng thuốc: {p_name}", data=counts).exec()
            except Exception as e:
                traceback.print_exc()
                QMessageBox.critical(self, "Lỗi", f"Không thể mở cửa sổ lịch sử: {e}")

        # Manual worker creation for custom task logic
        worker = Worker(fetch_history_task)
        worker.setAutoDelete(False)
        self._active_workers.add(worker)
        
        worker.signals.result.connect(on_history_success)
        worker.signals.finished.connect(self.overlay.hide_loading)
        worker.signals.finished.connect(lambda: self._cleanup_worker(worker))
        self.threadpool.start(worker)

    def open_edit_info(self):
        if not self.current_patient: return
        EditVisitWindow(self, self.current_patient['id'], on_success_callback=self.refresh_current).exec()

    def open_edit_diagnosis(self):
        if not self.current_patient: return
        EditDiagnosisWindow(self, self.current_patient['id'], on_success_callback=self.refresh_current).exec()

    def delete_patient(self):
        if not self.current_patient: return
        reply = QMessageBox.question(self, "Xóa hồ sơ", 
            f"Bạn muốn xóa bệnh nhân {self.current_patient['name']}?\n\nYES: Xóa toàn bộ lịch sử.\nNO: Chỉ xóa lượt khám này.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
        
        if reply == QMessageBox.StandardButton.Cancel: return
        
        if reply == QMessageBox.StandardButton.Yes:
            database.delete_patient_and_all_visits_db(self.current_patient['name'], self.current_patient['dob'])
        else:
            database.delete_visit_db(self.current_patient['id'])
            
        self.load_patients()
        self.detail_widget.update_data(None)
        self.current_patient = None

    def refresh_current(self, action=None, new_id=None):
        """
        Refresh patient list and optionally perform follow-up actions.
        
        Args:
            action: Optional action to perform after refresh ('prescribe' or None)
            new_id: Optional ID of newly created visit to focus on
        """
        self.load_patients()
        
        if self.current_patient:
            # Reload current patient details
            def on_refresh_complete(patient_data):
                self.display_patient_details(patient_data)
                
                # If we have a new visit ID, update current_patient to point to it
                if new_id:
                    self.current_patient['id'] = new_id
                    # Reload again to get the exact visit data
                    self.run_worker(database.get_patient_by_id, self.display_patient_details, new_id)
                
                # Auto-open prescription window if action is "prescribe"
                if action == "prescribe" and new_id:
                    # Use QTimer to ensure UI is fully updated before opening prescription
                    QTimer.singleShot(100, lambda: self._open_prescription_for_visit(new_id))
            
            self.run_worker(database.get_patient_by_id, on_refresh_complete, self.current_patient['id'])
    
    def _open_prescription_for_visit(self, visit_id):
        """Helper method to open prescription window for a specific visit."""
        # Fetch the visit data first
        visit_data = database.get_patient_by_id(visit_id)
        if not visit_data:
            return
        
        # Update current_patient to the new visit
        self.current_patient = dict(visit_data)
        self.detail_widget.update_data(self.current_patient)
        
        # Check diagnosis before opening prescription
        diagnosis = self.current_patient.get('diagnosis') or ""
        if not diagnosis:
            medical_history = self.current_patient.get('medical_history') or ""
            diagnosis = medical_history.split('\n', 1)[0].strip() if medical_history else ""
        
        if not diagnosis or diagnosis == "Chưa có chẩn đoán":
            QMessageBox.warning(
                self, 
                "Thiếu chẩn đoán", 
                "Vui lòng nhập chẩn đoán trước khi kê đơn!\n\n"
                "Bấm nút 'Sửa chẩn đoán' để thêm chẩn đoán cho bệnh nhân."
            )
            return
        
        # Open prescription window
        win = PrescriptionWindow(self, patient_id=visit_id, on_success_callback=self.refresh_current)
        win.show()