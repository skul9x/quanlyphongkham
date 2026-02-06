# ClinicManagerv4.1_SourceCode/main_pyside.py
import sys
import os
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QMessageBox, QStatusBar, 
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QButtonGroup, QFrame,
    QProgressDialog
)
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Qt, QSize, QPoint, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QThread, Signal, QObject, QTimer, Slot

import config
import database
import theme_manager_pyside
from animation_helper import AnimationHelper
from ux_components import MarqueeLabel
from sync_manager import sync_manager

from ui_patient_pyside import PatientTab
from ui_medicine_pyside import MedicineTab
from ui_stats_pyside import StatsTab
from ui_help_pyside import HelpTab
from ui_debug_pyside import DebugTab

# --- BACKGROUND COMPONENT: SYNC WORKER ---
# (Defined at the end of file to keep import clean)



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.settings_file = "settings.json"
        self.current_theme = "light"
        self.sidebar_collapsed = False
        
        # 1. Setup Data & UI Skeleton
        self.setup_database()
        self.setup_window()
        self.create_actions()
        self.create_menu()
        
        # 2. Create UI Elements (Sidebar, Stack, etc.)
        # Crucial: This must happen BEFORE loading settings that might trigger resize events
        self.setup_main_layout() 
        self.create_status_bar()
        
        # 3. Load Settings & Restore State
        # Now safe to call showMaximized() or access sidebar_container
        self.load_settings()
        
        # 4. Apply Theme
        self.set_theme(self.current_theme, save=False)

    def setup_window(self):
        self.setWindowTitle(config.APP_TITLE)
        if os.path.exists(config.APP_ICON):
            self.setWindowIcon(QIcon(config.APP_ICON))
        self.setMinimumSize(1280, 800)

    def setup_database(self):
        database.initialize_database()
        # [v5.0] Sync is now handled by Splash Screen Worker


    def create_actions(self):
        self.exit_action = QAction("Thoát", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(self.close)

        self.about_action = QAction("Giới thiệu", self)
        self.about_action.triggered.connect(self.show_about)

    def create_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("Hệ thống")
        file_menu.addAction(self.exit_action)

        help_menu = menu_bar.addMenu("Trợ giúp")
        help_menu.addAction(self.about_action)

    def setup_main_layout(self):
        main_container = QWidget()
        self.setCentralWidget(main_container)
        
        main_layout = QHBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.create_sidebar()
        main_layout.addWidget(self.sidebar_container)
        
        content_wrapper = QWidget()
        content_layout = QVBoxLayout(content_wrapper)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        self.stack = QStackedWidget()
        
        # --- LAZY LOADING: Only create PatientTab at startup ---
        self.patient_tab = PatientTab(self)
        self.stack.addWidget(self.patient_tab)
        
        # Store tab classes for lazy initialization (None = not yet created)
        self._tab_classes = [
            None,           # Index 0: PatientTab (already created)
            MedicineTab,    # Index 1
            StatsTab,       # Index 2
            HelpTab,        # Index 3
            DebugTab,       # Index 4
        ]
        self._tabs = [self.patient_tab, None, None, None, None]
        
        # Add placeholder widgets for deferred tabs
        for _ in range(4):  # 4 placeholders for indices 1-4
            placeholder = QWidget()
            self.stack.addWidget(placeholder)
        
        content_layout.addWidget(self.stack)
        main_layout.addWidget(content_wrapper)

    def create_sidebar(self):
        self.sidebar_container = QWidget()
        self.sidebar_container.setObjectName("Sidebar")
        self.sidebar_container.setFixedWidth(260)
        
        sidebar_layout = QVBoxLayout(self.sidebar_container)
        sidebar_layout.setContentsMargins(0, 15, 0, 20)
        sidebar_layout.setSpacing(8)
        
        # --- Sidebar Header (Toggle + Logo) ---
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(15, 0, 15, 0)
        header_layout.setSpacing(10)
        
        # Toggle Button
        self.btn_toggle = QPushButton("☰")
        self.btn_toggle.setObjectName("ToggleButton")
        self.btn_toggle.setFixedSize(40, 40) 
        self.btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle.clicked.connect(self.toggle_sidebar)
        
        # App Logo
        self.app_logo = MarqueeLabel("CLINIC MANAGER")
        self.app_logo.setObjectName("AppLogo")
        self.app_logo.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.app_logo.setStyleSheet("padding: 0px; border: none; background: transparent; font-weight: bold; font-size: 16px; color: #1e293b;")
        
        header_layout.addWidget(self.btn_toggle)
        header_layout.addWidget(self.app_logo)
        sidebar_layout.addLayout(header_layout)
        
        sidebar_layout.addSpacing(15)
        
        # --- Navigation Buttons ---
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        self.nav_group.buttonClicked.connect(self.on_nav_clicked)
        
        self.add_nav_button("👥  Bệnh nhân", 0, sidebar_layout, tooltip="Quản lý hồ sơ bệnh nhân, lịch sử khám", checked=True)
        self.add_nav_button("💊  Kho thuốc", 1, sidebar_layout, tooltip="Quản lý kho thuốc, nhập xuất tồn")
        self.add_nav_button("📊  Thống kê", 2, sidebar_layout, tooltip="Báo cáo doanh thu, lượt khám")
        self.add_nav_button("⚙️  Cài đặt", 3, sidebar_layout, tooltip="Cấu hình giao diện, thông tin phòng khám")
        self.add_nav_button("🐞  Debug / Log", 4, sidebar_layout, tooltip="Xem log hệ thống, gỡ lỗi")
        
        sidebar_layout.addStretch()
        
        self.version_label = QLabel(f"v{config.APP_VERSION}")
        self.version_label.setStyleSheet("color: #94a3b8; font-size: 12px; padding: 10px; qproperty-alignment: AlignCenter;")
        sidebar_layout.addWidget(self.version_label)

    def add_nav_button(self, text, index, layout, tooltip="", checked=False):
        btn = QPushButton(text)
        btn.setObjectName("NavButton")
        btn.setCheckable(True)
        btn.setChecked(checked)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setToolTip(tooltip)
        
        # Store original text for expanding later
        btn.setProperty("full_text", text)
        btn.setProperty("icon_text", text.split("  ")[0]) 
        
        self.nav_group.addButton(btn, index)
        layout.addWidget(btn)

    def toggle_sidebar(self):
        # Guard against calling before sidebar is created (defensive programming)
        if not hasattr(self, 'sidebar_container'):
            return

        self.sidebar_collapsed = not self.sidebar_collapsed
        
        start_width = self.sidebar_container.width()
        end_width = 70 if self.sidebar_collapsed else 260
        
        self.app_logo.setVisible(not self.sidebar_collapsed)
        self.version_label.setVisible(not self.sidebar_collapsed)
        
        for btn in self.nav_group.buttons():
            if self.sidebar_collapsed:
                icon_only = btn.property("icon_text")
                btn.setText(icon_only)
                btn.setProperty("collapsed", True)
            else:
                full_text = btn.property("full_text")
                btn.setText(full_text)
                btn.setProperty("collapsed", False)
            
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            
        self.anim = QPropertyAnimation(self.sidebar_container, b"minimumWidth")
        self.anim.setDuration(250)
        self.anim.setStartValue(start_width)
        self.anim.setEndValue(end_width)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        self.anim_max = QPropertyAnimation(self.sidebar_container, b"maximumWidth")
        self.anim_max.setDuration(250)
        self.anim_max.setStartValue(start_width)
        self.anim_max.setEndValue(end_width)
        self.anim_max.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.anim_group = QParallelAnimationGroup()
        self.anim_group.addAnimation(self.anim)
        self.anim_group.addAnimation(self.anim_max)
        self.anim_group.start()

    def on_nav_clicked(self, button):
        index = self.nav_group.id(button)
        
        # Lazy load tab if not yet created
        if self._tabs[index] is None and self._tab_classes[index] is not None:
            print(f"[LAZY] Creating tab at index {index}...")
            tab_class = self._tab_classes[index]
            new_tab = tab_class(self)
            self._tabs[index] = new_tab
            
            # Replace placeholder widget with actual tab
            old_widget = self.stack.widget(index)
            self.stack.removeWidget(old_widget)
            old_widget.deleteLater()
            self.stack.insertWidget(index, new_tab)
            
            # Store reference for backwards compatibility
            if index == 1:
                self.medicine_tab = new_tab
            elif index == 2:
                self.stats_tab = new_tab
            elif index == 3:
                self.help_tab = new_tab
            elif index == 4:
                self.debug_tab = new_tab
        
        self.stack.setCurrentIndex(index)

    def create_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Sẵn sàng")

    def show_about(self):
        about_message = (
            f"{config.APP_TITLE}\n"
            f"Phiên bản: {config.APP_VERSION}\n"
            f"© Nguyễn Duy Trường\n\n"
            "✨ ĐIỂM MỚI TRONG V5.0.1:\n"
            "✅ Fix lỗi đồng bộ kê đơn:\n"
            "   Đã sửa lỗi đơn thuốc mới không hiển thị trên App Mobile và Form cũ (Triển khai Double-Write).\n"
            "✅ Tối ưu đóng gói:\n"
            "   Cải thiện độ ổn định của file chạy (.exe) và thư viện đi kèm.\n\n"
            "----------------------------\n"
            "✨ ĐIỂM MỚI TRONG V5.0:\n"
            "✅ Kết nối Cloud System (Supabase):\n"
            "   Dữ liệu được đồng bộ an toàn lên đám mây, đảm bảo an toàn và truy cập mọi lúc.\n"
            "✅ Đồng bộ App Android:\n"
            "   Đã có thể theo dõi danh sách bệnh nhân và doanh thu ngay trên điện thoại thông qua App ClinicViewer.\n"
            "✅ Splash Screen Mới:\n"
            "   Trải nghiệm khởi động mượt mà, chuyên nghiệp với màn hình chờ đồng bộ thông minh.\n\n"
            "Hệ thống quản lý phòng khám hiện đại."
        )
        QMessageBox.information(self, "Giới thiệu", about_message)

    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    self.current_theme = settings.get("theme", "light")
                    self.sidebar_collapsed = settings.get("sidebar_collapsed", False)
                    
                    app_title = settings.get("app_title", config.DEFAULT_APP_TITLE)
                    self.set_app_title(app_title, save=False)
                    
                    if "window_geometry" in settings:
                        geo = settings["window_geometry"]
                        self.resize(QSize(geo["width"], geo["height"]))
                        self.move(QPoint(geo["x"], geo["y"]))
                        # Maximize is handled in main block to force it
        except (json.JSONDecodeError, IOError):
            self.current_theme = "light"

    def save_settings(self):
        settings = {
            "theme": self.current_theme,
            "sidebar_collapsed": self.sidebar_collapsed,
            "app_title": self.app_logo.text(),  
            
            "window_geometry": {
                "width": self.width(),
                "height": self.height(),
                "x": self.x(),
                "y": self.y(),
                "maximized": self.isMaximized()
            }
        }
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=4)
        except IOError as e:
            print(f"Error saving settings: {e}")

    def set_theme(self, theme_name, save=True):
        self.current_theme = theme_name
        theme_manager_pyside.apply_theme(QApplication.instance(), self.current_theme)
        if save:
            self.save_settings()
            self.status_bar.showMessage(f"Chế độ giao diện: {theme_name.capitalize()}", 2000)
            
        if self.sidebar_collapsed:
            for btn in self.nav_group.buttons():
                btn.setProperty("collapsed", True)
                btn.style().unpolish(btn)
                btn.style().polish(btn)

    def set_app_title(self, title, save=True):
        self.app_logo.setText(title)
        if save:
            self.save_settings()


    def showEvent(self, event):
        # Apply initial collapsed state if saved
        # We use a temporary flip logic because toggle_sidebar inverts the state
        if self.sidebar_collapsed:
            self.sidebar_collapsed = False 
            self.toggle_sidebar()
        super().showEvent(event)

    def closeEvent(self, event):
        self.save_settings()
        super().closeEvent(event)

