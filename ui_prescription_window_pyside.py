from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QTreeWidget, QTreeWidgetItem, QPushButton, QSpinBox, QSplitter, 
    QHeaderView, QMessageBox, QFrame, QGroupBox, QGridLayout, QAbstractItemView, QCheckBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QShortcut, QKeySequence, QColor, QFont, QIcon
import database
import config
import utils
from ux_components import AnimatedButton
from ui_dose_calculator_pyside import DoseCalculatorWindow
from animation_helper import AnimationHelper

class PrescriptionWindow(QMainWindow):
    def __init__(self, parent=None, patient_id=None, on_success_callback=None):
        super().__init__(parent)
        self.patient_id = patient_id
        self.patient_info = database.get_patient_by_id(patient_id) if patient_id else None
        self.on_success_callback = on_success_callback
        self.prescription_items = []
        self._saved = False  # Track if prescription was saved
        
        patient_name = self.patient_info['name'] if self.patient_info else "Unknown"
        self.setWindowTitle(f"Kê Đơn Thuốc: {patient_name}")
        self.setObjectName("PrescriptionWindow")
        self.resize(1366, 768)
        
        self.setup_ui()
        self.setup_shortcuts()
        self.load_all_medicines()

    def showEvent(self, event):
        super().showEvent(event)
        AnimationHelper.animate_dialog_open(self)

    def closeEvent(self, event):
        """Show confirmation if there are unsaved prescription items."""
        if self.prescription_items and not self._saved:
            msg = QMessageBox(self)
            msg.setWindowTitle("Đơn thuốc chưa lưu")
            msg.setText("Đơn chưa lưu, bạn có muốn lưu lại đơn thuốc không?")
            msg.setIcon(QMessageBox.Icon.Warning)
            btn_save = msg.addButton("Lưu đơn thuốc", QMessageBox.ButtonRole.AcceptRole)
            btn_discard = msg.addButton("Không lưu đơn thuốc", QMessageBox.ButtonRole.DestructiveRole)
            msg.exec()

            if msg.clickedButton() == btn_save:
                self.save_prescription()
                if not self._saved:
                    event.ignore()
                    return
        event.accept()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(20)
        
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        
        search_container = QWidget()
        search_container.setObjectName("SearchContainer")
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(10, 5, 10, 5)
        
        lbl_icon = QLabel("🔍")
        lbl_icon.setObjectName("SearchIconLabel")
        
        self.search_edit = QLineEdit()
        self.search_edit.setObjectName("BorderlessLineEdit")
        self.search_edit.setPlaceholderText("Nhập tên thuốc để tìm kiếm (Enter để chọn đầu tiên)...")
        self.search_edit.textChanged.connect(self.filter_catalog)
        
        search_layout.addWidget(lbl_icon)
        search_layout.addWidget(self.search_edit)
        left_layout.addWidget(search_container)
        
        self.catalog_tree = QTreeWidget()
        self.catalog_tree.setObjectName("CatalogTree")
        self.catalog_tree.setHeaderLabels(["Tên thuốc", "Quy cách", "Giá"])
        self.catalog_tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.catalog_tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.catalog_tree.header().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        
        self.catalog_tree.itemDoubleClicked.connect(self.add_selected_from_catalog)
        left_layout.addWidget(self.catalog_tree)
        
        util_layout = QHBoxLayout()
        self.btn_dose = AnimatedButton("🧮 Tính liều nhanh")
        self.btn_dose.setObjectName("UtilityButton")
        self.btn_dose.setFixedHeight(40)
        self.btn_dose.clicked.connect(self.open_dose_calculator)
        util_layout.addWidget(self.btn_dose)
        left_layout.addLayout(util_layout)
        
        main_layout.addWidget(left_panel, stretch=4)
        
        right_panel = QWidget()
        right_panel.setObjectName("CartPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(15)
        
        cart_header = QLabel("Đơn thuốc hiện tại")
        cart_header.setObjectName("CartHeader")
        cart_header.setStyleSheet("font-weight: bold; font-size: 16px; background-color: transparent;")
        right_layout.addWidget(cart_header)
        
        self.cart_tree = QTreeWidget()
        self.cart_tree.setObjectName("CartTree")
        self.cart_tree.setHeaderLabels(["Tên thuốc", "SL", "Đơn giá", "Thành tiền", ""])
        self.cart_tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.cart_tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.cart_tree.header().resizeSection(1, 100)
        self.cart_tree.header().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.cart_tree.header().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.cart_tree.header().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.cart_tree.header().resizeSection(4, 110)
        
        self.cart_tree.setRootIsDecorated(False)
        self.cart_tree.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection) 
        self.cart_tree.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        right_layout.addWidget(self.cart_tree)
        
        summary_frame = QFrame()
        summary_frame.setObjectName("SummaryFrame")
        sum_layout = QHBoxLayout(summary_frame)
        sum_layout.setContentsMargins(20, 10, 20, 10)
        
        lbl_total_cap = QLabel("TỔNG CỘNG")
        lbl_total_cap.setObjectName("TotalCaptionLabel")
        
        self.lbl_total = QLabel("0 ₫")
        self.lbl_total.setObjectName("TotalValueLabel")
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        sum_layout.addWidget(lbl_total_cap)
        sum_layout.addStretch()
        sum_layout.addWidget(self.lbl_total)
        
        right_layout.addWidget(summary_frame)
        
        btn_row = QHBoxLayout()
        
        self.btn_save = AnimatedButton("HOÀN TẤT + LƯU")
        self.btn_save.setObjectName("PrimarySaveButton")
        self.btn_save.setFixedHeight(55)
        self.btn_save.clicked.connect(self.save_prescription)
        
        self.btn_cancel = AnimatedButton("Hủy")
        self.btn_cancel.setObjectName("SecondaryButton")
        self.btn_cancel.setFixedSize(80, 55)
        self.btn_cancel.clicked.connect(self.close)
        
        self.chk_append = QCheckBox("Kê tiếp đơn cũ")
        self.chk_append.setCursor(Qt.CursorShape.PointingHandCursor)
        self.chk_append.setStyleSheet("""
            QCheckBox {
                font-weight: 600; 
                font-size: 14px; 
                background-color: transparent;
                margin-right: 10px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #94a3b8;
                border-radius: 4px;
                background: white;
            }
            QCheckBox::indicator:checked {
                background-color: #10b981;
                border-color: #10b981;
                image: none; /* Reset if any */
            }
        """)
        
        btn_row.addWidget(self.chk_append)
        btn_row.addWidget(self.btn_cancel)
        btn_row.addWidget(self.btn_save)
        right_layout.addLayout(btn_row)
        
        main_layout.addWidget(right_panel, stretch=3)

    def setup_shortcuts(self):
        QShortcut(QKeySequence("Return"), self.search_edit).activated.connect(self.add_top_result)
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self.save_prescription)

    def load_all_medicines(self):
        self.all_medicines = database.get_all_medicines_db()
        self.filter_catalog("")

    def filter_catalog(self, text):
        self.catalog_tree.clear()
        t = utils.remove_diacritics(text.lower())
        
        count = 0
        for med in self.all_medicines:
            name_norm = utils.remove_diacritics(med['name'].lower())
            if text == "" or t in name_norm:
                # FIX: Hien thi gia voi dinh dang thap phan neu can thiet, khong lam tron
                item = QTreeWidgetItem([med['name'], med['packing_spec'] or "", "{:,.2f}".format(med['price'] or 0).rstrip('0').rstrip('.')])
                item.setData(0, Qt.ItemDataRole.UserRole, med)
                self.catalog_tree.addTopLevelItem(item)
                count += 1
                if count > 50: break 

    def add_top_result(self):
        if self.catalog_tree.topLevelItemCount() > 0:
            item = self.catalog_tree.topLevelItem(0)
            self.add_item_to_cart(item.data(0, Qt.ItemDataRole.UserRole))
            self.search_edit.clear()

    def add_selected_from_catalog(self, item):
        med = item.data(0, Qt.ItemDataRole.UserRole)
        self.add_item_to_cart(med)
        self.search_edit.clear()
        self.search_edit.setFocus()

    def add_item_to_cart(self, med):
        for i, item in enumerate(self.prescription_items):
            if item['id'] == med['id']:
                new_qty = item['qty'] + 1
                self.update_qty(i, new_qty) 
                return

        self.prescription_items.append({
            'id': med['id'],
            'name': med['name'],
            'spec': med['packing_spec'] or "",
            'price': med['price'] or 0,
            'qty': 1
        })
        self.rebuild_cart_tree()

    def update_qty(self, index, new_val):
        if index < 0 or index >= len(self.prescription_items): return

        item_data = self.prescription_items[index]
        
        if new_val <= 0:
            self.remove_item(index)
        else:
            item_data['qty'] = new_val
            
            tree_item = self.cart_tree.topLevelItem(index)
            if tree_item:
                subtotal = new_val * item_data['price']
                # FIX: Hien thi thanh tien voi dinh dang thap phan
                tree_item.setText(3, "{:,.2f}".format(subtotal).rstrip('0').rstrip('.'))
                
                widget = self.cart_tree.itemWidget(tree_item, 1)
                if widget:
                    spin = widget.findChild(QSpinBox)
                    if spin and spin.value() != new_val:
                        spin.blockSignals(True)
                        spin.setValue(new_val)
                        spin.blockSignals(False)

            self.recalculate_total()

    def remove_item(self, index):
        del self.prescription_items[index]
        self.rebuild_cart_tree()

    def rebuild_cart_tree(self):
        self.cart_tree.clear()
        
        for i, item in enumerate(self.prescription_items):
            subtotal = item['qty'] * item['price']
            
            tree_item = QTreeWidgetItem(self.cart_tree)
            tree_item.setText(0, item['name'])
            
            container = QWidget()
            container.setObjectName("SpinBoxContainer")
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            spin = QSpinBox()
            spin.setObjectName("CartSpinBox")
            spin.setRange(0, 999)
            spin.setValue(item['qty'])
            spin.setFixedWidth(80) 
            spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            spin.valueChanged.connect(lambda val, idx=i: self.update_qty(idx, val))
            
            layout.addWidget(spin)
            self.cart_tree.setItemWidget(tree_item, 1, container)
            
            # FIX: Hien thi don gia va thanh tien voi dinh dang thap phan
            tree_item.setText(2, "{:,.2f}".format(item['price']).rstrip('0').rstrip('.'))
            tree_item.setText(3, "{:,.2f}".format(subtotal).rstrip('0').rstrip('.'))
            
            del_container = QWidget()
            del_container.setObjectName("TransparentFrame")
            del_layout = QHBoxLayout(del_container)
            del_layout.setContentsMargins(0, 0, 0, 0)
            del_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            btn_del = AnimatedButton("🗑️ Xóa") 
            btn_del.setObjectName("CartDeleteButton")
            btn_del.setFixedSize(100, 40) 
            btn_del.clicked.connect(lambda checked, idx=i: self.remove_item(idx))
            
            del_layout.addWidget(btn_del)
            self.cart_tree.setItemWidget(tree_item, 4, del_container)
            
        self.recalculate_total()

    def recalculate_total(self):
        med_total = sum(item['qty'] * item['price'] for item in self.prescription_items)
        fee = config.get_consultation_fee()
        total = med_total + fee
        # FIX: Hien thi tong tien voi dinh dang thap phan
        self.lbl_total.setText(f"{total:,.2f} ₫".replace('.00', ''))

    def open_dose_calculator(self):
        raw_weight = self.patient_info['weight'] if self.patient_info else ""
        
        weight_val = None
        try:
            if raw_weight:
                import re
                match = re.search(r"(\d+(\.\d+)?)", str(raw_weight))
                if match:
                    weight_val = float(match.group(1))
        except Exception:
            weight_val = None
            
        DoseCalculatorWindow(self, patient_weight=weight_val).show()

    def save_prescription(self):
        if not self.prescription_items:
            QMessageBox.warning(self, "Chưa có thuốc", "Vui lòng chọn ít nhất một loại thuốc.")
            return

        # [FIX BUG 1] Reload patient info to get latest data (avoid stale data)
        self.patient_info = database.get_patient_by_id(self.patient_id)

        # Get current diagnosis from patient (new field)
        current_diagnosis = database.get_patient_diagnosis_db(self.patient_id)
        if not current_diagnosis:
            # Fallback: try to parse from old medical_history
            medical_history = dict(self.patient_info).get('medical_history') or ""
            if medical_history:
                lines = medical_history.split('\n', 1)
                current_diagnosis = lines[0].strip() if lines else ""
        
        # Prepare prescription items for API
        items = []
        for item in self.prescription_items:
            items.append({
                'medicine_id': item['id'],
                'quantity': item['qty'],
                'unit_price': item['price']
            })
        
        # [FIX BUG 3] Branch logic: append to existing prescription vs create new
        import re
        
        if self.chk_append.isChecked():
            # "Kê tiếp đơn cũ": Append items to the latest existing prescription
            latest_id = database.get_latest_prescription_id_db(self.patient_id)
            if latest_id:
                success = database.append_items_to_prescription_db(latest_id, items)
            else:
                # No existing prescription → create new one
                success = database.create_prescription_db(
                    patient_id=self.patient_id,
                    diagnosis=current_diagnosis,
                    items=items,
                    notes=""
                )
        else:
            # Normal mode: Create entirely new prescription
            success = database.create_prescription_db(
                patient_id=self.patient_id,
                diagnosis=current_diagnosis,
                items=items,
                notes=""
            )
        
        if success:
            # [FIX] Sync legacy medical_history field for backward compatibility
            if self.chk_append.isChecked():
                # "Kê tiếp đơn cũ": Append new medicines after existing ones
                existing_history = dict(self.patient_info).get('medical_history') or ""
                existing_lines = existing_history.split('\n') if existing_history else []
                
                # [FIX BUG 5] Count existing medicine lines — strict regex: line must start with digit+)
                old_med_lines = [l for l in existing_lines if re.match(r'^\d+\)\s', l)]
                start_num = len(old_med_lines) + 1
                
                # Build new medicine lines numbered after the old ones
                new_med_lines = []
                for i, item in enumerate(self.prescription_items):
                    new_med_lines.append(f"{start_num + i}) {item['name']} x {item['qty']} {item['spec']}")
                
                # [FIX BUG 4] Strip trailing newlines before joining to avoid blank lines
                legacy_text = existing_history.rstrip("\n") + "\n" + "\n".join(new_med_lines)
            else:
                # Normal mode: Replace entirely
                legacy_lines = [current_diagnosis or ""]
                for i, item in enumerate(self.prescription_items):
                    legacy_lines.append(f"{i+1}) {item['name']} x {item['qty']} {item['spec']}")
                legacy_text = "\n".join(legacy_lines)
            
            database.update_patient_medical_history_db(self.patient_id, legacy_text)
            
            self._saved = True  # Mark as saved to skip close confirmation
            QMessageBox.information(self, "Thành công", "Đã lưu đơn thuốc và cập nhật hồ sơ.")
            if self.on_success_callback:
                self.on_success_callback()
            self.close()
        else:
            QMessageBox.critical(self, "Lỗi", "Không thể lưu dữ liệu.")