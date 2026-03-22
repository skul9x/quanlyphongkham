from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QListView, QFrame, QStyledItemDelegate, QStyle
)
from PySide6.QtCore import Qt, Signal, QAbstractListModel, QModelIndex, QTimer, QSize
from PySide6.QtGui import QFont, QFontMetrics, QPainter, QColor, QPen, QPainterPath
import utils


class PatientListModel(QAbstractListModel):
    """
    Model-based architecture for patient list.
    Only stores data; rendering is handled lazily by QListView.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._patients = []  # List of dicts
    
    def rowCount(self, parent=QModelIndex()):
        return len(self._patients)
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or index.row() >= len(self._patients):
            return None
        
        patient = self._patients[index.row()]
        
        if role == Qt.ItemDataRole.DisplayRole:
            name = patient.get('name', '')
            phone = patient.get('phone') or "Không có SĐT"
            return f"{name}\n{phone}"
        
        elif role == Qt.ItemDataRole.ToolTipRole:
            return f"ID: {patient.get('id', '')} - {patient.get('address', '')}"
        
        elif role == Qt.ItemDataRole.UserRole:
            return patient
        
        return None
    
    def set_patients(self, patients):
        """
        Efficiently update the entire dataset.
        Uses beginResetModel/endResetModel for batch updates.
        """
        self.beginResetModel()
        self._patients = [dict(p) for p in patients]
        self.endResetModel()
    
    def append_patients(self, patients):
        """
        Append more patients to the list (for infinite scroll).
        Uses beginInsertRows/endInsertRows for efficient update.
        """
        if not patients:
            return
        
        start = len(self._patients)
        end = start + len(patients) - 1
        
        self.beginInsertRows(QModelIndex(), start, end)
        self._patients.extend([dict(p) for p in patients])
        self.endInsertRows()
    
    def patient_count(self):
        """Return current number of patients in the model."""
        return len(self._patients)
    
    def get_patient(self, index):
        """Get patient dict at given row index."""
        if 0 <= index < len(self._patients):
            return self._patients[index]
        return None


class PatientItemDelegate(QStyledItemDelegate):
    """Custom delegate to render patient items with proper styling."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.padding = 12
        self.line_spacing = 4
        self.margin_x = 8
        self.margin_y = 4
    
    def sizeHint(self, option, index):
        # Increased height for card look + margins
        return QSize(option.rect.width(), 72)

    def paint(self, painter, option, index):
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Clear the entire rect first to remove any artifacts (like focus rects or default bg)
        # Assuming list background is white. If transparent, use transparent.
        painter.fillRect(option.rect, Qt.GlobalColor.white)
        
        # Define card rect with margins
        rect = option.rect.adjusted(self.margin_x, self.margin_y, -self.margin_x, -self.margin_y)
        
        # Determine colors based on state
        is_selected = option.state & QStyle.State_Selected
        is_hover = option.state & QStyle.State_MouseOver
        
        if is_selected:
            bg_color = QColor("#4F46E5") # Indigo color
            name_color = Qt.GlobalColor.white
            phone_color = QColor(220, 220, 220)
            border_color = Qt.GlobalColor.transparent
        else:
            bg_color = Qt.GlobalColor.white
            if is_hover:
                bg_color = QColor("#F3F4F6") # Light gray hover
            name_color = QColor("#111827") # Dark gray text
            phone_color = QColor("#6B7280") # Gray subtext
            border_color = QColor("#E5E7EB") # Light border

        # Draw Card Background
        path = QPainterPath()
        path.addRoundedRect(rect, 10, 10) # 10px radius
        
        painter.fillPath(path, bg_color)
        
        if border_color != Qt.GlobalColor.transparent:
            pen = QPen(border_color)
            pen.setWidth(1)
            painter.setPen(pen)
            painter.drawPath(path)

        # Get data
        patient = index.data(Qt.ItemDataRole.UserRole)
        if not patient:
            painter.restore()
            return
            
        name = patient.get('name', '')
        phone = patient.get('phone') or "Không có SĐT"
        
        # Setup fonts
        name_font = QFont(option.font)
        name_font.setBold(True)
        name_font.setPointSize(10)
        
        phone_font = QFont(option.font)
        phone_font.setPointSize(9)

        # Draw Name
        # Adjust text rect to be inside the card padding
        text_rect = rect.adjusted(self.padding, self.padding, -self.padding, 0)
        
        painter.setFont(name_font)
        painter.setPen(name_color)
        
        # Fix: Elide text if too long (add "...")
        fm_name = QFontMetrics(name_font)
        elided_name = fm_name.elidedText(name, Qt.TextElideMode.ElideRight, text_rect.width())
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, elided_name)
        
        # Draw Phone
        name_height = fm_name.height()
        
        phone_rect = text_rect.adjusted(0, name_height + self.line_spacing, 0, 0)
        
        painter.setFont(phone_font)
        painter.setPen(phone_color)
        
        # Fix: Elide phone if too long
        fm_phone = QFontMetrics(phone_font)
        elided_phone = fm_phone.elidedText(phone, Qt.TextElideMode.ElideRight, phone_rect.width())
        painter.drawText(phone_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, elided_phone)
        
        painter.restore()


