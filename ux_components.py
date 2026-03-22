from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QProgressBar, QSizePolicy, QPushButton
from PySide6.QtCore import Qt, QEvent, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QColor, QPalette

class LoadingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        if parent:
            self.resize(parent.size())
            parent.installEventFilter(self)
            
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setAutoFillBackground(True)
        
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255, 220))
        self.setPalette(palette)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)
        
        self.lbl_text = QLabel("Đang xử lý...")
        self.lbl_text.setStyleSheet("font-weight: bold; font-size: 16px; color: #2563eb; background: transparent;")
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setFixedWidth(250)
        self.progress.setFixedHeight(6)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: none;
                background: #e2e8f0;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background: #2563eb;
                border-radius: 3px;
            }
        """)
        
        layout.addWidget(self.lbl_text, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.progress, 0, Qt.AlignmentFlag.AlignCenter)
        
        # --- SAFETY TIMER ---
        self.safety_timer = QTimer(self)
        self.safety_timer.setSingleShot(True)
        self.safety_timer.setInterval(15000) # 15 seconds safety timeout
        self.safety_timer.timeout.connect(self.on_safety_timeout)
        
        self.hide()
        
    def eventFilter(self, obj, event):
        if obj == self.parent() and event.type() == QEvent.Type.Resize:
            self.resize(event.size())
        return super().eventFilter(obj, event)

    def show_loading(self):
        self.raise_()
        self.show()
        self.safety_timer.start() # Start counting
        
    def hide_loading(self):
        self.safety_timer.stop()
        self.hide()

    def on_safety_timeout(self):
        self.hide()
        print("[OVERLAY] Safety timeout triggered! Forcing hide.")
        # Optionally show a message box here, but for now just unstuck the UI

class EmptyStateWidget(QWidget):
    def __init__(self, text="Không có dữ liệu", icon="📭", parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)
        
        self.lbl_icon = QLabel(icon) 
        self.lbl_icon.setStyleSheet("font-size: 64px; color: #cbd5e1; background: transparent;")
        self.lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_text = QLabel(text)
        self.lbl_text.setStyleSheet("font-size: 16px; color: #64748b; font-weight: 500; background: transparent;")
        self.lbl_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch()
        layout.addWidget(self.lbl_icon)
        layout.addWidget(self.lbl_text)
        layout.addStretch()

class AnimatedButton(QPushButton):
    """
    Standard QPushButton optimized for CSS styling.
    """
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

def set_validation_error(widget, is_error=True):
    if is_error:
        widget.setStyleSheet("border: 1px solid #ef4444; background-color: #fef2f2;")
    else:
        widget.setStyleSheet("")

class MarqueeLabel(QLabel):
    """
    QLabel that auto-scrolls text if it's wider than the label.
    """
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._text = text
        self._offset = 0
        self._scroll_enabled = False
        
        # Timer for scrolling
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._scroll)
        self.timer.setInterval(30) # ~33 FPS
        
        # Pause before restarting scroll
        self.pause_timer = QTimer(self)
        self.pause_timer.setSingleShot(True)
        self.pause_timer.timeout.connect(self._restart_scroll)
        self.pause_duration = 2000 # ms
        
        self.is_paused = False
        
    def setText(self, text):
        self._text = text
        self._offset = 0
        self.update()
        self.check_scroll_needed()

    def text(self):
        return self._text

    def check_scroll_needed(self):
        fm = self.fontMetrics()
        text_width = fm.horizontalAdvance(self._text)
        if text_width > self.width():
            self._scroll_enabled = True
            if not self.timer.isActive() and not self.is_paused:
                self.timer.start()
        else:
            self._scroll_enabled = False
            self.timer.stop()
            self._offset = 0
            self.update()

    def resizeEvent(self, event):
        self.check_scroll_needed()
        super().resizeEvent(event)
        
    def _scroll(self):
        self._offset += 1
        fm = self.fontMetrics()
        text_width = fm.horizontalAdvance(self._text)
        
        # Reset if scrolled past end + some padding
        if self._offset > text_width + 50: 
            self.timer.stop()
            self.is_paused = True
            self.pause_timer.start(self.pause_duration)
            
        self.update()
        
    def _restart_scroll(self):
        self._offset = -self.width() # Start from left edge (scrolling in)
        self.is_paused = False
        self.timer.start()

    def paintEvent(self, event):
        if not self._scroll_enabled:
            super().paintEvent(event) # Default draw
            return
            
        from PySide6.QtGui import QPainter
        painter = QPainter(self)
        
        rect = self.rect()
        painter.setClipRect(rect)
        
        x = -self._offset
        y = (rect.height() + self.fontMetrics().ascent() - self.fontMetrics().descent()) // 2
        
        painter.drawText(x, y, self._text)