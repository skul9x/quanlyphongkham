from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTreeWidget, 
    QTreeWidgetItem, QPushButton, QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from animation_helper import AnimationHelper

class HistoryWindow(QDialog):
    def __init__(self, parent=None, title="Lịch sử khám", data=None):
        super().__init__(parent)
        self.data = data or []
        self.setWindowTitle("Lịch Sử Dùng Thuốc")
        self.resize(600, 700)
        # Removed hardcoded background color to support Dark Mode
        # self.setStyleSheet("background-color: #f8fafc;") 
        self.setup_ui(title)

    def showEvent(self, event):
        super().showEvent(event)
        AnimationHelper.animate_dialog_open(self)

    def setup_ui(self, title_text):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # Title
        lbl_title = QLabel(title_text)
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_title.setWordWrap(True)
        # Removed hardcoded color to adapt to theme
        lbl_title.setStyleSheet("font-size: 18px; font-weight: 800; margin-bottom: 10px;")
        layout.addWidget(lbl_title)

        # Tree Widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Tên Thuốc", "Số Lần Kê"])
        
        # Header Styling & Sizing
        header = self.tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(1, 120)
        header.setSectionsClickable(True) 
        
        self.tree.setAlternatingRowColors(True)
        self.tree.setSortingEnabled(True)
        
        # Removed hardcoded colors for background/text to allow Global Theme to apply.
        # Only keeping structural styling (padding, borders).
        self.tree.setStyleSheet("""
            QTreeWidget { 
                border: 1px solid rgba(128, 128, 128, 0.3); 
                border-radius: 8px; 
                font-size: 14px;
                outline: none;
            }
            QTreeWidget::item { 
                padding: 8px; 
                height: 30px;
            }
            /* Header styling is handled by global theme */
        """)
        
        layout.addWidget(self.tree)

        # Populate Data
        self.tree.setSortingEnabled(False) # Disable sorting while populating for speed
        
        for drug, count in self.data:
            item = QTreeWidgetItem()
            item.setText(0, str(drug))
            
            # Set count as integer for proper numeric sorting (DisplayRole automatically handles str conversion)
            item.setData(1, Qt.ItemDataRole.DisplayRole, int(count)) 
            item.setTextAlignment(1, Qt.AlignmentFlag.AlignCenter)
            
            # Highlight drugs used 3+ times
            if count >= 3:
                font = item.font(0)
                font.setBold(True)
                item.setFont(0, font)
                item.setFont(1, font)
                
                # Removed explicit dark blue foreground color which caused low contrast in Dark Mode.
                # Bold text is sufficient for emphasis and works in both modes.
                item.setToolTip(0, "Thuốc thường xuyên sử dụng")
                
            self.tree.addTopLevelItem(item)
            
        self.tree.setSortingEnabled(True)
        # Default sort: Count Descending
        self.tree.sortItems(1, Qt.SortOrder.DescendingOrder)

        # Close Button
        btn_close = QPushButton("Đóng")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setFixedWidth(100)
        # Updated button style to be theme-friendly
        btn_close.setStyleSheet("""
            QPushButton {
                border: 1px solid rgba(128, 128, 128, 0.5);
                border-radius: 6px;
                padding: 8px 15px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: rgba(128, 128, 128, 0.1);
            }
        """)
        btn_close.clicked.connect(self.accept)
        
        btn_layout = QVBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        btn_layout.addWidget(btn_close)
        
        layout.addLayout(btn_layout)