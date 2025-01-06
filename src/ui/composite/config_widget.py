from pathlib import Path
from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QLabel,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QVBoxLayout,
    QWidget,
)

from src.utils.message_utils import MessageUtils


class ConfigWidget(QWidget):
    """
    A widget for configuring trial settings.
    Includes subject ID, import/export functionality, sensor map upload, directory selection, and configuration setup.
    """
    signal_save_directory_selected = Signal(Path)
    signal_sensor_map_uploaded = Signal(Path)

    def __init__(self,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(10)

        self.import_export_layout = QHBoxLayout()
        self.import_button = QPushButton("Import", self)
        self.import_button.clicked.connect(self.handle_import)
        self.export_button = QPushButton("Export", self)
        self.export_button.clicked.connect(self.handle_export)
        self.import_export_layout.addWidget(self.import_button)
        self.import_export_layout.addWidget(self.export_button)

        self.main_layout.addLayout(self.import_export_layout)

        self.config_groupbox = QGroupBox("New Configuration", self)
        self.config_layout = QFormLayout(self.config_groupbox)
        self.config_layout.setSpacing(10)  

        self.subject_id_label = QLabel("Subject ID:", self)
        self.subject_id_input = QLineEdit(self)
        self.subject_id_input.editingFinished.connect(lambda subject_id: self.handle_subject_id_edit)
        self.config_layout.addRow(self.subject_id_label, self.subject_id_input)

        self.upload_sensor_map_label = QLabel("No sensor map selected", self)  
        self.upload_sensor_map_button = QPushButton("Upload Sensor Map", self)
        self.upload_sensor_map_button.clicked.connect(self.handle_upload_sensor_map)

        upload_layout = QVBoxLayout()
        upload_layout.addWidget(self.upload_sensor_map_label)
        upload_layout.addWidget(self.upload_sensor_map_button)
        self.config_layout.addRow(upload_layout)

        self.directory_label = QLabel("No save directory selected", self)  
        self.directory_button = QPushButton("Select Save Directory", self)
        self.directory_button.clicked.connect(self.handle_select_directory)

        directory_layout = QVBoxLayout()
        directory_layout.addWidget(self.directory_label)
        directory_layout.addWidget(self.directory_button)
        self.config_layout.addRow(directory_layout)

        self.main_layout.addWidget(self.config_groupbox)

        self.set_config_button = QPushButton("Set Config", self)
        self.set_config_button.clicked.connect(self.handle_set_config)

        self.set_config_button.setStyleSheet("background-color: green; color: white;")
        self.main_layout.addWidget(self.set_config_button)

        self.setLayout(self.main_layout)

    def handle_import(self):
        """
        Placeholder for handling import functionality.
        """
        print("Import button clicked. Placeholder for import functionality.")

    def handle_export(self):
        """
        Placeholder for handling export functionality.
        """
        print("Export button clicked. Placeholder for export functionality.")

    def handle_upload_sensor_map(self):
        """
        Opens a file dialog to select a sensor map file and updates the QLabel with the uploaded file path.
        """
        file_path, _ = QFileDialog.getOpenFileName(self,
                                                   "Select Sensor Map",
                                                   "",
                                                   "CSV Files (*.csv);;All Files (*)")
        if file_path:
            self.upload_sensor_map_label.setText(file_path)
            file_path = Path(file_path)
            self.signal_sensor_map_uploaded.emit(file_path)

    def handle_select_directory(self):
        """
        Opens a dialog to select a directory and updates the QLabel with the selected directory path.
        """
        directory = QFileDialog.getExistingDirectory(self, "Select Save Directory")
        if directory:
            self.directory_label.setText(directory)
            directory = Path(directory)
            self.signal_save_directory_selected.emit(directory)


    def handle_set_config(self):
        """
        Validates input fields and sets configuration if all fields are valid.
        """
        subject_id = self.subject_id_input.text().strip()
        sensor_map = self.upload_sensor_map_label.text().strip()
        save_directory = self.directory_label.text().strip()

        # Validation
        if not subject_id:
            MessageUtils.show_error_message(self,
                                            "Configuration Error",
                                            "Validation Failed",
                                            "Subject ID is required.")
            return
        if sensor_map == "No sensor map selected":
            MessageUtils.show_error_message(self,
                                            "Configuration Error",
                                            "Validation Failed",
                                            "A sensor map must be uploaded.")
            return
        if save_directory == "No save directory selected":
            MessageUtils.show_error_message(self,
                                            "Configuration Error",
                                            "Validation Failed",
                                            "A save directory must be selected.")
            return

        # If all fields are valid, proceed to set the config
        print("Configuration is valid. Proceeding to set configuration.")


