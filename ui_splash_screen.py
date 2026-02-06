from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QProgressBar, QFrame, QApplication
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QIcon, QPixmap, QColor, QPainter, QBrush, QLinearGradient
import config

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(600, 360)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Background Frame (Rounded & Dark)
        self.bg_frame = QFrame()
        self.bg_frame.setObjectName("SplashFrame")
        self.bg_frame.setStyleSheet("""
            QFrame#SplashFrame {
                background-color: #0f172a;
                border: 1px solid #334155;
                border-radius: 12px;
            }
        """)
        
        frame_layout = QVBoxLayout(self.bg_frame)
        frame_layout.setContentsMargins(40, 40, 40, 30)
        frame_layout.setSpacing(10)
        
        # 1. Logo (Centered)
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap(config.APP_ICON)
        if not pixmap.isNull():
            self.logo_label.setPixmap(pixmap.scaled(96, 96, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        frame_layout.addWidget(self.logo_label)
        
        frame_layout.addSpacing(10)
        
        # 2. App Title
        title_label = QLabel(config.DEFAULT_APP_TITLE)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            color: #f8fafc;
            font-size: 24px;
            font-weight: 800;
            font-family: 'Segoe UI', sans-serif;
            letter-spacing: 1px;
        """)
        frame_layout.addWidget(title_label)
        
        # 3. Subtitle (Full Name)
        subtitle_label = QLabel(f"PHẦN MỀM QUẢN LÝ PHÒNG KHÁM NHI")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("""
            color: #6366f1;
            font-size: 14px;
            font-weight: 700;
            text-transform: uppercase;
        """)
        frame_layout.addWidget(subtitle_label)

        # 4. Version
        version_label = QLabel(f"Phiên bản {config.APP_VERSION}")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("""
            color: #94a3b8;
            font-size: 13px;
        """)
        frame_layout.addWidget(version_label)
        
        frame_layout.addSpacing(30)
        
        # 5. Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #1e293b;
                border-radius: 3px;
                border: none;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #6366f1, stop:1 #818cf8);
                border-radius: 3px;
            }
        """)
        frame_layout.addWidget(self.progress_bar)
        
        # 6. Status Text
        self.status_label = QLabel("Đang khởi tạo hệ thống...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            color: #94a3b8;
            font-size: 12px;
            font-style: italic;
        """)
        frame_layout.addWidget(self.status_label)
        
        frame_layout.addStretch()
        
        # 7. Copyright
        copyright_label = QLabel("© Nguyễn Duy Trường")
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setStyleSheet("""
            color: #475569;
            font-size: 11px;
        """)
        frame_layout.addWidget(copyright_label)
        
        layout.addWidget(self.bg_frame)
        
        # Drop Shadow Effect
        # Note: Shadow effects can be heavy or tricky on non-standard windows, 
        # but the translucent background and internal border help simulate depth.

    @Slot(str, int)
    def update_progress(self, message, percent):
        self.status_label.setText(message)
        self.progress_bar.setValue(percent)
        QApplication.processEvents() # Ensure UI redraws immediately
