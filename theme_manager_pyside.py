from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
import modern_theme

def apply_theme(app, theme_name):
    """
    Applies the selected theme (light/dark) to the QApplication.
    Configures both QPalette (for system-level consistency) and QSS (for custom styling).
    """
    # Set Qt Style Engine to Fusion for consistent cross-platform rendering
    app.setStyle("Fusion")
    
    # Get Colors from modern_theme
    c = modern_theme.get_palette(theme_name)
    
    # Configure Palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(c['bg_main']))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(c['text_primary']))
    palette.setColor(QPalette.ColorRole.Base, QColor(c['bg_card']))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(c['bg_alt']))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(c['text_primary']))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(c['bg_card']))
    palette.setColor(QPalette.ColorRole.Text, QColor(c['text_primary']))
    palette.setColor(QPalette.ColorRole.Button, QColor(c['bg_main']))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(c['text_primary']))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(c['danger']))
    palette.setColor(QPalette.ColorRole.Link, QColor(c['primary']))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(c['primary']))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(c['text_inverted']))
    
    app.setPalette(palette)
    
    # Apply Global QSS from modern_theme
    stylesheet = modern_theme.get_stylesheet(theme_name)
    app.setStyleSheet(stylesheet)
    
    # Update Global Font (Optional, but ensures consistency)
    font = app.font()
    font.setFamily("Segoe UI") # Fallback handled by OS usually
    font.setPointSize(10) # 10pt approx 13-14px
    app.setFont(font)