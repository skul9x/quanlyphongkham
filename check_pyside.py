import sys
try:
    from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
    from PySide6.QtCore import Qt

    class VerifyWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("PySide6 Environment Verification")
            self.resize(400, 200)

            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)

            label = QLabel("PySide6 is installed and working correctly.")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("font-size: 16px; color: green; font-weight: bold;")
            layout.addWidget(label)

            info_label = QLabel(f"Python: {sys.version.split()[0]}\nPySide6 Version Installed")
            info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(info_label)

    if __name__ == "__main__":
        app = QApplication(sys.argv)
        window = VerifyWindow()
        window.show()
        print("PySide6 successfully imported. GUI should appear.")
        sys.exit(app.exec())

except ImportError:
    print("Error: PySide6 is not installed.")
    print("Please install it using: pip install PySide6")
except Exception as e:
    print(f"An error occurred: {e}")