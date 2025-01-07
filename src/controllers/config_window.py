from pathlib import Path
from typing import Dict

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QMainWindow

from src.managers.config_manager import ConfigManager
from src.ui.composite.config_widget import ConfigWidget


class ConfigMainWindow(QMainWindow):
    """
    Main window for session configuration management.

    Signals:
        signal_configuration_complete: Emitted when configuration is complete.
    """

    signal_configuration_complete = Signal()

    def __init__(self, config_manager: ConfigManager) -> None:
        super().__init__()
        self.config_manager = config_manager

        self.config_widget = ConfigWidget()
        self.setCentralWidget(self.config_widget)
        self.setWindowTitle("Session Configuration")

        self._connect_signals()

    def _connect_signals(self) -> None:
        """
        Connects signals from the config widget to the corresponding handlers."""
        self.config_widget.signal_export_config.connect(self._handle_export_config)
        self.config_widget.signal_sensor_map_upload.connect(self._handle_sensor_map_upload)
        self.config_widget.signal_set_config.connect(self._handle_set_config)

    def _handle_export_config(self, config_data: Dict[str, str]) -> None:
        """
        Handles the export configuration signal by updating the config manager.

        Args:
            config_data (Dict[str, str]): Configuration data to export.
        """
        self.config_manager.set_config(config_data)
        self.config_manager.export_config()

    def _handle_sensor_map_upload(self, sensor_map_path: str) -> None:
        """
        Handles the sensor map upload signal.

        Args:
            sensor_map_path (str): The path of the uploaded sensor map.
        """
        print(sensor_map_path)

    def _handle_set_config(self, config_data: Dict[str, str]) -> None:
        """
        Handles the set config signal by updating the config manager and emitting completion signal.

        Args:
            config_data (Dict[str, str]): Configuration data to set.
        """
        self.config_manager.set_config(config_data)
        self.config_manager.export_config()
        self.signal_configuration_complete.emit()
