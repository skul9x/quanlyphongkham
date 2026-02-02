from PySide6.QtGui import QColor

LIGHT_PALETTE = {
    "bg_main": "#f8fafc",
    "bg_card": "#ffffff",
    "bg_sidebar": "#ffffff",
    "bg_alt": "#f1f5f9",
    "text_primary": "#0f172a",
    "text_secondary": "#64748b",
    "text_inverted": "#ffffff",
    "primary": "#4f46e5",
    "primary_hover": "#4338ca",
    "primary_pressed": "#3730a3",
    "primary_light": "rgba(79, 70, 229, 0.1)",
    "danger": "#ef4444",
    "danger_hover": "#dc2626",
    "danger_light": "#fee2e2",
    "danger_text": "#ef4444",
    "success": "#10b981",
    "success_hover": "#059669",
    "utility_blue": "#3b82f6",
    "utility_blue_light": "rgba(59, 130, 246, 0.1)",
    "border": "#e2e8f0",
    "border_focus": "#6366f1",
    "input_bg": "#ffffff",
    "selection": "#e0e7ff",
    "selection_text": "#312e81",
    "nav_text": "#475569",
    "nav_hover": "#e2e8f0",
    "nav_active": "#e0e7ff",
    "nav_active_text": "#4f46e5",
    "nav_border_active": "#4f46e5"
}

DARK_PALETTE = {
    "bg_main": "#0f172a",
    "bg_card": "#1e293b",
    "bg_sidebar": "#1e293b",
    "bg_alt": "#334155",
    "text_primary": "#f8fafc",
    "text_secondary": "#94a3b8",
    "text_inverted": "#ffffff",
    "primary": "#6366f1",
    "primary_hover": "#818cf8",
    "primary_pressed": "#4f46e5",
    "primary_light": "rgba(99, 102, 241, 0.2)",
    "danger": "#ef4444",
    "danger_hover": "#f87171",
    "danger_light": "#451a1a",
    "danger_text": "#f87171",
    "success": "#10b981",
    "success_hover": "#059669",
    "utility_blue": "#3b82f6",
    "utility_blue_light": "rgba(59, 130, 246, 0.2)",
    "border": "#475569",
    "border_focus": "#818cf8",
    "input_bg": "#0f172a",
    "selection": "#1e1b4b",
    "selection_text": "#c7d2fe",
    "nav_text": "#94a3b8",
    "nav_hover": "#334155",
    "nav_active": "#312e81",
    "nav_active_text": "#e0e7ff",
    "nav_border_active": "#6366f1"
}

def get_palette(theme):
    return DARK_PALETTE if theme == "dark" else LIGHT_PALETTE

