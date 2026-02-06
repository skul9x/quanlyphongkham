import sys
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel
)
from PySide6.QtCore import Qt, Signal, QObject, Slot
from PySide6.QtGui import QTextCursor, QColor

# --- Log Streamer Helper ---
class LogStream(QObject):
    """Redirects sys.stdout and sys.stderr to a Signal."""
    text_written = Signal(str, bool) # text, is_error

    def __init__(self, original_stream, is_error=False):
        super().__init__()
        self.original_stream = original_stream
        self.is_error = is_error

    def write(self, text):
        # Write to original stream (console) just in case
        if self.original_stream:
            self.original_stream.write(text)
        # Emit signal to UI
        self.text_written.emit(str(text), self.is_error)

    def flush(self):
        if self.original_stream:
            self.original_stream.flush()

class DebugTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_logging()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Header
        header = QHBoxLayout()
        lbl_title = QLabel("System Logs & Debug Console")
        lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #334155;")
        header.addWidget(lbl_title)
        header.addStretch()
        
        btn_clear = QPushButton("Xóa Log")
        btn_clear.setStyleSheet("background-color: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 4px; padding: 5px 10px;")
        btn_clear.clicked.connect(self.clear_log)
        header.addWidget(btn_clear)
        
        layout.addLayout(header)

        # Log Area
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("""
            QTextEdit {
                background-color: #1e293b; 
                color: #f8fafc; 
                font-family: 'Consolas', 'Courier New', monospace; 
                font-size: 13px;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.log_output)

    def setup_logging(self):
        # Redirect stdout and stderr
        self.stdout_stream = LogStream(sys.stdout, is_error=False)
        self.stderr_stream = LogStream(sys.stderr, is_error=True)
        
        self.stdout_stream.text_written.connect(self.append_log)
        self.stderr_stream.text_written.connect(self.append_log)
        
        sys.stdout = self.stdout_stream
        sys.stderr = self.stderr_stream
        
        print("--- DEBUG CONSOLE READY ---")

    @Slot(str, bool)
    def append_log(self, text, is_error):
        if not text: return
        
        # Move cursor to end
        cursor = self.log_output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        # Format based on type
        format_ = cursor.charFormat()
        if is_error:
            format_.setForeground(QColor("#ef4444")) # Red for errors
        else:
            format_.setForeground(QColor("#f8fafc")) # White for logs
            
        cursor.setCharFormat(format_)
        cursor.insertText(text)
        
        # Auto scroll
        self.log_output.setTextCursor(cursor)
        self.log_output.ensureCursorVisible()

    def clear_log(self):
        self.log_output.clear()
        print("--- Logs Cleared ---")