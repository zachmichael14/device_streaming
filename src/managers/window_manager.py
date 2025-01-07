from typing import Dict

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QMainWindow

from src.managers.config_manager import ConfigManager
from src.controllers.config_window import ConfigMainWindow

class WindowManager(QObject):
    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config_manager = config_manager
        self.windows: Dict[str: QMainWindow] = {}

    def create_config_window(self) -> QMainWindow:
        """
        Create the config window.

        Returns:
            QMainWindow: The configuration window.
        """
        if "config_window" not in self.windows:
            config_window = ConfigMainWindow(self.config_manager)
            self.windows["config_window"] = config_window

        return self.windows["config_window"]


