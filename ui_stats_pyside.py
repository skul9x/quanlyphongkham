from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, 
    QPushButton, QTreeWidget, QTreeWidgetItem, QHeaderView, 
    QComboBox, QRadioButton, QButtonGroup, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, QThreadPool
from datetime import datetime
import calendar
import database
import utils
import config
from worker import Worker
from ux_components import LoadingOverlay, AnimatedButton

class StatsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(8)
        
        self.available_months = []
        self.available_years = []
        
        self._current_request_id = 0
        self._active_workers = set()
        
        self.setup_ui()
        self.overlay = LoadingOverlay(self)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        header_lbl = QLabel("Báo Cáo & Thống Kê")
        header_lbl.setObjectName("HeaderTitle")
        layout.addWidget(header_lbl)

        filter_group = QGroupBox("Bộ lọc dữ liệu")
        filter_group.setObjectName("FilterGroupBox")
        filter_layout = QVBoxLayout(filter_group)
        filter_layout.setSpacing(15)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.btn_day = self.create_filter_btn("📅 Theo Ngày", "FilterButtonDay")
        self.btn_week = self.create_filter_btn("📅 Theo Tuần", "FilterButtonWeek")
        self.btn_month = self.create_filter_btn("📅 Theo Tháng", "FilterButtonMonth")
        self.btn_year = self.create_filter_btn("📅 Theo Năm", "FilterButtonYear")
        self.btn_age = self.create_filter_btn("👶 Theo Độ Tuổi", "FilterButtonAge")
        self.btn_gender = self.create_filter_btn("⚧ Giới Tính", "FilterButtonGender")
        self.btn_loc = self.create_filter_btn("📍 Địa Điểm", "FilterButtonLocation")
        self.btn_med = self.create_filter_btn("💊 Báo Cáo Thuốc", "FilterButtonMedicine") # v5.1.0

        self.btn_group = QButtonGroup(self)
        self.btn_group.addButton(self.btn_day)
        self.btn_group.addButton(self.btn_week)
        self.btn_group.addButton(self.btn_month)
        self.btn_group.addButton(self.btn_year)
        self.btn_group.addButton(self.btn_age)
        self.btn_group.addButton(self.btn_gender)
        self.btn_group.addButton(self.btn_loc)
        self.btn_group.addButton(self.btn_med)

        self.btn_day.clicked.connect(self.stats_day)
        self.btn_week.clicked.connect(self.stats_week)
        self.btn_month.clicked.connect(self.stats_month)
        self.btn_year.clicked.connect(self.stats_year)
        self.btn_age.clicked.connect(self.stats_age)
        self.btn_gender.clicked.connect(self.stats_gender)
        self.btn_loc.clicked.connect(self.stats_location)
        self.btn_med.clicked.connect(self.stats_medicine_usage)

        btn_layout.addWidget(self.btn_day)
        btn_layout.addWidget(self.btn_week)
        btn_layout.addWidget(self.btn_month)
        btn_layout.addWidget(self.btn_year)
        
        btn_layout2 = QHBoxLayout()
        btn_layout2.setSpacing(10)
        btn_layout2.addWidget(self.btn_age)
        btn_layout2.addWidget(self.btn_gender)
        btn_layout2.addWidget(self.btn_loc)
        btn_layout2.addWidget(self.btn_med)
        btn_layout2.addStretch()
        
        filter_layout.addLayout(btn_layout)
        filter_layout.addLayout(btn_layout2)
        
        self.dynamic_filter_area = QWidget()
        self.dynamic_layout = QHBoxLayout(self.dynamic_filter_area)
        self.dynamic_layout.setContentsMargins(0, 0, 0, 0)
        self.dynamic_layout.setSpacing(15)
        filter_layout.addWidget(self.dynamic_filter_area)
        
        layout.addWidget(filter_group)

        self.tree = QTreeWidget()
        self.tree.setObjectName("StatsTreeWidget")
        self.tree.setHeaderLabels(["Tiêu chí phân loại", "Số lượng"])
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.tree.header().resizeSection(1, 200)
        self.tree.setAlternatingRowColors(True)
        
        layout.addWidget(self.tree)

    def create_filter_btn(self, text, obj_name):
        btn = QPushButton(text)
        btn.setObjectName(obj_name)
        btn.setCheckable(True)
        btn.setAutoExclusive(True)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedHeight(40)
        return btn

    def get_new_request_id(self):
        self._current_request_id += 1
        return self._current_request_id

    def is_valid_request(self, req_id):
        return req_id == self._current_request_id

    def clear_dynamic_filters(self):
        while self.dynamic_layout.count():
            child = self.dynamic_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def populate_tree(self, headers, data, total_label="TỔNG CỘNG"):
        self.tree.setHeaderLabels(headers)
        self.tree.clear()
        
        total = 0
        if data:
            for row in data:
                try:
                    label, val = row[0], row[1]
                    if isinstance(val, (int, float)):
                        total += val
                    
                    item = QTreeWidgetItem([str(label), str(val)])
                    item.setTextAlignment(1, Qt.AlignmentFlag.AlignCenter)
                    self.tree.addTopLevelItem(item)
                except Exception:
                    pass
        
        if len(data) > 0:
            if len(headers) == 3:  # Thống kê thuốc có cấu trúc cột khác
                t_item = QTreeWidgetItem([total_label, "", "{:,.2f}".format(total).rstrip('0').rstrip('.')])
                t_item.setTextAlignment(2, Qt.AlignmentFlag.AlignRight)
                for i in range(3):
                    font = t_item.font(i)
                    font.setBold(True)
                    t_item.setFont(i, font)
            else:
                t_item = QTreeWidgetItem([total_label, str(total)])
                t_item.setTextAlignment(1, Qt.AlignmentFlag.AlignCenter)
                font = t_item.font(0)
                font.setBold(True)
                t_item.setFont(0, font)
                t_item.setFont(1, font)
            self.tree.addTopLevelItem(t_item)

    def _cleanup_worker(self, worker):
        if worker in self._active_workers:
            self._active_workers.discard(worker)

    def run_worker(self, func, headers, *args):
        req_id = self.get_new_request_id()
        self.overlay.show_loading()
        self.tree.clear()
        self.threadpool.clear()
        
        def wrapped_func():
            try:
                return func(*args)
            except Exception:
                return []

        worker = Worker(wrapped_func)
        worker.setAutoDelete(False)
        self._active_workers.add(worker)
        
        def on_success(data):
            if self.is_valid_request(req_id):
                rows = []
                if data:
                    first = dict(data[0])
                    if 'week' in first: 
                        rows = [(r['week'], r['count']) for r in data]
                    elif 'month' in first: 
                        formatted = []
                        for r in data:
                            try:
                                d = datetime.strptime(r['month'], '%Y-%m')
                                formatted.append((d.strftime('%m/%Y'), r['count']))
                            except: 
                                formatted.append((r['month'], r['count']))
                        rows = formatted
                    elif 'year' in first: 
                        rows = [(r['year'], r['count']) for r in data]
                    elif 'gender' in first: 
                        rows = [(r['gender'], r['count']) for r in data]
                    elif 'location' in first: 
                        rows = [(r['location'], r['count']) for r in data]
                    else: 
                        rows = data
                
                self.populate_tree(headers, rows)
                self.overlay.hide_loading()
        
        def on_error(err):
            if self.is_valid_request(req_id):
                self.overlay.hide_loading()
                QMessageBox.warning(self, "Lỗi", f"Đã xảy ra lỗi: {err[1]}")

        worker.signals.result.connect(on_success)
        worker.signals.error.connect(on_error)
        worker.signals.finished.connect(lambda: self._cleanup_worker(worker))
        
        self.threadpool.start(worker)

    def fetch_time_data(self, callback, req_id):
        self.overlay.show_loading()
        
        def task():
            return database.get_distinct_months_years()

        worker = Worker(task)
        worker.setAutoDelete(False)
        self._active_workers.add(worker)
        
        def on_loaded(res):
            if not self.is_valid_request(req_id):
                return
            self.available_months, self.available_years = res
            callback()
            
        def on_error(err):
            if self.is_valid_request(req_id):
                self.overlay.hide_loading()

        worker.signals.result.connect(on_loaded)
        worker.signals.result.connect(on_loaded)
        worker.signals.error.connect(on_error) 
        worker.signals.finished.connect(lambda: self._cleanup_worker(worker))
        self.threadpool.start(worker)

    # --- [v5.1.0] Medicine Usage Stats ---
    def stats_medicine_usage(self):
        req_id = self.get_new_request_id()
        self.clear_dynamic_filters()
        self.threadpool.clear()
        
        # Sửa lại số lượng cột của tree
        self.tree.setColumnCount(3)
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.tree.header().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.tree.header().resizeSection(1, 150)
        self.tree.header().resizeSection(2, 200)

        def setup_med_ui():
            if not self.is_valid_request(req_id): return
            
            lbl = QLabel("Thời gian:")
            lbl.setObjectName("FormLabel")
            combo = QComboBox()
            combo.setObjectName("ThemedComboBox")
            combo.setFixedWidth(200)
            
            combo.addItem("Tất cả thời gian", None)
            
            display_months = []
            if self.available_months:
                for m in self.available_months:
                    display_text = datetime.strptime(m, '%Y-%m').strftime('%m/%Y')
                    combo.addItem(f"Tháng {display_text}", m)
            
            def on_change(idx):
                sub_req_id = self.get_new_request_id()
                self.overlay.show_loading()
                self.tree.clear()
                self.threadpool.clear()
                
                selected_val = combo.itemData(idx)
                
                def load_data():
                    return database.get_medicine_usage_stats_db(selected_val)
                    
                worker = Worker(load_data)
                worker.setAutoDelete(False)
                self._active_workers.add(worker)
                
                def f(d):
                    if self.is_valid_request(sub_req_id):
                        rows = []
                        if d:
                            for r in d:
                                amt = r['total_amount'] if r['total_amount'] else 0
                                # Chuyển amount sang dạng formatted string, giữ float cho total row
                                fmt_amt = "{:,.2f}".format(amt).rstrip('0').rstrip('.')
                                item = QTreeWidgetItem([r['medicine_name'], str(r['total_quantity']), fmt_amt])
                                item.setTextAlignment(1, Qt.AlignmentFlag.AlignCenter)
                                item.setTextAlignment(2, Qt.AlignmentFlag.AlignRight)
                                self.tree.addTopLevelItem(item)
                                rows.append((r['medicine_name'], amt)) # Trả về số cho tổng
                        
                        # Không gọi self.populate_tree để làm total tuỳ chỉnh
                        total = sum([r[1] for r in rows if isinstance(r[1], (int, float))])
                        if rows:
                            t_item = QTreeWidgetItem(["TỔNG DOANH THU", "", "{:,.2f}".format(total).rstrip('0').rstrip('.')])
                            t_item.setTextAlignment(2, Qt.AlignmentFlag.AlignRight)
                            for i in range(3):
                                font = t_item.font(i)
                                font.setBold(True)
                                t_item.setFont(i, font)
                            self.tree.addTopLevelItem(t_item)
                            
                        self.tree.setHeaderLabels(["Tên thuốc", "SL Sử dụng", "Doanh thu (VNĐ)"])
                        self.overlay.hide_loading()
                        
                def e(err):
                    if self.is_valid_request(sub_req_id):
                        self.overlay.hide_loading()
                        QMessageBox.warning(self, "Lỗi", f"Đã xảy ra lỗi: {err[1]}")
                        
                worker.signals.result.connect(f)
                worker.signals.error.connect(e)
                worker.signals.finished.connect(lambda: self._cleanup_worker(worker))
                self.threadpool.start(worker)

            combo.currentIndexChanged.connect(on_change)
            self.dynamic_layout.addWidget(lbl)
            self.dynamic_layout.addWidget(combo)
            self.dynamic_layout.addStretch()
            
            on_change(0) # Trigger first load

        self.fetch_time_data(setup_med_ui, req_id)
    # -----------------------------------------------

    def stats_day(self):
        req_id = self.get_new_request_id()
        self.clear_dynamic_filters()
        self.threadpool.clear()
        
        def setup_day_ui():
            if not self.is_valid_request(req_id): return
            
            lbl = QLabel("Chọn tháng:")
            lbl.setObjectName("FormLabel")
            combo = QComboBox()
            combo.setObjectName("ThemedComboBox")
            combo.setFixedWidth(150)
            
            display_months = []
            if self.available_months:
                display_months = [datetime.strptime(m, '%Y-%m').strftime('%m/%Y') for m in self.available_months]
            else:
                combo.addItem("Chưa có dữ liệu")
                combo.setEnabled(False)
                self.overlay.hide_loading()
                
            combo.addItems(display_months)
            
            def on_change(idx):
                sub_req_id = self.get_new_request_id()
                
                if idx < 0 or idx >= len(self.available_months): 
                    self.overlay.hide_loading()
                    return
                
                self.overlay.show_loading()
                self.tree.clear()
                ym = self.available_months[idx]
                
                def task():
                    raw = database.get_stats_by_day_for_month(ym)
                    results = []
                    for r in raw:
                        d_obj = datetime.strptime(r['visit_date'], '%Y-%m-%d')
                        lbl_date = f"{d_obj.strftime('%d/%m/%Y')} ({utils.get_vietnamese_weekday(d_obj)})"
                        results.append((lbl_date, r['count']))
                    return results

                worker = Worker(task)
                worker.setAutoDelete(False)
                self._active_workers.add(worker)
                
                def on_day_success(d):
                    if self.is_valid_request(sub_req_id):
                        self.populate_tree(["Ngày", "Số lượt khám"], d)
                        self.overlay.hide_loading()
                
                worker.signals.result.connect(on_day_success)
                worker.signals.error.connect(lambda e: self.overlay.hide_loading() if self.is_valid_request(sub_req_id) else None)
                worker.signals.finished.connect(lambda: self._cleanup_worker(worker))
                self.threadpool.start(worker)
                
            combo.currentIndexChanged.connect(on_change)
            self.dynamic_layout.addWidget(lbl)
            self.dynamic_layout.addWidget(combo)
            self.dynamic_layout.addStretch()
            
            if display_months:
                on_change(0)
            else:
                self.overlay.hide_loading()

        self.fetch_time_data(setup_day_ui, req_id)

    def stats_week(self):
        self.clear_dynamic_filters()
        self.run_worker(database.get_stats_by_week, ["Tuần (Năm-Tuần)", "Số lượt khám"])

    def stats_month(self):
        self.clear_dynamic_filters()
        self.run_worker(database.get_stats_by_month, ["Tháng", "Số lượt khám"])

    def stats_year(self):
        self.clear_dynamic_filters()
        self.run_worker(database.get_stats_by_year, ["Năm", "Số lượt khám"])

    def stats_age(self):
        req_id = self.get_new_request_id()
        self.clear_dynamic_filters()
        self.threadpool.clear()
        
        def setup_age_ui():
            if not self.is_valid_request(req_id): return
            
            rb_month = QRadioButton("Theo tháng")
            rb_month.setObjectName("ThemedRadioButton")
            rb_year = QRadioButton("Theo năm")
            rb_year.setObjectName("ThemedRadioButton")
            rb_month.setChecked(True)
            
            bg = QButtonGroup(self)
            bg.addButton(rb_month)
            bg.addButton(rb_year)
            
            lbl_time = QLabel("Chọn thời gian:")
            lbl_time.setObjectName("FormLabel")
            combo = QComboBox()
            combo.setObjectName("ThemedComboBox")
            combo.setFixedWidth(150)
            
            self.dynamic_layout.addWidget(rb_month)
            self.dynamic_layout.addWidget(rb_year)
            self.dynamic_layout.addSpacing(15)
            self.dynamic_layout.addWidget(lbl_time)
            self.dynamic_layout.addWidget(combo)
            self.dynamic_layout.addStretch()
            
            def load_data():
                sub_req_id = self.get_new_request_id()
                idx = combo.currentIndex()
                if idx < 0: 
                    self.overlay.hide_loading()
                    return
                
                is_month = rb_month.isChecked()
                filter_type = 'month' if is_month else 'year'
                time_val = ""
                
                if is_month:
                    if idx < len(self.available_months):
                        time_val = self.available_months[idx]
                    else: 
                        self.overlay.hide_loading()
                        return
                else:
                    if idx < len(self.available_years):
                        time_val = self.available_years[idx]
                    else: 
                        self.overlay.hide_loading()
                        return

                self.overlay.show_loading()
                
                def task():
                    return self.calculate_age_stats(filter_type, time_val)

                worker = Worker(task)
                worker.setAutoDelete(False)
                self._active_workers.add(worker)
                
                def on_age_success(result):
                    if self.is_valid_request(sub_req_id):
                        data, invalid_count, total_count = result
                        self.populate_tree(["Nhóm tuổi", "Số lượng bệnh nhân"], data, "TỔNG SỐ BỆNH NHÂN")
                        self.overlay.hide_loading()
                        
                        # Show warning if date format issues detected
                        if total_count > 0:
                            if invalid_count == total_count:
                                QMessageBox.warning(
                                    self, "Cảnh báo dữ liệu",
                                    "100% dữ liệu ngày sinh không đúng định dạng (YYYY-MM-DD).\n\n"
                                    "Báo cáo thống kê tuổi không chính xác.\n"
                                    "Hãy kiểm tra và sửa dữ liệu ngày sinh trong hệ thống."
                                )
                            elif invalid_count > total_count * 0.5:
                                QMessageBox.information(
                                    self, "Lưu ý",
                                    f"Có {invalid_count}/{total_count} ({invalid_count*100//total_count}%) bản ghi có ngày sinh không hợp lệ.\n\n"
                                    "Những bản ghi này được xếp vào nhóm 'Không xác định'."
                                )
                        
                worker.signals.result.connect(on_age_success)
                worker.signals.error.connect(lambda e: self.overlay.hide_loading() if self.is_valid_request(sub_req_id) else None)
                worker.signals.finished.connect(lambda: self._cleanup_worker(worker))
                self.threadpool.start(worker)

            def update_combo():
                combo.blockSignals(True)
                combo.clear()
                
                if rb_month.isChecked():
                    if self.available_months:
                        display = [datetime.strptime(m, '%Y-%m').strftime('%m/%Y') for m in self.available_months]
                        combo.addItems(display)
                    else:
                        combo.addItem("Không có dữ liệu")
                else:
                    if self.available_years:
                        combo.addItems(self.available_years)
                    else:
                        combo.addItem("Không có dữ liệu")
                        
                combo.blockSignals(False)
                
                if combo.count() > 0 and combo.itemText(0) != "Không có dữ liệu":
                    combo.setCurrentIndex(0)
                    load_data()
                else:
                    self.tree.clear()
                    self.overlay.hide_loading()

            rb_month.toggled.connect(update_combo)
            rb_year.toggled.connect(update_combo)
            combo.currentIndexChanged.connect(load_data)
            
            update_combo()

        self.fetch_time_data(setup_age_ui, req_id)

    def calculate_age_stats(self, filter_type, time_val):
        """Calculate age statistics with invalid date tracking.
        
        Returns:
            tuple: (results, invalid_count, total_count)
                - results: list of (group_name, count) tuples
                - invalid_count: number of records with invalid/empty DOB
                - total_count: total number of records processed
        """
        ref_date = datetime.now()
        try:
            if filter_type == 'month':
                dt = datetime.strptime(time_val, '%Y-%m')
                last_day = calendar.monthrange(dt.year, dt.month)[1]
                ref_date = dt.replace(day=last_day)
            else:
                year = int(time_val)
                ref_date = datetime(year, 12, 31)
        except Exception:
            pass

        dob_data = database.get_patient_dobs_by_time(filter_type, time_val)
        age_groups_count = {group: 0 for group in config.AGE_GROUPS_STATS}
        
        # Track invalid date count for warning
        invalid_count = 0
        total_count = 0
        
        for row in dob_data:
            dob_str = row['dob']
            count = row['count']
            total_count += count
            
            if not dob_str:
                age_groups_count["Không xác định"] += count
                invalid_count += count
                continue
            
            try:
                dob_date = datetime.strptime(dob_str, '%Y-%m-%d')
                age_days = (ref_date - dob_date).days
                
                if age_days < 0:
                    age_groups_count["Không xác định"] += count
                    invalid_count += count
                    continue
                
                found = False
                for group_name, range_val in config.AGE_GROUPS_STATS.items():
                    if group_name == "Không xác định" or range_val is None: 
                        continue
                    
                    min_days, max_days = range_val
                    
                    if max_days == float('inf'):
                        if age_days >= min_days:
                            age_groups_count[group_name] += count
                            found = True
                            break
                    else:
                        if min_days <= age_days < max_days:
                            age_groups_count[group_name] += count
                            found = True
                            break
                
                if not found:
                    age_groups_count["Không xác định"] += count
                    invalid_count += count

            except (ValueError, TypeError):
                age_groups_count["Không xác định"] += count
                invalid_count += count
        
        results = []
        for group in config.AGE_GROUPS_STATS.keys():
            if age_groups_count[group] > 0:
                results.append((group, age_groups_count[group]))
        
        return results, invalid_count, total_count

    def stats_gender(self):
        self.clear_dynamic_filters()
        self.run_worker(database.get_stats_by_gender, ["Giới tính", "Số lượng bệnh nhân"])

    def stats_location(self):
        self.clear_dynamic_filters()
        self.run_worker(database.get_stats_by_location, ["Địa điểm", "Số lượng bệnh nhân"])