# --- BACKGROUND COMPONENT: SYNC WORKER ---
class SyncWorker(QObject):
    progress_update = Signal(str, int)
    sync_finished = Signal(bool)

    def run_sync(self):
        try:
            # Helper to bridge sync_manager callback to Qt Signal
            def callback_bridge(msg, pct):
                self.progress_update.emit(msg, pct)
            
            # Run sync
            success = sync_manager.startup_sync(callback_bridge)
            self.sync_finished.emit(success)
        except Exception as e:
            print(f"[WORKER ERROR] {e}")
            self.progress_update.emit("Lỗi khởi động!", 0)
            self.sync_finished.emit(False)

class StartupManager(QObject):
    def __init__(self, splash, worker_thread):
        super().__init__()
        self.splash = splash
        self.worker_thread = worker_thread
        self.main_window = None

    @Slot(bool)
    def on_sync_finished(self, success):
        # This runs on the Main Thread because StartupManager is created in Main Thread
        if success:
            self.splash.update_progress("Đồng bộ hoàn tất! Đang mở ứng dụng...", 100)
        else:
            self.splash.update_progress("Đồng bộ thất bại (Offline). Đang mở ứng dụng...", 100)
        
        # Slight delay to let user see 100%
        QTimer.singleShot(500, self.start_main_window)

    def start_main_window(self):
        # Properly stop the worker thread
        self.worker_thread.quit()
        self.worker_thread.wait()
        
        # Init MainWindow (Now guaranteed to be on Main Thread)
        self.main_window = MainWindow()
        self.main_window.showMaximized()
        
        # Close splash
        self.splash.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName(config.APP_TITLE)
    app.setOrganizationName("NguyenDuyTruong")
    
    # [STARTUP] Show Splash Screen
    from ui_splash_screen import SplashScreen
    splash = SplashScreen()
    splash.show()
    
    # [WORKER] Setup Sync Worker
    worker_thread = QThread()
    worker = SyncWorker()
    worker.moveToThread(worker_thread)
    
    # [MANAGER] Setup Startup Manager (Living in Main Thread)
    startup_manager = StartupManager(splash, worker_thread)
    
    # Connect signals
    # 1. Thread start -> Worker run
    worker_thread.started.connect(worker.run_sync)
    # 2. Worker progress -> Splash update
    worker.progress_update.connect(splash.update_progress)
    # 3. Worker finish -> Manager handle (Cross-thread signal)
    worker.sync_finished.connect(startup_manager.on_sync_finished)
    
    # Start process
    worker_thread.start()
    
    sys.exit(app.exec())