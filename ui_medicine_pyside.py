from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTreeWidget, QTreeWidgetItem, QHeaderView, 
    QMessageBox, QGroupBox, QSplitter, QFormLayout, QFileDialog,
    QMenu, QFrame, QStackedWidget, QAbstractItemView
)
from PySide6.QtCore import Qt, QThreadPool, QSize, QTimer
from PySide6.QtGui import QAction, QIcon
import database
import utils
import openpyxl
from worker import Worker
from ux_components import LoadingOverlay, EmptyStateWidget, set_validation_error, AnimatedButton
from animation_helper import AnimationHelper
import traceback
import math

class MedicineTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.all_medicines_data = []
        self.threadpool = QThreadPool()
        # --- FIX: Track active workers to prevent GC ---
        self._active_workers = set()
        
        self.setup_ui()
        
        self.overlay = LoadingOverlay(self)
        QTimer.singleShot(100, self.load_medicines)

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        
        header_row = QHBoxLayout()
        lbl_title = QLabel("Kho Thuốc")
        lbl_title.setObjectName("HeaderTitle")
        
        btn_import = AnimatedButton("📥 Nhập Excel")
        btn_import.setObjectName("SecondaryButton")
        btn_import.clicked.connect(self.import_excel)
        
        header_row.addWidget(lbl_title)
        header_row.addStretch()
        header_row.addWidget(btn_import)
        left_layout.addLayout(header_row)
        
        # --- [v5.1.0] Alert Banner for Low Stock ---
        self.alert_banner = QFrame()
        self.alert_banner.setObjectName("AlertBanner")
        self.alert_banner.setStyleSheet("""
            QFrame#AlertBanner {
                background-color: #FEF2F2;
                border: 1px solid #F87171;
                border-radius: 6px;
                padding: 8px 12px;
                margin-bottom: 15px;
            }
        """)
        alert_layout = QHBoxLayout(self.alert_banner)
        alert_layout.setContentsMargins(10, 5, 10, 5)
        self.alert_label = QLabel()
        self.alert_label.setStyleSheet("color: #991B1B; font-weight: bold; font-size: 14px;")
        alert_layout.addWidget(self.alert_label)
        self.alert_banner.hide()  # Hidden by default
        left_layout.addWidget(self.alert_banner)
        # -------------------------------------------
        
        self.search_input = QLineEdit()
        self.search_input.setObjectName("SearchInput")
        self.search_input.setPlaceholderText("🔍 Tìm tên thuốc...")
        self.search_input.setFixedHeight(40)
        self.search_input.textChanged.connect(self.filter_medicines)
        left_layout.addWidget(self.search_input)
        
        self.stack_list = QStackedWidget()
        
        self.tree = QTreeWidget()
        self.tree.setObjectName("MedicineTree")
        self.tree.setHeaderLabels(["Tên thuốc", "Quy cách", "Giá bán", "Tồn kho", "Tối thiểu"])
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tree.header().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tree.header().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.tree.header().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.tree.setIndentation(0)
        self.tree.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        
        self.tree.itemSelectionChanged.connect(self.on_selection_changed)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.open_context_menu)
        
        self.empty_state = EmptyStateWidget("Kho thuốc đang rỗng. Hãy thêm thuốc mới hoặc nhập từ Excel.", "💊")
        
        self.stack_list.addWidget(self.tree)
        self.stack_list.addWidget(self.empty_state)
        
        left_layout.addWidget(self.stack_list)
        splitter.addWidget(left_container)

        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(10, 0, 0, 0)
        
        editor_group = QGroupBox("Thông tin chi tiết")
        editor_group.setObjectName("GroupHeader")
        editor_group.setSizePolicy(right_container.sizePolicy())
        
        form_layout = QVBoxLayout(editor_group)
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(25, 30, 25, 30)
        
        self.name_edit = QLineEdit()
        self.name_edit.setObjectName("ThemedLineEdit")
        self.name_edit.setPlaceholderText("Ví dụ: Panadol Extra")
        form_layout.addWidget(self.create_labeled_input("Tên thuốc (*)", self.name_edit))
        
        self.spec_edit = QLineEdit()
        self.spec_edit.setObjectName("ThemedLineEdit")
        self.spec_edit.setPlaceholderText("Ví dụ: Viên, Vỉ, Chai...")
        form_layout.addWidget(self.create_labeled_input("Quy cách đóng gói", self.spec_edit))
        
        self.price_edit = QLineEdit()
        self.price_edit.setObjectName("ThemedLineEdit")
        self.price_edit.setPlaceholderText("0")
        form_layout.addWidget(self.create_labeled_input("Đơn giá (VNĐ)", self.price_edit))
        
        # --- [v5.1.0] Inventory Inputs ---
        self.stock_edit = QLineEdit()
        self.stock_edit.setObjectName("ThemedLineEdit")
        self.stock_edit.setPlaceholderText("0")
        form_layout.addWidget(self.create_labeled_input("Tồn kho hiện tại", self.stock_edit))
        
        self.min_stock_edit = QLineEdit()
        self.min_stock_edit.setObjectName("ThemedLineEdit")
        self.min_stock_edit.setPlaceholderText("5")
        form_layout.addWidget(self.create_labeled_input("Tồn tối thiểu (Ngưỡng cảnh báo)", self.min_stock_edit))
        # ---------------------------------
        
        form_layout.addStretch()
        
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(10)
        
        self.btn_add = AnimatedButton("✨ Thêm thuốc mới")
        self.btn_add.setObjectName("PrimaryAddButton")
        self.btn_add.setFixedHeight(45)
        self.btn_add.clicked.connect(self.add_medicine)
        
        self.btn_update = AnimatedButton("💾 Cập nhật")
        self.btn_update.setObjectName("PrimaryUpdateButton")
        self.btn_update.setFixedHeight(45)
        self.btn_update.clicked.connect(self.update_medicine)
        self.btn_update.hide()
        
        row_edit_actions = QHBoxLayout()
        row_edit_actions.setSpacing(10)
        
        self.btn_cancel = AnimatedButton("Hủy bỏ")
        self.btn_cancel.setObjectName("SecondaryButton")
        self.btn_cancel.setFixedHeight(45)
        self.btn_cancel.clicked.connect(self.clear_form)
        
        self.btn_delete = AnimatedButton("🗑️ Xóa")
        self.btn_delete.setObjectName("DangerDeleteButton")
        self.btn_delete.setFixedHeight(45)
        self.btn_delete.clicked.connect(self.delete_medicine)
        
        row_edit_actions.addWidget(self.btn_cancel)
        row_edit_actions.addWidget(self.btn_delete)
        
        self.edit_actions_container = QWidget()
        self.edit_actions_container.setLayout(row_edit_actions)
        self.edit_actions_container.hide()
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_update)
        btn_layout.addWidget(self.edit_actions_container)
        
        form_layout.addLayout(btn_layout)
        
        right_layout.addWidget(editor_group)
        splitter.addWidget(right_container)
        
        splitter.setStretchFactor(0, 6)
        splitter.setStretchFactor(1, 4)
        
        main_layout.addWidget(splitter)

    def create_labeled_input(self, label_text, widget):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        
        label = QLabel(label_text)
        label.setObjectName("FormLabel")
        label.setStyleSheet("font-weight: 600; opacity: 0.9;")
        
        layout.addWidget(label)
        layout.addWidget(widget)
        return container

    def open_context_menu(self, position):
        item = self.tree.itemAt(position)
        if not item: return
        menu = QMenu()
        act_edit = QAction("✏️ Sửa thuốc", self)
        act_edit.triggered.connect(self.on_selection_changed)
        act_delete = QAction("🗑️ Xóa thuốc", self)
        act_delete.triggered.connect(self.delete_medicine)
        menu.addAction(act_edit)
        menu.addAction(act_delete)
        menu.exec(self.tree.viewport().mapToGlobal(position))

    # --- FIX: WORKER MANAGEMENT HELPERS ---
    def _cleanup_worker(self, worker):
        if worker in self._active_workers:
            self._active_workers.discard(worker)

    def run_worker(self, func, on_success, on_error=None):
        """
        Generic safe worker runner.
        Prevents premature destruction by holding reference in self._active_workers.
        """
        self.overlay.show_loading()
        
        worker = Worker(func)
        worker.setAutoDelete(False) # Prevent auto-deletion by QThreadPool
        self._active_workers.add(worker)
        
        worker.signals.result.connect(on_success)
        if on_error:
            worker.signals.error.connect(on_error)
        else:
            # Default error handler
            worker.signals.error.connect(lambda e: self.overlay.hide_loading())
            
        # Always cleanup
        worker.signals.finished.connect(lambda: self._cleanup_worker(worker))
        
        self.threadpool.start(worker)
    # --------------------------------------

    def load_medicines(self):
        print("[UI] Loading medicines...")
        self.run_worker(database.get_all_medicines_db, self.on_medicines_loaded)

    def on_medicines_loaded(self, data):
        print(f"[UI] Medicines loaded: {len(data)} records")
        self.overlay.hide_loading()
        self.all_medicines_data = data
        self.populate_tree(self.all_medicines_data)
        self.clear_form()

    def populate_tree(self, data):
        self.tree.clear()
        
        low_stock_count = 0
        out_of_stock_count = 0
        
        if not data:
            self.stack_list.setCurrentWidget(self.empty_state)
            self.alert_banner.hide()
        else:
            self.stack_list.setCurrentWidget(self.tree)
            from PySide6.QtGui import QColor, QFont
            from PySide6.QtCore import Qt
            
            bold_font = QFont()
            bold_font.setBold(True)
            
            for med in data:
                item = QTreeWidgetItem(self.tree)
                item.setText(0, med['name'])
                item.setText(1, med['packing_spec'] or "")
                item.setText(2, "{:,.2f}".format(med['price'] or 0).rstrip('0').rstrip('.') if med['price'] else "0")
                
                # sqlite3.Row doesn't support .get(), convert to dict first
                med_dict = dict(med)
                
                raw_stock = med_dict.get('stock_quantity')
                stock = int(raw_stock) if raw_stock is not None else 0
                
                raw_min = med_dict.get('min_stock_level')
                min_stock = int(raw_min) if raw_min is not None else 5
                
                # --- v5.1.0 Highlighting Logic ---
                if stock <= 0:
                    out_of_stock_count += 1
                    item.setText(3, f"❌ {stock} (Hết)")
                    item.setFont(3, bold_font)
                    item.setForeground(3, QColor("#B91C1C"))  # Dark Red text
                    # Target background color: #FEF2F2
                    for i in range(5): item.setBackground(i, QColor(254, 242, 242))
                elif stock <= min_stock:
                    low_stock_count += 1
                    item.setText(3, f"⚠️ {stock}")
                    item.setFont(3, bold_font)
                    item.setForeground(3, QColor("#B45309"))  # Dark Amber text
                    # Target background color: #FFFBEB
                    for i in range(5): item.setBackground(i, QColor(255, 251, 235))
                else:
                    item.setText(3, str(stock))
                
                item.setText(4, str(min_stock))
                item.setTextAlignment(3, Qt.AlignmentFlag.AlignCenter)
                item.setTextAlignment(4, Qt.AlignmentFlag.AlignCenter)
                item.setData(0, Qt.ItemDataRole.UserRole, med['id'])
                
            # Update Banner
            total_warnings = low_stock_count + out_of_stock_count
            if total_warnings > 0:
                parts = []
                if out_of_stock_count > 0:
                    parts.append(f"{out_of_stock_count} loại đã HẾT KHO")
                if low_stock_count > 0:
                    parts.append(f"{low_stock_count} loại SẮP HẾT")
                
                self.alert_label.setText(f"⚠️ CẢNH BÁO: " + " và ".join(parts) + "!")
                if out_of_stock_count > 0:
                    self.alert_banner.setStyleSheet("QFrame#AlertBanner { background-color: #FEF2F2; border: 1px solid #F87171; border-radius: 6px; padding: 8px 12px; margin-bottom: 15px; }")
                    self.alert_label.setStyleSheet("color: #991B1B; font-weight: bold; font-size: 14px;")
                else:
                    self.alert_banner.setStyleSheet("QFrame#AlertBanner { background-color: #FFFBEB; border: 1px solid #FCD34D; border-radius: 6px; padding: 8px 12px; margin-bottom: 15px; }")
                    self.alert_label.setStyleSheet("color: #92400E; font-weight: bold; font-size: 14px;")
                
                self.alert_banner.show()
            else:
                self.alert_banner.hide()

    def filter_medicines(self, text):
        t = text.lower()
        tn = utils.remove_diacritics(t)
        filtered = [m for m in self.all_medicines_data if t in m['name'].lower() or tn in utils.remove_diacritics(m['name'].lower())]
        self.populate_tree(filtered)

    def on_selection_changed(self):
        items = self.tree.selectedItems()
        if not items:
            self.clear_form()
            return
        
        mid = items[0].data(0, Qt.ItemDataRole.UserRole)
        print(f"[UI] Selection changed to ID: {mid}")
        
        med = database.get_medicine_by_id_db(mid)
        
        if med:
            self.name_edit.setText(med['name'])
            self.spec_edit.setText(med['packing_spec'] or "")
            price_val = med['price'] if med['price'] is not None else 0
            self.price_edit.setText(f"{price_val:g}")
            
            # Inventory fields - [FIX] sqlite3.Row doesn't support .get(), must cast to dict
            med_dict = dict(med)
            stock_val = med_dict.get('stock_quantity', 0) or 0
            min_val = med_dict.get('min_stock_level', 5) or 5
            self.stock_edit.setText(str(int(stock_val)))
            self.min_stock_edit.setText(str(int(min_val)))
            
            self.btn_add.hide()
            self.btn_update.show()
            self.edit_actions_container.show()
            set_validation_error(self.name_edit, False)
            
            AnimationHelper.fade_in(self.btn_update, duration=200)
        else:
            self.clear_form()

    def clear_form(self):
        self.name_edit.clear()
        self.spec_edit.clear()
        self.price_edit.clear()
        self.stock_edit.clear()
        self.min_stock_edit.clear()
        self.tree.clearSelection()
        
        self.btn_add.show()
        self.btn_update.hide()
        self.edit_actions_container.hide()
        set_validation_error(self.name_edit, False)
        set_validation_error(self.price_edit, False)
        set_validation_error(self.stock_edit, False)
        set_validation_error(self.min_stock_edit, False)

    def get_form_data(self):
        name = self.name_edit.text().strip()
        spec = self.spec_edit.text().strip()
        price_str = self.price_edit.text().strip()
        stock_str = self.stock_edit.text().strip()
        min_stock_str = self.min_stock_edit.text().strip()
        
        valid = True
        if not name:
            set_validation_error(self.name_edit, True)
            valid = False
        else:
            set_validation_error(self.name_edit, False)
            
        price = 0.0
        try:
            price = float(price_str) if price_str else 0.0
            if price < 0 or math.isinf(price) or math.isnan(price) or price > 1_000_000_000:
                raise ValueError()
            set_validation_error(self.price_edit, False)
        except ValueError:
            set_validation_error(self.price_edit, True)
            valid = False
            
        stock = 0
        try:
            stock = int(stock_str) if stock_str else 0
            set_validation_error(self.stock_edit, False)
        except ValueError:
            set_validation_error(self.stock_edit, True)
            valid = False
            
        min_stock = 5
        try:
            min_stock = int(min_stock_str) if min_stock_str else 5
            set_validation_error(self.min_stock_edit, False)
        except ValueError:
            set_validation_error(self.min_stock_edit, True)
            valid = False
            
        if not valid:
            QMessageBox.warning(self, "Lỗi nhập liệu", "Vui lòng kiểm tra các trường bôi đỏ.")
            return None
            
        return name, spec, price, stock, min_stock

    def add_medicine(self):
        print("[UI] Adding medicine...")
        d = self.get_form_data()
        if not d: return

        def task():
            print("[WORKER] Checking for duplicates...")
            if database.get_medicine_by_name_db(d[0]):
                return "DUPLICATE"
            print("[WORKER] Adding to DB...")
            return database.add_medicine_db(*d)
            
        def on_done(res):
            print(f"[UI] Add completed with result: {res}")
            self.overlay.hide_loading()
            if res == "DUPLICATE":
                QMessageBox.warning(self, "Trùng lặp", "Tên thuốc này đã tồn tại trong kho.")
                set_validation_error(self.name_edit, True)
            elif res:
                self.load_medicines()
                QMessageBox.information(self, "Thành công", "Đã thêm thuốc mới.")
            else:
                QMessageBox.critical(self, "Lỗi", "Không thể lưu vào cơ sở dữ liệu.")
        
        def on_err(e):
            print(f"[UI] Add Error: {e}")
            self.overlay.hide_loading()
            QMessageBox.critical(self, "Lỗi", f"Lỗi hệ thống: {str(e[1])}")

        self.run_worker(task, on_done, on_err)

    def update_medicine(self):
        print("[UI] Updating medicine...")
        items = self.tree.selectedItems()
        if not items: return
        mid = items[0].data(0, Qt.ItemDataRole.UserRole)
        d = self.get_form_data()
        if not d: return
        
        def task():
            print(f"[WORKER] Checking duplicate for update ID {mid}...")
            ex = database.get_medicine_by_name_db(d[0])
            if ex and ex['id'] != mid:
                return "DUPLICATE"
            print("[WORKER] Updating DB...")
            # Unpack form data (d[0]=name, d[1]=spec, d[2]=price, d[3]=stock, d[4]=min)
            return database.update_medicine_db(mid, d[0], d[1], d[2], d[3], d[4])
            
        def on_done(res):
            print(f"[UI] Update result: {res}")
            self.overlay.hide_loading()
            if res == "DUPLICATE":
                QMessageBox.warning(self, "Trùng lặp", "Tên thuốc mới bị trùng với thuốc khác.")
                set_validation_error(self.name_edit, True)
            elif res:
                self.load_medicines()
                QMessageBox.information(self, "Thành công", "Đã cập nhật thông tin thuốc.")
            else:
                QMessageBox.critical(self, "Lỗi", "Lỗi cập nhật.")
        
        def on_err(e):
            print(f"[UI] Update Error: {e}")
            self.overlay.hide_loading()
            QMessageBox.critical(self, "Lỗi", f"Lỗi hệ thống: {str(e[1])}")
                    
        self.run_worker(task, on_done, on_err)

    def delete_medicine(self):
        items = self.tree.selectedItems()
        if not items: return
        mid = items[0].data(0, Qt.ItemDataRole.UserRole)
        
        if database.is_medicine_in_use(mid):
            QMessageBox.warning(self, "Không thể xóa", "Thuốc này đang có trong đơn thuốc của bệnh nhân. Không thể xóa để bảo toàn lịch sử.")
            return
            
        if QMessageBox.question(self, "Xác nhận", f"Bạn có chắc muốn xóa thuốc '{items[0].text(0)}'?") == QMessageBox.StandardButton.Yes:
            
            def on_done(res):
                self.overlay.hide_loading()
                if res:
                    self.load_medicines()
                else:
                    QMessageBox.critical(self, "Lỗi", "Không thể xóa thuốc (Có thể do lỗi DB).")
            
            self.run_worker(lambda: database.delete_medicine_db(mid), on_done)

    def import_excel(self):
        fp, _ = QFileDialog.getOpenFileName(self, "Chọn file Excel", "", "Excel Files (*.xlsx)")
        if not fp: return
        
        def task():
            wb = openpyxl.load_workbook(fp, data_only=True)
            s = wb.active
            count = 0
            for r in s.iter_rows(min_row=2, values_only=True):
                if len(r) >= 2 and r[1]:
                    name = str(r[1]).strip()
                    if not name: continue
                    
                    if not database.get_medicine_by_name_db(name):
                         spec = str(r[2]).strip() if len(r) > 2 and r[2] else ""
                         try:
                            price = float(str(r[3]).replace(",", ".")) if len(r) > 3 and r[3] else 0.0
                         except: price = 0.0
                         
                         if database.add_medicine_db(name, spec, price):
                             count += 1
            return count

        def fin(res):
            self.overlay.hide_loading()
            QMessageBox.information(self, "Hoàn tất", f"Đã nhập thành công {res} thuốc mới.")
            self.load_medicines()
            
        def err(e):
            self.overlay.hide_loading()
            QMessageBox.critical(self, "Lỗi", f"Lỗi đọc file Excel: {str(e[1])}")
            
        self.run_worker(task, fin, err)