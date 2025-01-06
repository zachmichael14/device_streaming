import sys

from PySide6.QtWidgets import QApplication, QStyleFactory

from src.managers.config_manager import ConfigManager
from src.managers.window_manager import WindowManager


# class MainApplicationWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Main Application")
#         self.central_widget = MainWidget()
#         self.setCentralWidget(self.central_widget)

if __name__ == "__main__":
    app = QApplication([])
    QApplication.setStyle(QStyleFactory.create("Fusion"))

    config_manager = ConfigManager()
    window_manager = WindowManager(config_manager)

    config_window = window_manager.create_config_window()
    config_window.show()

    sys.exit(app.exec())