def get_stylesheet(theme):
    c = get_palette(theme)
    
    qss = f"""
    * {{
        outline: none;
        font-family: 'Segoe UI', 'Roboto', sans-serif;
        font-size: 14px;
        color: {c['text_primary']};
    }}
    
    QWidget {{
        background-color: {c['bg_main']};
    }}
    
    QMainWindow, QDialog {{
        background-color: {c['bg_main']};
    }}
    
    QToolTip {{
        background-color: {c['bg_card']};
        color: {c['text_primary']};
        border: 1px solid {c['border']};
        border-radius: 4px;
        padding: 4px;
        font-size: 12px;
    }}
    
    /* --- LABELS & HEADERS --- */
    QLabel#DialogTitle, QLabel#CartHeader, QLabel#HeaderTitle {{
        font-size: 20px; 
        font-weight: 800;
        margin-bottom: 5px;
    }}
    
    QLabel#PatientListTitle {{
        font-size: 18px; 
        font-weight: 800;
    }}
    
    QLabel#PatientNameLabel {{
        font-size: 24px; 
        font-weight: 800; 
        border: none;
    }}
    
    QLabel#PatientMetaLabel {{
        font-size: 13px; 
        color: {c['text_secondary']};
        border: none;
    }}
    
    QLabel#AvatarLabel {{
        font-size: 32px; 
        background-color: {c['nav_active']}; 
        border-radius: 32px; 
        border: 1px solid {c['nav_border_active']}; 
        color: {c['text_primary']};
    }}
    
    QLabel#DiagnosisLabel, QLabel#MedicineLabel {{
        background-color: {c['input_bg']}; 
        padding: 10px; 
        border-radius: 6px; 
        border: 1px solid {c['border']};
        font-style: italic;
        color: {c['text_secondary']};
    }}
    
    QLabel#MedicineLabel {{
        font-family: monospace;
    }}

    QLabel#InfoCaptionLabel {{
        font-size: 12px; 
        font-weight: 600; 
        text-transform: uppercase; 
        border: none; 
        color: {c['text_secondary']};
    }}
    
    QLabel#InfoValueLabel {{
        font-size: 15px; 
        font-weight: 500; 
        border: none;
    }}

    QLabel#FormLabel {{
        font-weight: 600;
        background-color: transparent;
    }}

    /* --- GROUPS & FRAMES --- */
    QGroupBox#ActionGroupBox, QGroupBox#InfoGroupBox, QGroupBox#ClinicalGroupBox, QGroupBox#GroupHeader, QGroupBox#FilterGroupBox {{
        background-color: {c['bg_card']};
        border: 1px solid {c['border']};
        border-radius: 12px;
        margin-top: 1.5em;
        padding: 20px;
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 5px;
        left: 15px;
        color: {c['text_secondary']};
        font-weight: 700;
        font-size: 12px;
        text-transform: uppercase;
        background-color: transparent;
    }}

    QGroupBox#DoseResultGroup {{
        background-color: {c['primary_light']}; 
        border: 1px solid {c['primary']}; 
        border-radius: 8px;
        margin-top: 10px; 
    }}
    
    QLabel#DosePerDoseLabel {{
        font-size: 24px; 
        font-weight: 800; 
        color: {c['primary']}; 
        background: transparent;
    }}
    
    QLabel#DoseTotalLabel {{
        color: {c['primary_hover']}; 
        font-weight: 600; 
        background: transparent;
    }}
    
    QWidget#SearchContainer {{
        background-color: {c['input_bg']}; 
        border-radius: 8px; 
        border: 1px solid {c['border']};
    }}
    
    QLabel#SearchIconLabel {{
        border: none; 
        background: transparent; 
        color: {c['text_secondary']};
    }}
    
    QWidget#CartPanel {{
        background-color: {c['bg_card']}; 
        border-radius: 12px; 
        border: 1px solid {c['border']};
    }}
    
    QFrame#SummaryFrame {{
        background-color: {c['bg_alt']}; 
        border: 1px solid {c['border']};
        border-radius: 8px;
    }}

    QLabel#TotalCaptionLabel {{
        font-weight: bold; 
        font-size: 16px; 
        border: none; 
        background: transparent;
    }}
    
    QLabel#TotalValueLabel {{
        font-weight: 900; 
        font-size: 28px; 
        color: {c['success']}; 
        border: none; 
        background: transparent;
    }}
    
    QWidget#SpinBoxContainer {{
        background-color: transparent;
    }}

    /* --- SIDEBAR --- */
    QWidget#PatientListContainer {{
        border-right: 1px solid {c['border']};
    }}
    
    QWidget#Sidebar {{
        background-color: {c['bg_sidebar']};
        border-right: 1px solid {c['border']};
    }}
    
    QLabel#AppLogo {{
        font-size: 18px;
        font-weight: 800;
        color: {c['primary']};
        padding: 20px 10px;
        qproperty-alignment: AlignLeft;
    }}
    
    QPushButton#NavButton {{
        background-color: transparent;
        color: {c['nav_text']};
        border: none;
        border-radius: 8px;
        text-align: left;
        padding: 12px 20px;
        font-weight: 600;
        font-size: 14px;
        margin: 4px 12px;
    }}
    
    QPushButton#NavButton:hover {{
        background-color: {c['nav_hover']};
        color: {c['text_primary']};
    }}
    
    QPushButton#NavButton:checked {{
        background-color: {c['nav_active']};
        color: {c['nav_active_text']};
        border-left: 4px solid {c['nav_border_active']};
        border-top-left-radius: 2px;
        border-bottom-left-radius: 2px;
        font-weight: 700;
    }}
    
    QPushButton#NavButton[collapsed="true"] {{
        text-align: center;
        padding: 12px 0px;
        margin: 4px 8px;
        border-left: none; 
        border: 2px solid transparent; 
    }}
    
    QPushButton#NavButton[collapsed="true"]:checked {{
        background-color: {c['nav_active']};
        color: {c['nav_active_text']};
        border: 2px solid {c['nav_border_active']};
        border-radius: 8px;
    }}
    
    QPushButton#ToggleButton {{
        background-color: {c['bg_alt']}; 
        color: {c['text_primary']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        font-size: 20px;
        font-weight: bold;
        padding: 0px; 
        margin: 0px;
        text-align: center;
    }}
    QPushButton#ToggleButton:hover {{
        color: {c['primary']};
        background-color: {c['nav_hover']};
        border-color: {c['primary']};
    }}
    
    /* --- BUTTONS --- */
    QPushButton {{
        background-color: {c['primary']};
        color: {c['text_inverted']};
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        font-size: 13px;
        /* REMOVED CURSOR POINTER TO FIX CONSOLE SPAM */
    }}
    
    QPushButton:hover {{
        background-color: {c['primary_hover']};
    }}
    
    QPushButton:pressed {{
        background-color: {c['primary_pressed']};
    }}
    
    QPushButton:disabled {{
        background-color: {c['bg_alt']};
        color: {c['text_secondary']};
        border: 1px solid {c['border']};
    }}
    
    QPushButton#PrimaryButton, QPushButton#PrimaryAddButton {{
        background-color: {c['primary']};
        color: {c['text_inverted']};
    }}
    
    QPushButton#PrimaryAddButton {{
        background-color: {c['success']};
        color: {c['text_inverted']};
    }}
    
    QPushButton#PrimaryAddButton:hover {{
        background-color: {c['success_hover']};
    }}
    
    QPushButton#PrimaryUpdateButton {{
        background-color: {c['utility_blue']};
        color: {c['text_inverted']};
    }}
    
    QPushButton#PrimaryUpdateButton:hover {{
        background-color: #3b82f6; 
    }}

    QPushButton#PrimarySaveButton {{
        background-color: {c['success']};
        font-weight: 800; 
        font-size: 16px; 
    }}
    
    QPushButton#PrimarySaveButton:hover {{
        background-color: {c['success_hover']}; 
    }}
    
    QPushButton#SecondaryButton, QPushButton#UtilityButton {{
        background-color: {c['bg_card']};
        color: {c['text_primary']};
        border: 1px solid {c['border']};
        padding: 8px 15px;
        font-weight: 600;
    }}
    
    QPushButton#SecondaryButton:hover, QPushButton#UtilityButton:hover {{
        background-color: {c['nav_hover']};
    }}

    QPushButton#DangerDeleteButton, QPushButton#CartDeleteButton {{
        background-color: {c['danger_light']};
        color: {c['danger_text']};
        border: 1px solid {c['danger']};
        font-weight: 700;
        font-size: 13px;
    }}
    
    QPushButton#DangerDeleteButton:hover, QPushButton#CartDeleteButton:hover {{
        background-color: {c['danger']}; 
        color: white;
        border-color: {c['danger_hover']};
    }}
    
    QPushButton#FilterButtonDay, QPushButton#FilterButtonWeek, QPushButton#FilterButtonMonth, QPushButton#FilterButtonYear, QPushButton#FilterButtonAge, QPushButton#FilterButtonGender, QPushButton#FilterButtonLocation {{
        background-color: {c['bg_card']};
        border: 1px solid {c['border']};
        color: {c['text_primary']};
        border-radius: 6px;
        font-weight: 600;
        padding: 0 15px;
    }}
    
    QPushButton#FilterButtonDay:checked, QPushButton#FilterButtonWeek:checked, QPushButton#FilterButtonMonth:checked, QPushButton#FilterButtonYear:checked, QPushButton#FilterButtonAge:checked, QPushButton#FilterButtonGender:checked, QPushButton#FilterButtonLocation:checked {{
        background-color: {c['primary']};
        color: {c['text_inverted']};
        border-color: {c['primary_pressed']};
    }}

    QPushButton#DetailActionButton {{
        background-color: {c['bg_card']};
        border: 1px solid {c['border']};
        color: {c['text_primary']};
        text-align: left;
        padding-left: 15px;
        border-radius: 8px;
    }}
    
    QPushButton#DetailActionButton:hover {{
        background-color: {c['nav_hover']};
    }}

    /* --- INPUTS --- */
    QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
        background-color: {c['input_bg']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        padding: 10px 12px;
        color: {c['text_primary']};
        selection-background-color: {c['selection']};
        selection-color: {c['selection_text']};
    }}
    
    QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QComboBox:focus {{
        border: 2px solid {c['border_focus']};
        padding: 9px 11px;
    }}
    
    QTextEdit#MonospaceTextEdit {{
        font-family: monospace; 
        color: {c['text_secondary']};
    }}

    QLineEdit#ThemedLineEdit, QComboBox#ThemedComboBox, QSpinBox#ThemedSpinBox {{
        border: 1px solid {c['border']}; 
        border-radius: 6px; 
        padding: 8px; 
        background-color: {c['input_bg']};
        color: {c['text_primary']};
    }}
    
    QLineEdit#ThemedLineEdit:focus, QComboBox#ThemedComboBox:focus, QSpinBox#ThemedSpinBox:focus {{
        border: 2px solid {c['border_focus']}; 
        padding: 7px;
    }}
    
    QLineEdit#BorderlessLineEdit {{
        border: none; 
        font-size: 15px; 
        background: transparent; 
        padding: 0px; 
        color: {c['text_primary']};
    }}

    QSpinBox#CartSpinBox {{
        border: 1px solid {c['border']}; 
        border-radius: 6px; 
        padding: 6px 4px; 
        background-color: {c['input_bg']};
        color: {c['text_primary']};
        font-weight: 600;
        font-size: 13px;
    }}
    
    QSpinBox#CartSpinBox::up-button {{
        subcontrol-origin: border;
        subcontrol-position: top right;
        width: 20px;
        background: {c['bg_alt']};
        border-left: 1px solid {c['border']};
        border-bottom: 1px solid {c['border']};
        border-top-right-radius: 5px; 
    }}
    
    QSpinBox#CartSpinBox::down-button {{
        subcontrol-origin: border;
        subcontrol-position: bottom right;
        width: 20px;
        background: {c['bg_alt']};
        border-left: 1px solid {c['border']};
        border-bottom-right-radius: 5px;
    }}
    
    QSpinBox#CartSpinBox::up-button:hover, QSpinBox#CartSpinBox::down-button:hover {{
        background: {c['nav_hover']};
    }}

    /* --- TABLES & TREES --- */
    QTreeWidget, QTableWidget, QListWidget {{
        background-color: {c['bg_card']};
        border: 1px solid {c['border']};
        border-radius: 12px;
        gridline-color: {c['border']};
    }}
    
    QTreeWidget#MedicineTree, QTreeWidget#CatalogTree, QTreeWidget#HistoryTree {{
        background-color: {c['bg_card']};
        border: 1px solid {c['border']};
        border-radius: 8px; 
        font-size: 14px;
        outline: none;
    }}
    
    QTreeWidget#CartTree {{
        background-color: transparent;
        border: none;
        border-radius: 0px; 
    }}
    
    QHeaderView::section {{
        background-color: {c['bg_main']};
        color: {c['text_secondary']};
        padding: 12px;
        border: none;
        border-bottom: 2px solid {c['border']};
        font-weight: 700;
        text-transform: uppercase;
        font-size: 11px;
    }}
    
    QTreeWidget::item {{
        padding: 10px;
        border-bottom: 1px solid {c['border']};
    }}
    
    QTreeWidget::item:selected {{
        background-color: {c['selection']};
        color: {c['selection_text']};
    }}
    
    QTreeWidget#CartTree::item {{
        min-height: 55px; 
        border-bottom: 1px solid {c['nav_hover']};
        color: {c['text_primary']};
    }}
    
    QTreeWidget#HistoryTree::item {{
        padding: 8px; 
        height: 30px;
        border-bottom: 1px solid {c['nav_hover']};
    }}

    /* --- PATIENT LIST --- */
    QListWidget#PatientList {{
        background-color: transparent;
        outline: none;
        border: none;
    }}
    
    QListWidget#PatientList::item {{
        padding: 12px; 
        border-bottom: 1px solid {c['border']};
        border-radius: 8px;
        margin-bottom: 4px;
        color: {c['text_primary']};
    }}
    
    QListWidget#PatientList::item:selected {{
        background-color: {c['primary']};
        color: {c['text_inverted']};
        border: 1px solid {c['primary_pressed']};
    }}
    
    QListWidget#PatientList::item:hover:!selected {{
        background-color: {c['nav_hover']};
    }}
    
    /* --- SCROLLBAR --- */
    QScrollBar:vertical {{
        background: transparent;
        width: 8px;
        margin: 0px;
    }}
    
    QScrollBar::handle:vertical {{
        background: {c['border']};
        border-radius: 4px;
        min-height: 30px;
    }}
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    
    /* --- MENUS --- */
    QMenu {{
        background-color: {c['bg_card']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        padding: 6px 0;
    }}
    
    QMenu::item {{
        padding: 8px 24px 8px 16px;
        color: {c['text_primary']};
    }}
    
    QMenu::item:selected {{
        background-color: {c['primary']};
        color: {c['text_inverted']};
    }}
    
    QRadioButton#ThemedRadioButton {{
        background-color: transparent;
        color: {c['text_primary']};
    }}
    """
    return qss