class PatientListWidget(QWidget):
    patient_selected = Signal(dict)
    add_patient_clicked = Signal()
    search_requested = Signal(str)  # New signal for debounced search
    load_more_requested = Signal()  # Signal for infinite scroll

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(320)
        self.setStyleSheet("border-right: 1px solid palette(mid);")
        
        # Debounce timer for search
        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(300)  # 300ms debounce
        self._debounce_timer.timeout.connect(self._emit_search)
        
        # Infinite scroll state
        self._is_loading_more = False
        self._has_more_data = True
        
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(15)
        
        header_row = QHBoxLayout()
        lbl_title = QLabel("Danh sách")
        lbl_title.setStyleSheet("font-size: 18px; font-weight: 800; border: none;")
        
        btn_add = QPushButton("+ Mới")
        btn_add.setFixedSize(90, 40)
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.setStyleSheet("""
            QPushButton { background-color: #10b981; color: white; border-radius: 6px; font-weight: 600; border: none; }
            QPushButton:hover { background-color: #059669; }
        """)
        btn_add.clicked.connect(self.add_patient_clicked.emit)
        
        header_row.addWidget(lbl_title)
        header_row.addStretch()
        header_row.addWidget(btn_add)
        layout.addLayout(header_row)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Tìm tên hoặc SĐT...")
        self.search_input.setFixedHeight(40)
        self.search_input.textChanged.connect(self._on_search_text_changed)
        layout.addWidget(self.search_input)
        
        # Use QListView with Model instead of QListWidget
        self.patient_list = QListView()
        self.patient_list.setObjectName("PatientList")
        self.patient_list.setFrameShape(QFrame.Shape.NoFrame)
        self.patient_list.setUniformItemSizes(True)  # Performance optimization
        self.patient_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # Fix: no horizontal scroll
        # self.patient_list.setAlternatingRowColors(True) # Disabled for card view
        
        # Create and set the model
        self.model = PatientListModel(self)
        self.patient_list.setModel(self.model)
        
        # Set custom delegate for better padding
        self.patient_list.setItemDelegate(PatientItemDelegate(self.patient_list))
        
        # Connect selection changed
        self.patient_list.selectionModel().selectionChanged.connect(self._on_selection_changed)
        
        # Connect scroll detection for infinite scroll
        scrollbar = self.patient_list.verticalScrollBar()
        scrollbar.valueChanged.connect(self._on_scroll_value_changed)
        
        layout.addWidget(self.patient_list)
    
    def _on_scroll_value_changed(self, value):
        """Detect when user scrolls near the bottom to trigger load more."""
        scrollbar = self.patient_list.verticalScrollBar()
        max_value = scrollbar.maximum()
        
        # Trigger load more when within 20% of bottom
        if value >= max_value * 0.8 and max_value > 0:
            if not self._is_loading_more and self._has_more_data:
                self._is_loading_more = True
                self.load_more_requested.emit()
    
    def _on_search_text_changed(self, text):
        """
        Debounced search - starts timer instead of searching immediately.
        This prevents O(N) operations on every keystroke.
        """
        self._debounce_timer.start()
    
    def _emit_search(self):
        """Emit search signal after debounce delay."""
        text = self.search_input.text().strip()
        self.search_requested.emit(text)
    
    def populate_list(self, patients):
        """
        Legacy method name for compatibility.
        Delegates to set_patients().
        """
        self.set_patients(patients)
    
    def set_patients(self, patients):
        """
        Update the patient list with new data.
        Model handles efficient UI updates.
        """
        self.model.set_patients(patients)
    
    def _on_selection_changed(self, selected, deselected):
        """Handle selection change in QListView."""
        indexes = self.patient_list.selectionModel().selectedIndexes()
        if indexes:
            patient = self.model.data(indexes[0], Qt.ItemDataRole.UserRole)
            self.patient_selected.emit(patient if patient else {})
        else:
            self.patient_selected.emit({})
    
    # Backward compatibility: expose double-click signal
    @property
    def itemDoubleClicked(self):
        """Provide backward compatible signal for double-click."""
        return self.patient_list.doubleClicked